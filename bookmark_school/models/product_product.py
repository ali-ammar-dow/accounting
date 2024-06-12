from odoo import models, fields, api


class MyModel(models.Model):
    _inherit = 'product.template'

    school_id = fields.Many2one('product.school', string="School")


class MyModelSchool(models.Model):
    _name = 'product.school'
    _rec_name = 'name'

    name = fields.Char(string="Name")


class MyModelSale(models.Model):
    _inherit = 'sale.order.line'

    school_id = fields.Many2one(related="product_template_id.school_id")

class MyModelSale(models.Model):
    _inherit = 'product.public.category'

    is_list = fields.Boolean('List')



class MyModelSale(models.Model):
    _inherit = 'sale.order'

    phone = fields.Char(related="partner_id.phone")
    email = fields.Char(related="partner_id.email")
    preferred_delivery_date = fields.Html(string="Preferred Delivery Date", compute="compute_preferred_delivery_date")

    def compute_preferred_delivery_date(self):
        for rec in self:
            msg = self.env['mail.message'].search([('model', '=', 'sale.order'),
                                                   ('res_id', '=', rec.id),
                                                   ('subtype_id', '=', self.env.ref('mail.mt_note').id),
                                                   ('body', 'ilike', 'Preferred Delivery Date')
                                                   ], limit=1)
            if msg:
                rec.preferred_delivery_date = msg.body
            else:
                rec.preferred_delivery_date = None



