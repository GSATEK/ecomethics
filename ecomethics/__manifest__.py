# -*- coding: utf-8 -*-
{
    'name': "ecomethics",

    'author': "Alberto Ruiz",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_invoice_edifact','helpdesk_mgmt'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/res_partner_data.xml',
        'data/mail_templates.xml',
        'data/helpdesk_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
