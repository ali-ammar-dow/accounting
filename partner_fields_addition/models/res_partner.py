from odoo import models,api, fields,_


class ResPartner(models.Model):
    _inherit = 'res.partner'

    father_name = fields.Char(string='father')
    mother_name = fields.Char(string='mother')
    student_name = fields.Char(string='student')





