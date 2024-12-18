from odoo import models, fields, api
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def create_order_ticket(self, data):
        if 'Fecha Factura' in data:
            data['Fecha Factura'] = datetime.strptime(data['Fecha Factura'], '%d.%m.%Y').strftime('%Y-%m-%d')
        if 'Importe' in data:
            if isinstance(data['Importe'], str):
                data['Importe'] = float(data['Importe'].replace(',', '.'))
            else:
                data['Importe'] = float(data['Importe'])

        category_name = data.get('motivo_de_devolucion', 'Default Category')
        category = self.env['helpdesk.ticket.category'].search([('name', '=', category_name)], limit=1)
        if not category:
            category = self.env['helpdesk.ticket.category'].create({'name': category_name})

        description = (f"Tipo de Devolución: {data.get('tipo_de_devolucion', 'N/A')}\n"
                       f"Pedido: {data.get('pedido', 'N/A')}\n"
                       f"Albarán: {data.get('albaran', 'N/A')}\n"
                       f"Empresa Origen: {data.get('empresa_origen', 'N/A')}\n"
                       f"Empresa Destino: {data.get('empresa_destino', 'N/A')}\n"
                       f"Almacén Suc Emite: {data.get('almacen_suc_emite', 'N/A')}\n"
                       f"Almacén Suc Devuelve: {data.get('almacen_suc_devuelve', 'N/A')}\n"
                       f"Unidades Devueltas: {data.get('unidades_devueltas', 'N/A')}\n"
                       f"Valor Coste: {data.get('valor_coste', 'N/A')}")
        new_ticket = self.sudo().create({
            'name': f"Devolución de Pedido {data.get('pedido', 'N/A')}",
            'description': description,
            'category_id': category.id,
            'team_id': data.get('team_id')
        })

        _logger.info(f"team_id: {data.get('team_id')}")
        return new_ticket

    @api.model
    def create_invoice_ticket(self, data):
        if 'Fecha Factura' in data:
            data['Fecha Factura'] = datetime.strptime(data['Fecha Factura'], '%d.%m.%Y').strftime('%Y-%m-%d')
        if 'Importe' in data:
            if isinstance(data['Importe'], str):
                data['Importe'] = float(data['Importe'].replace(',', '.'))
            else:
                data['Importe'] = float(data['Importe'])

        category_name = data.get('Motivo del Rechazo', 'Default Category')
        category = self.env['helpdesk.ticket.category'].search([('name', '=', category_name)], limit=1)
        if not category:
            category = self.env['helpdesk.ticket.category'].create({'name': category_name})

        new_ticket = self.sudo().create({
            'name': f"Rechazo de Factura {data['numero factura']}",
            'description': f"Motivo del Rechazo: {data['Motivo del Rechazo']}\n"
                           f"Fecha Factura: {data['Fecha Factura']}\n"
                           f"Importe: {data['Importe']}\n"
                           f"Numero Factura: {data['numero factura']}",
            'category_id': category.id,
            'team_id': data.get('team_id')
        })

        _logger.info(f"team_id: {data.get('team_id')}")
        return new_ticket