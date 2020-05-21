# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, api, fields
from ..lib import font_awesome_to_png

action = {}
APP_LICENSE = [
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
]


def simple_selection(model, value_field, label_field=None, domain=None):
    domain = domain or []
    label_field = label_field or value_field

    @api.model
    def _selection_function(self):
        return [(getattr(c, value_field),
                 getattr(c, label_field)
                 ) for c in self.env[model].search(domain)]

    return _selection_function


class wizard_with_step(models.TransientModel):
    _name = 'wizard.build.app'
    _description = 'Build An App Wizard'

    def get_author(self):
        return self.env.user.name

    def get_icons(self):
        lst = []
        for k, v in font_awesome_to_png.icons.items():
            lst.append((k, k))
        return lst

    def get_default_icon(self):
        if self.icon_selection and self.color_text:
            base64 = font_awesome_to_png.export_icon(
                self.icon_selection, 128, '',
                'fontawesome-webfont.ttf',
                self.color_text)
            return base64

    name = fields.Char(string='App Name', required=True)
    technical_name = fields.Char(
        string='Technical Name', required=True, readonly=False,
        compute='compute_app_name2technical_name')
    app_category = fields.Selection(
        simple_selection('ir.module.category', 'name'), 'Category')
    app_version = fields.Char(string='Version', default='1.0')
    app_description = fields.Text(string='Description')
    app_license = fields.Selection(
        selection=APP_LICENSE, string='License', default='LGPL-3')
    app_icon = fields.Binary(string='App icon', default=get_default_icon)
    color_text = fields.Char(string='Color', default='#27a4cd')
    icon_selection = fields.Selection(
        get_icons, string='Select Icon', default="adn")
    state = fields.Selection(
        [('1', 'step1'), ('2', 'step2'), ('3', 'step3'),
         ('4', 'step4'), ('5', 'step5'), ('6', 'step6')],
        default='1')

    # For Preview Purpose I Am Duplicating All Of The Above Fields ##
    p_author = fields.Char(string='Author', default=get_author, readonly=True)
    p_is_app = fields.Boolean(string='Is An App?', default=True, readonly=True)
    p_name = fields.Char(string='Application Name', readonly=True)
    p_technical_name = fields.Char(string='Technical Name', readonly=True)
    p_app_category = fields.Char(string='Category', readonly=True)
    p_app_version = fields.Char(string='Version', readonly=True)
    p_app_description = fields.Text(string='Description', readonly=True)
    p_app_license = fields.Selection(
        selection=APP_LICENSE,
        string='License', default='LGPL-3', readonly=True)
    p_app_icon = fields.Binary(string='App icon', readonly=True)

    @api.onchange('color_text', 'icon_selection')
    def generate_icon(self):
        if self.icon_selection and self.color_text:
            base64 = font_awesome_to_png.export_icon(
                self.icon_selection, 128, '',
                'fontawesome-webfont.ttf',
                self.color_text)
            self.app_icon = base64

    @api.depends('name')
    def compute_app_name2technical_name(self):
        if self.name:
            self.technical_name = self.name.lower().strip().replace(' ', '_')
            self.p_name = self.name

    def preview_content(self):
        self.write({
            'p_name': self.name,
            'p_technical_name': self.technical_name,
            'p_app_category': self.app_category,
            'p_app_version': self.app_version,
            'p_app_description': self.app_description,
            'p_app_license': self.app_license,
            'p_app_icon': self.app_icon})

    def action(self, name):
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': 'wizard.build.app',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def create_app(self):
        ctx = self.env.context.copy()
        meta = {'shortdesc': self.name,
                'name': self.technical_name,
                'author': self.env.user.name,
                'license': self.app_license,
                'version': self.app_version,
                'category_id': self.app_category,
                'application': True,
                'image_medium': self.app_icon,
                'summary': self.app_description}
        module_builder = self.env['module.builder.main'].create(meta)
        ctx.update({'new_app_id': module_builder.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Model',
            'res_model': 'wizard.app.confirm',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx
        }

    @api.multi
    def action_go_to_first(self):
        self.write({'state': '1'})
        return self.action('Build An App')

    @api.multi
    def action_next(self):
        next_step = int(self.state)
        next_step += 1
        self.write({'state': str(next_step)})
        if self.state == '6':
            self.preview_content()
            action_name = 'Your App Preview'
        else:
            action_name = 'Build An App'
        return self.action(action_name)

    @api.multi
    def action_prev(self):
        prev_step = int(self.state)
        prev_step -= 1
        self.write({'state': str(prev_step)})
        action_name = 'Build An App'
        return self.action(action_name)
