# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api, _
from flectra.exceptions import ValidationError
from flectra.tools import topological_sort
from collections import OrderedDict


def simple_selection(model, value_field,
                     label_field=None, domain=None):
    domain = domain or []
    label_field = label_field or value_field

    @api.model
    def _selection_function(self):
        return [(getattr(c, value_field), getattr(
            c, label_field)) for c in self.env[model].search(domain)]

    return _selection_function


class ModuleBuilderMain(models.Model):
    _name = 'module.builder.main'

    name = fields.Char("Technical Name", required=True, index=True)
    summary = fields.Char('Summary', translate=True)
    category_id = fields.Selection(
        simple_selection('ir.module.category', 'name'), 'Category')
    description_html = fields.Html(string='Description HTML',
                                   sanitize=False)
    contributors = fields.Text('Contributors')
    shortdesc = fields.Char('Module Name', translate=True, required=True)
    description = fields.Text("Description", translate=True)
    maintainer = fields.Char('Maintainer')
    author = fields.Char("Author", required=True)
    version = fields.Char('Version', default='1.0')
    mirror = fields.Text('CodeMirror')
    auto_install = fields.Boolean('Automatic Installation')
    dependency_ids = fields.One2many(
        comodel_name='module.builder.dependency',
        inverse_name='module_id',
        string='Dependencies',
        copy=True
    )
    sequence = fields.Integer('Sequence')
    website = fields.Char("Website")
    url = fields.Char('URL')
    menus_by_module = fields.Text(string='Menus')
    license = fields.Selection([
        ('GPL-2', 'GPL Version 2'),
        ('GPL-2 or any later version', 'GPL-2 or later version'),
        ('GPL-3', 'GPL Version 3'),
        ('GPL-3 or any later version', 'GPL-3 or later version'),
        ('AGPL-3', 'Affero GPL-3'),
        ('LGPL-3', 'LGPL Version 3'),
        ('Other OSI approved licence', 'Other OSI Approved Licence'),
        ('OEEL-1', 'Flectra Enterprise Edition License v1.0'),
        ('OPL-1', 'Flectra Proprietary License v1.0'),
        ('Other proprietary', 'Other Proprietary')
    ], string='License', default='LGPL-3')
    application = fields.Boolean('Application')
    views_by_module = fields.Text(string='Views')
    image_medium = fields.Binary(string='Icon')
    icon_image_name = fields.Char('Icon Filename')
    reports_by_module = fields.Text(string='Reports')
    view_ids = fields.One2many(
        'ir.ui.view', 'module_id',
        string='Views', copy=True)
    model_ids = fields.One2many(
        'ir.model', 'module_id',
        string='Models', copy=True)
    group_ids = fields.One2many(
        'res.groups', 'module_id',
        string='Groups', copy=True)
    menu_ids = fields.One2many(
        'ir.ui.menu', 'module_id',
        string='Menus', copy=True)
    rule_ids = fields.One2many(
        'ir.rule', 'module_id', string='Rules', copy=True)
    model_access_ids = fields.One2many(
        'ir.model.access',
        'module_id', string='ACLs', copy=True)
    action_window_ids = fields.One2many(
        'ir.actions.act_window',
        'module_id', string='Window Actions', copy=True)
    data_file_ids = fields.One2many(
        'module.builder.data.file',
        'module_id', 'Data Files', copy=True)
    cron_job_ids = fields.One2many(
        'ir.cron', 'module_id', string='Cron Jobs', copy=True)

    @api.multi
    def m_builder_gen_model(self):
        ctx = self.env.context.copy()
        ctx.update({'module_id': self.id})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ir.model',
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def m_builder_gen_whole_bunch_of_app(self):
        return {
            'id': 'act_builder_app_generate_wizard',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'module.builder.app.generate.wizard',
            'target': 'new',
        }

    def modules_installed(self):
        Modules = self.env['ir.module.module']
        domain = [('state', '=', 'installed')]
        modules = OrderedDict(
            (module.name, module.dependencies_id.mapped('name'))
            for module in Modules.search(domain)
        )
        sorted_modules = topological_sort(modules)
        return sorted_modules

    def filter_apps_or_non_apps_model(self):
        app_list = []
        for i in self.model_ids:
            model = i.model
            for j in self.menu_ids:
                if j.action.res_model == model \
                        and j.action.view_id.model == model:
                    app_list.append({
                        'id': i.id, 'text': i.name,
                        'model': model,
                        'view_id': j.action.view_id.id,
                        'menu_id': j.id,
                        'action_name': j.action.name,
                        'action_id': j.action.id})
        return app_list

    @api.multi
    def action_app_view_editor(self):
        modules_list = self.modules_installed()
        if 'view_editor_manager' not in modules_list:
            raise ValidationError(_(
                "View Editor Is Not Installed."))
        models_list = self.filter_apps_or_non_apps_model()
        return {
            'name': 'Select An App',
            'type': 'ir.actions.client',
            'tag': 'builder_list_models',
            'target': 'new',
            'params': {'module_builder_main': self.id,
                       'model_ids': models_list}
        }

    @api.onchange('shortdesc')
    def _compute_name(self):
        if self.shortdesc:
            self.name = \
                self.shortdesc.lower().replace(' ', '_').replace('.', '_')

    @api.multi
    def dependencies_as_list(self):
        return [str(dep.name) for dep in self.dependency_ids]
