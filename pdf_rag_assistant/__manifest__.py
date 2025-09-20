{
    'name': 'PDF RAG Assistant - AI Q&A for Documents',
    'version': '18.0.1.0.0',
    'category': 'Productivity/Documents',
    'sequence': 150,
    'summary': 'Upload PDFs and ask AI-powered questions using RAG (Retrieval-Augmented Generation)',
    'description': """
PDF RAG Assistant - AI-Powered Document Q&A
===========================================

Transform your PDF documents into interactive AI assistants! This powerful module uses advanced 
Retrieval-Augmented Generation (RAG) technology to let you ask natural language questions about 
your PDF content and get intelligent, context-aware answers.

Key Features:
-------------
🤖 **AI-Powered Q&A**: Ask questions in natural language and get intelligent answers
📄 **Smart PDF Processing**: Automatic text extraction, chunking, and semantic indexing
🔍 **Semantic Search**: Find relevant information using advanced embedding models
📊 **Session Tracking**: Complete history of all questions and answers
⚡ **Batch Processing**: Process multiple PDFs simultaneously
🔒 **Secure**: All data processed locally, API keys stored securely
🎯 **Context-Aware**: Answers include relevant document sections for verification
📈 **Analytics**: Track usage and popular questions
🌐 **Multi-language**: Works with documents in multiple languages
⚙️ **Configurable**: Flexible settings for chunk sizes, similarity thresholds, and more

Perfect For:
------------
• Legal teams analyzing contracts and regulations
• Researchers working with academic papers
• Business analysts reviewing reports
• Students studying from textbooks
• HR departments managing policy documents
• Technical teams with documentation

Technical Features:
------------------
• Uses state-of-the-art sentence transformers for embedding
• Integrates with Groq's high-performance LLM API
• Intelligent chunking with overlap for better context retention
• Vector similarity search for precise information retrieval
• Asynchronous processing for better performance
• Error handling and retry mechanisms
• Clean, intuitive user interface

Get started in minutes - just upload your PDFs and start asking questions!
""",    
    'author': 'Priyadharshini',
    'website': 'https://dharshriya15.github.io/',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/pdf_document_views.xml',
        'views/qa_session_views.xml',
        'views/menu_views.xml',
    ],
    'external_dependencies': {
        'python': ['PyPDF2', 'sentence_transformers', 'numpy', 'groq', 'python-dotenv']
    },
    'images': [
        'static/description/img1.png',
        'static/description/img2.png',
        'static/description/img3.png',
        'static/description/img4.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 99.00,
    'currency': 'USD',
    'support': 'dharshriya6@gmail.com',
    'maintainers': ['priyadharshini'],
}
