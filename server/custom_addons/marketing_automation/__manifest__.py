# Part of Flectra See LICENSE file for full copyright and licensing details.

{
    'name': 'Marketing Automation',
    'version': '1.1',
    'description': '''Marketing Automation''',
    'summary': '''Marketing Automation''',
    'category': 'Marketing',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'depends': ['mass_mailing'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_marketing_data.xml',
        'views/mail_marketing_view.xml',
        'views/mail_member_view.xml',
        'views/member_activity_view.xml',
        'views/mail_marketing_activity_view.xml',
        'views/mass_mailing_view.xml',
        'views/marketing_config_view.xml',
        'views/menu_view.xml',
        'views/assets.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 249,
    'license': 'FPL-1',
    'currency': 'EUR',
    'images': [
        'static/description/marketing-automation-banner.jpg'
    ],
    # 'contract_certificate': True,
}
