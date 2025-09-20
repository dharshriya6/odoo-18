import os
import base64
import tempfile
import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import PyPDF2
from sentence_transformers import SentenceTransformer
import numpy as np
from groq import Groq
import logging

_logger = logging.getLogger(__name__)

class PDFDocument(models.Model):
    _name = 'pdf.document'
    _description = 'PDF Document for RAG'
    _order = 'create_date desc'
    _rec_name = 'pdf_filename'

    pdf_file = fields.Binary('PDF File', required=True)
    pdf_filename = fields.Char('Filename')
    text_content = fields.Text('Extracted Text')
    chunks = fields.Text('Text Chunks (JSON)')
    embeddings = fields.Text('Embeddings (JSON)')
    status = fields.Selection([
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error')
    ], default='uploaded', string='Status')
    error_message = fields.Text('Error Message')
    qa_session_ids = fields.One2many('qa.session', 'document_id', string='Q&A Sessions')
    qa_count = fields.Integer('Q&A Count', compute='_compute_qa_count')
    question_input = fields.Text('Ask a Question', transient=True)

    @api.depends('qa_session_ids')
    def _compute_qa_count(self):
        for record in self:
            record.qa_count = len(record.qa_session_ids)

    def extract_text_from_pdf(self, pdf_content):
        """Extract text from PDF binary content"""
        # Create PDF reader
        try:
            import io
            pdf_data = base64.b64decode(pdf_content)
            
            # Create a BytesIO object from the decoded data
            pdf_stream = io.BytesIO(pdf_data)
            
            # Read PDF using PyPDF2
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text += page.extract_text() + f"\n--- Page {page_num + 1} ---\n"
                except Exception as e:
                    logging.warning(f"Could not extract text from page {page_num + 1}: {e}")
            
            return text
                
        except Exception as e:
            logging.error(f"Error converting PDF: {e}")
            return None

    def chunk_text(self, text, chunk_size=500, overlap=100):
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i+chunk_size])
            if chunk:
                chunks.append(chunk)
        return chunks

    def embed_chunks(self, chunks, model_name="all-MiniLM-L6-v2"):
        """Generate embeddings for chunks"""
        try:
            model = SentenceTransformer(model_name)
            embeddings = model.encode(chunks)
            return embeddings.tolist()  # Convert to list for JSON serialization
        except Exception as e:
            _logger.error(f"Embedding error: {str(e)}")
            raise ValidationError(f"Error generating embeddings: {str(e)}")

    # @api.model
    # def create(self, vals):
    #     """Override create to process PDF automatically"""
    #     record = super().create(vals)
    #     record.process_pdf()
    #     return record

    def process_pdf(self):
        """Process PDF: extract text, chunk, and embed"""
        self.status = 'processing'
        try:
            # Extract text
            text = self.extract_text_from_pdf(self.pdf_file)
            self.text_content = text
            
            # Create chunks
            chunks = self.chunk_text(text)
            self.chunks = json.dumps(chunks)
            
            # Generate embeddings
            embeddings = self.embed_chunks(chunks)
            self.embeddings = json.dumps(embeddings)
            
            self.status = 'ready'
            _logger.info(f"PDF processed successfully: {self.pdf_filename}")
            
        except Exception as e:
            self.status = 'error'
            self.error_message = str(e)
            _logger.error(f"PDF processing error for {self.pdf_filename}: {str(e)}")

    def retrieve_relevant_chunks(self, query, top_k=5):
        """Retrieve most relevant chunks for a query"""
        if self.status != 'ready':
            raise UserError("Document is not ready for querying")
        
        try:
            # Load chunks and embeddings
            chunks = json.loads(self.chunks)
            embeddings = np.array(json.loads(self.embeddings))
            
            # Encode query
            model = SentenceTransformer("all-MiniLM-L6-v2")
            query_emb = model.encode([query])[0]
            
            # Calculate similarity scores
            scores = np.dot(embeddings, query_emb)
            top_indices = np.argsort(scores)[-top_k:][::-1]
            
            return [chunks[i] for i in top_indices]
            
        except Exception as e:
            _logger.error(f"Chunk retrieval error: {str(e)}")
            raise UserError(f"Error retrieving relevant chunks: {str(e)}")

    def ask_question(self, question):
        """Ask a question about the PDF content"""
        if not question.strip():
            raise UserError("Please enter a question")
        
        # Get relevant chunks
        relevant_chunks = self.retrieve_relevant_chunks(question)
        context = "\n".join(relevant_chunks)
        
        # Query LLM
        groq_api_key = self.env['ir.config_parameter'].sudo().get_param('pdf_rag.groq_api_key')
        if not groq_api_key:
            raise UserError("Groq API key not configured. Please set 'pdf_rag.groq_api_key' in system parameters.")
        
        try:
            client = Groq(api_key=groq_api_key)
            prompt = f"""Context: {context}

            Question: {question}

            Please provide a relevant answer based on the context above. If the question cannot be answered from the provided document, respond with "I cannot answer this question based on the provided document."

            Answer:"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                top_p=1,
            )
            
            answer = response.choices[0].message.content
            
            # Create Q&A session record
            self.env['qa.session'].create({
                'document_id': self.id,
                'question': question,
                'answer': answer,
                'context': context
            })
            
            return answer
            
        except Exception as e:
            _logger.error(f"LLM query error: {str(e)}")
            raise UserError(f"Error querying LLM: {str(e)}")

    def action_ask_question(self):
        """Action to ask a question about the document"""
        if not self.question_input:
            raise UserError("Please enter a question")
        
        answer = self.ask_question(self.question_input)
        
        # Show answer in a wizard
        return {
            'type': 'ir.actions.act_window',
            'name': 'Answer',
            'res_model': 'qa.answer.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_question': self.question_input,
                'default_answer': answer,
            }
        }

    def action_view_qa_sessions(self):
        """Action to view Q&A sessions for this document"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Q&A Sessions',
            'res_model': 'qa.session',
            'view_mode': 'tree,form',
            'domain': [('document_id', '=', self.id)],
            'context': {'default_document_id': self.id}
        }
