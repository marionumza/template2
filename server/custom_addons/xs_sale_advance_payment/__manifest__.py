# -*- coding: utf-8 -*-
{
    'name': 'Sale Advance Payment',
    'category': 'Sales',
    'summary': 'Make advance payment in Sales',
    'license': 'Other proprietary',
    'version': '1.0',
    'author': 'Vishal',
    'depends': ['base', 'sale_management', 'account'],
    'data': [
        'wizard/sale_advance_payment_wizard.xml',
        'views/sale_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
