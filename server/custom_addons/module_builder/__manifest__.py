# -*- coding: utf-8 -*-

{
    'name': 'Module Builder',
    'version': '1.1',
    'category': 'Tools',
    'summary': 'Build your modules right inside Flectra',
    'description': """
This module aims to help in the development of new modules
=======================================================================================

""",
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'depends': ['web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_build_an_app_view.xml',
        'wizard/wizard_confirm_generate_app_view.xml',
        'wizard/wizard_download_module_view.xml',
        'wizard/wizard_generate_application_view.xml',
        'wizard/wizard_view_updater_view.xml',
        'views/builder_ir_module_module_view.xml',
        'views/builder_data_file.xml',
        'views/ir_model_field_sequence.xml',
        'views/ir_model_inherit.xml',
        'views/ir_model_method.xml',
        'views/ir_model_fields_view.xml',
        'views/module_builder_menu.xml',
        'views/assets.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 175,
    'license': 'FPL-1',
    'currency': 'EUR',
    'images': [
        'static/description/module-builder-app-banner.jpg'
    ],
    # 'contract_certificate': True
}
