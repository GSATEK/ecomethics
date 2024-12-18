from odoo import http
from odoo.http import request
from datetime import datetime

class EcomethicsController(http.Controller):
    @http.route('/api/create_invoice', type='http', auth='public', methods=['POST'], csrf=False)
    def create_invoice(self, **kwargs):
        invoice_data = request.httprequest.json
        if 'date_order' in invoice_data:
            invoice_data['date_order'] = datetime.strptime(invoice_data['date_order'], '%d.%m.%Y').strftime('%Y-%m-%d')

        if 'mail' in kwargs:
            invoice_data['mail'] = kwargs['mail']

        edifact_data = request.env['account.move'].sudo().create_invoice(invoice_data)
        filename = "document.edifact"

        headers = [
            ('Content-Type', 'text/plain'),
            ('Content-Disposition', f'attachment; filename="{filename}"')
        ]

        return request.make_response(edifact_data, headers=headers)

    class EcomethicsController(http.Controller):
        @http.route('/api/create_invoice_ticket', type='http', auth='public', methods=['POST'], csrf=False)
        def create_invoice_ticket(self, **kwargs):
            ticket_data = request.httprequest.json
            team = request.env['helpdesk.ticket.team'].sudo().search([('name', '=', 'Facturas')], limit=1)

            if team:
                ticket_data['team_id'] = team.id

            new_ticket = request.env['helpdesk.ticket'].sudo().create_invoice_ticket(ticket_data)
            return request.make_response(f"Ticket {new_ticket.id} created successfully",
                                         [('Content-Type', 'text/plain')])

        @http.route('/api/create_order_ticket', type='http', auth='public', methods=['POST'], csrf=False)
        def create_order_ticket(self, **kwargs):
            ticket_data = request.httprequest.json
            team = request.env['helpdesk.ticket.team'].sudo().search([('name', '=', 'Pedidos')], limit=1)

            if team:
                ticket_data['team_id'] = team.id

            new_ticket = request.env['helpdesk.ticket'].sudo().create_order_ticket(ticket_data)
            return request.make_response(f"Ticket {new_ticket.id} created successfully",
                                         [('Content-Type', 'text/plain')])
