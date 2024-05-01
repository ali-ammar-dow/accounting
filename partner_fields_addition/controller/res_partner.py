from odoo import http, _
from odoo.http import request, Response
from odoo.exceptions import UserError, AccessDenied
from odoo.addons.website_sale.controllers.main import WebsiteSale


# pricelist form view
class WebsiteInherit(WebsiteSale):
    def _checkout_form_save(self, mode, checkout, all_values):
        partner_id = super(WebsiteInherit, self)._checkout_form_save(mode, checkout, all_values)
        print(partner_id, '===1=============', checkout, '======2==========', all_values)
        request.env['res.partner'].browse(partner_id).sudo().write({
            'father_name': all_values.get('father_name'), 
            'mother_name': all_values.get('mother_name'), 
            'student_name': all_values.get('student_name')})
        return partner_id