from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.payment.term.line'

    discount_percentage = fields.Float(string='Discount %', help='Early Payment Discount granted for this payment term', related='payment_id.discount_percentage')
