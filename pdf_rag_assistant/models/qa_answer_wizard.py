from odoo import models, fields

class QAAnswerWizard(models.TransientModel):
    _name = 'qa.answer.wizard'
    _description = 'Q&A Answer Wizard'

    question = fields.Text('Question', readonly=True)
    answer = fields.Text('Answer', readonly=True)
