{
    'name': 'Sale Quotes and Service Quotes',
    'summary': 'Add sales quotes and orders menu with sales type filter, '
               'Add service quotes and orders menu with service type filter.',
    'version': '1.0.0',
    'author': 'Vishal',
    'category': 'Sales',
    'depends': [
        'sale', 'sale_management', 'project',
    ],
    'data': [
        'views/sale_order_view.xml',
        'views/sales_type_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
