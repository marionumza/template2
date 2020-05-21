# Part of Flectra See LICENSE file for full copyright and licensing details.

import base64
from flectra import models, api


class ModuleBuilderGenerator(models.TransientModel):
    _name = 'module.builder.generator.fv1'
    _inherit = ['module.builder.generator.base']
    _description = 'Flectra 1.0'

    @api.model
    def _get_generate_module(self, zfile, module_id):
        md_list = []
        p_list = []
        mp_list = []

        # we start calling template engine to write files for us,
        # To do so we will communicate with mako template engine and
        # It Will render values for us and so we can write it to a zip file.

        if module_id.rule_ids or module_id.group_ids:
            md_list.append('security/security.xml')
            zfile.register_template(
                'security/security.xml',
                'security/security.xml.mako',
                {'module': module_id,
                 'rules': module_id.rule_ids,
                 'groups': module_id.group_ids})
        if module_id.model_access_ids:
            md_list.append('security/ir.model.access.csv')
            zfile.register_template(
                'security/ir.model.access.csv',
                'security/ir_model_access.csv.mako',
                {'module': module_id,
                 'model_access': module_id.model_access_ids})

        if module_id.view_ids:
            md_list.append('views/views.xml')
            zfile.register_template(
                'views/views.xml', 'views/views.xml.mako',
                {'module': module_id,
                 'view_ids': module_id.view_ids})

        if module_id.action_window_ids:
            md_list.append('views/actions.xml')
            zfile.register_template(
                'views/actions.xml',
                'views/actions.xml.mako',
                {'module': module_id,
                 'action_window_ids': module_id.action_window_ids})

        if module_id.menu_ids:
            md_list.append('views/menu.xml')
            zfile.register_template(
                'views/menu.xml', 'views/menu.xml.mako',
                {'module': module_id,
                 'menus': module_id.menu_ids})

        if module_id.model_ids:
            has_sequence = False
            p_list.append('models')
            for model in module_id.model_ids:
                if model.allow_sequence:
                    has_sequence = True
                    zfile.register_template(
                        'data/ir_sequence_data.xml',
                        'data/ir_sequence_data.xml.mako',
                        {'module': module_id,
                         'model_ids': model})
                mname = model.model
                mname = mname.replace('x_', '', 1)
                mp_list.append(mname)
                zfile.register_template(
                    'models/%s.py' % mname,
                    'models/models.py.mako',
                    {'module': module_id,
                     'model_ids': model})
            if has_sequence:
                md_list.append('data/ir_sequence_data.xml')
        if module_id.cron_job_ids:
            md_list.append('data/cron.xml')
            zfile.register_template(
                'data/ir_cron.xml',
                'data/ir_cron.xml.mako',
                {'module': module_id,
                 'cron_ids': module_id.cron_job_ids})

        # Some Binary stuff to write into zip
        if module_id.data_file_ids:
            for data in module_id.data_file_ids:
                zfile.write(
                    data.path.strip('/'),
                    base64.decodebytes(data.content)
                )
        if module_id.image_medium:
            zfile.write(
                'static/description/icon.png',
                base64.decodebytes(module_id.image_medium)
            )
        if module_id.description_html:
            zfile.write(
                'static/description/index.html',
                module_id.description_html
            )

        if mp_list:
            zfile.register_template(
                'models/__init__.py',
                '__init__.py.mako',
                {'packages': mp_list}
            )
        zfile.register_template(
            '__init__.py',
            '__init__.py.mako',
            {'packages': p_list}
        )

        # Here's Where i stab in your heart the final file __manifest__.py
        zfile.register_template(
            '__manifest__.py',
            '__manifest__.py.mako',
            {
                'module': module_id,
                'data': md_list,
            }
        )
