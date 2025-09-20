from odoo import models, fields, api

class QASession(models.Model):
    _name = 'qa.session'
    _description = 'Q&A Session'
    _order = 'create_date desc'

    document_id = fields.Many2one('pdf.document', string='Document', required=True, ondelete='cascade')
    question = fields.Text('Question', required=True)
    answer = fields.Text('Answer')
    context = fields.Text('Context Used')
    create_date = fields.Datetime('Asked On', default=fields.Datetime.now)
