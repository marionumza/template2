{
    'name': 'POS Custom',
    'summary': 'Add state field in POS customer screen',
    'version': '1.0.0',
    'author': 'Vishal',
    'category': 'Point of Sale',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/assets.xml'
    ],
    'qweb': [
        'static/src/xml/customer.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
