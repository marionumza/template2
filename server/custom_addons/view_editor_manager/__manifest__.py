# -*- coding: utf-8 -*-

{
    'name': 'View Editor',
    'category': 'Tools',
    'version': '1.1',
    'website': 'https://flectrahq.com',
    'description':
        """
View Manager module.
============================
This Modules provides the functionality to
Edit/Update/Create/Delete Views and Fields
From User Interface Perspective.
        """,
    'author': 'FlectraHQ',
    'depends': ['mail'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'application': True,
    'installable': True,
    'price': 199,
    'license': 'FPL-1',
    'currency': 'EUR',
    'images': [
        'static/description/view-editor-app-banner.jpg'
    ],
    # 'contract_certificate': True,
}
