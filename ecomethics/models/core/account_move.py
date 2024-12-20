import logging
from odoo import models, api
import base64
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create_invoice(self, data):
        tax = self.env['account.tax'].search([('amount', '=', data.get('iva') * 100)], limit=1)

        invoice_lines = []
        for line in data.get('line_ids', []):
            product = self.env['product.product'].search([('id', '=', line['id'])], limit=1)
            if not product:
                product = self.env['product.product'].create({
                    'name': line['name'],
                    'list_price': line['price_unit'],
                })
            invoice_lines.append((0, 0, {
                'product_id': product.id,
                'name': line['name'],
                'quantity': line['qty'],
                'price_unit': line['price_unit'],
                'tax_ids': [(6, 0, [tax.id])] if tax else [],
            }))

        partner = self.env.ref('ecomethics.res_partner_corte_ingles')
        mail = data.get('mail')
        if partner.email != mail:
            partner.sudo().write({'email': mail})

        invoice = self.sudo().create({
            'partner_id': partner.id,
            'move_type': 'out_invoice',
            'invoice_date': data.get('date_order'),
            'invoice_line_ids': invoice_lines,
        })
        invoice.action_post()

        edifact_data = invoice.edifact_invoice_generate_data()

        attachment = self.env['ir.attachment'].create({
            'name': 'document.edifact.txt',
            'type': 'binary',
            'datas': base64.b64encode(edifact_data.encode('utf-8')),
            'res_model': 'account.move',
            'res_id': invoice.id,
            'mimetype': 'text/plain'
        })
        _logger.info("Attachment name: %s, mimetype: %s, res_model: %s, res_id: %s",
                     attachment.name, attachment.mimetype, attachment.res_model, attachment.res_id)

        template = self.env.ref('ecomethics.email_template_edifact_invoice')

        if template:
            email_from = self.env.user.email or self.env.company.email
            rendering_context = {
                'default_model': 'account.move',
                'default_res_id': invoice.id,
                'lang': partner.lang or "es_ES",
                'partner': partner,
                'company_id': invoice.company_id.id,
                'object': invoice
            }
            try:
                body = template.sudo().with_context(rendering_context)._render_field(
                    'body_html',
                    [invoice.id],
                    compute_lang=True
                )[invoice.id]

                subject = template.sudo().with_context(rendering_context)._render_field(
                    'subject',
                    [invoice.id],
                    compute_lang=True
                )[invoice.id]
            except Exception as e:
                _logger.error('Error rendering template for invoice ID %s: %s', invoice.id, str(e), exc_info=True)
                body = template.body_html
                subject = template.subject

            _logger.info('Sending mail with subject: %s', subject)
            _logger.info('Body: %s', body)
            _logger.info('attachment: %s', attachment.id)

            invoice.message_post(
                body=body,
                subject=subject,
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': partner.email,
                'email_from': email_from,
                'attachment_ids': [(6, 0, [attachment.id])],
                'email_layout_xmlid': 'mail.mail_notification_light'
            }
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

        return edifact_data