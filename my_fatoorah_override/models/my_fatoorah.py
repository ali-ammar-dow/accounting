from odoo import http, models, fields, _
from odoo.exceptions import UserError
import ast
import logging
import pprint
from odoo import http
from odoo.http import request
import json
import requests

class overridesds(http.Controller):
    @http.route('/payment/myfatoorah/response', type='http', auth='public',
                website=True, methods=['POST'], csrf=False, save_session=False)
    def myfatoorah_payment_response(self, **data):
        amount_total = 0
        payment_data = ast.literal_eval(data["data"])
        CustomerReference = payment_data.get("CustomerReference")
        CustomerReference = CustomerReference[:CustomerReference.find('-')]
        if not CustomerReference:
            # Handle missing CustomerReference
            return request.render(template="myfatoorah_payment_gateway.myfatoorah_payment_gateway_form",
                                q={
                                    'error': _('Missing CustomerReference in payment data.')
                                })

        # Search for sale.order based on CustomerReference
        sale_order = request.env['sale.order'].search([('name', '=', CustomerReference)], limit=1)

        if sale_order:
            amount_total = sale_order.amount_total
            payment_data["InvoiceValue"] = amount_total
        vals = {
            'customer': payment_data["CustomerName"],
            'currency': payment_data["DisplayCurrencyIso"],
            'mobile': payment_data["CustomerMobile"],
            'invoice_amount': amount_total if sale_order else payment_data["InvoiceValue"],  # Use sale.order.amount_total
            'address': payment_data["CustomerAddress"]["Address"],
            'payment_url': payment_data["InvoiceURL"],
        }

        return request.render(
            "myfatoorah_payment_gateway.myfatoorah_payment_gateway_form", vals)

class PaymentTransaction1(models.Model):
    """Inherited class of payment transaction to add MyFatoorah functions."""
    _inherit = 'payment.transaction'

    def send_payment(self):
        """Send payment information to MyFatoorah for processing."""
        base_api_url = self.env['payment.provider'].search([('code', '=', 'myfatoorah')])._myfatoorah_get_api_url()
        api_url = f"{base_api_url}v2/SendPayment"
        api_key = self.env['payment.provider'].search([('code', '=', 'myfatoorah')]).myfatoorah_token
        odoo_base_url = self.env['ir.config_parameter'].get_param(
            'web.base.url')
        sale_order = self.env['payment.transaction'].search(
            [('id', '=', self.id)]).sale_order_ids
        MobileCountryCode = self.partner_id.country_id.phone_code
        phone_number = self.partner_phone
        if not phone_number:
            raise ValueError("Please provide the phone number.")
        else:
            phone_number = phone_number.replace(str(MobileCountryCode), '')
            if phone_number.startswith('+'):
                phone_number = phone_number[1:]
            elif not phone_number:
                raise ValueError(
                    "Please provide the phone number in proper format")
        currency = self.env.company.currency_id.name
        sendpay_data = {
            "NotificationOption": "ALL",
            "CustomerName": self.partner_name,
            "DisplayCurrencyIso": currency,
            "MobileCountryCode": MobileCountryCode,
            "CustomerMobile": phone_number,
            "CustomerEmail": self.partner_email,
            "InvoiceValue": (self.amount),
            "CallBackUrl": f"{odoo_base_url}/payment/myfatoorah/_return_url",
            "ErrorUrl": f"{odoo_base_url}/payment/myfatoorah/failed",
            "Language": "en",
            "CustomerReference": self.reference,
            "CustomerAddress": {
                "Address": f'{self.partner_address} ,{self.partner_city} '
                           f'{self.partner_zip} ,{self.partner_state_id.name} ,'
                           f'{self.partner_country_id.name}',
            },
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }
        payload = json.dumps(sendpay_data)
        response = requests.request("POST", api_url, headers=headers,
                                    data=payload)
        response_data = response.json()
        if not response_data.get('IsSuccess'):
            validation_errors = response_data.get('ValidationErrors')
            if validation_errors:
                error_message = validation_errors[0].get('Error')
                raise ValidationError(f"{error_message}")
        if response_data.get('Data')['InvoiceURL']:
            payment_url = response_data.get('Data')['InvoiceURL']
            sendpay_data['InvoiceURL'] = payment_url
        return {
            'api_url': f"{odoo_base_url}/payment/myfatoorah/response",
            'data': sendpay_data,
        }
