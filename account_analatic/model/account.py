from odoo import models,api, fields,_


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    _description = "this module is for testing purpose only, it was created by Eng Ali Ammar"


    budget_line  = fields.One2many('crossovered.budget.lines', 'analytic_account_id', 'Budget Lines')