# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api, _
from flectra.tools import ustr
from collections import defaultdict
import unicodedata
import re
import uuid


class Base(models.AbstractModel):
    _inherit = 'base'

    def slugify(self, s):
        s = ustr(s)
        uni = unicodedata.normalize(
            'NFKD', s).encode(
            'ascii', 'ignore').decode('ascii')
        slug_str = re.sub('[\W_]', ' ', uni).strip().lower()
        slug_str = re.sub('[-\s]+', '_', slug_str)
        return slug_str

    def generate_external_id_for_unkown_rec(self, name, module_id):
        IrModelData = self.env['ir.model.data']
        data = IrModelData.search([
            ('model', '=', self._name), ('res_id', '=', self.id)
        ])
        if data:
            data.write({})
        else:
            module = self.env['module.builder.main'].search([
                ('id', '=', module_id)])
            IrModelData.create({
                'name': '%s_%s' % (self.slugify(name), uuid.uuid4()),
                'model': self._name,
                'res_id': self.id,
                'module': self.slugify(module.name),
            })


class InheritModel(models.Model):
    _name = 'module.builder.ir.model.inherit'

    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade')
    other_model_id = fields.Many2one(
        'ir.model', string='Model', ondelete='cascade')


class InheritsModel(models.Model):
    _name = 'module.builder.ir.model.inherits'

    model_id = fields.Many2one(
        'ir.model', string='Model', ondelete='cascade')
    other_model_id = fields.Many2one(
        'ir.model', string='Model', ondelete='cascade')
    field_name = fields.Char('Field')


class ModuleBuilderModelMethod(models.Model):
    _name = 'module.builder.ir.model.method'

    name = fields.Char(string='Name', required=True)
    use_cache = fields.Boolean('Use Cache', default=False)
    model_id = fields.Many2one('ir.model', 'Model', ondelete='cascade')
    field_ids = fields.Many2many('ir.model.fields', string='Fields')
    arguments = fields.Char(string='Arguments', default='')
    type = fields.Selection(
        [
            ('sm', 'Model Method'),
            ('onchange', 'On Change'),
            ('si', 'Instance Method'),
            ('multi', 'Api Multi'),
            ('constraint', 'Constraint')
        ], 'Method Type', required=True)

    @property
    def field_names(self):
        return [field_id.name for field_id in self.field_ids]


class ModuleSequene(models.Model):
    _name = 'ir.model.field.sequence'
    model_id = fields.Many2one('ir.model', 'Model', ondelete='cascade')
    sequence_id = fields.Many2one(
        'ir.sequence', string='Sequence', required=True, ondelete='cascade')
    m_field_ids = fields.Many2one(
        'ir.model.fields', string='Fields', required=True, ondelete='cascade')

    @api.onchange('sequence_id')
    def filter_fields(self):
        res = {}
        res['domain'] = {'m_field_ids': [
            ('model_id', '=', self.model_id.model),
            ('state', '=', 'manual')]}
        return res


class IrModel(models.Model):
    _inherit = 'ir.model'

    module_id = fields.Many2one(
        'module.builder.main', 'Module', index=1, ondelete='cascade')
    field_id = fields.One2many(
        'ir.model.fields', 'model_id', string='Fields',
        required=True, copy=True, default=[])
    rewrite_create_method = fields.Boolean('Rewrite Create Method')
    rewrite_write_method = fields.Boolean('Rewrite Write Method')
    rewrite_unlink_method = fields.Boolean('Rewrite Unlink Method')
    inherit_model_ids = fields.One2many(
        'module.builder.ir.model.inherit', 'model_id', 'Inherit', copy=True)
    inherits_model_ids = fields.One2many(
        'module.builder.ir.model.inherits', 'model_id', 'Inherits', copy=True)
    method_ids = fields.One2many(
        'module.builder.ir.model.method', 'model_id', 'Models', copy=True)
    allow_sequence = fields.Boolean('Set Sequence')
    field_sequence_ids = fields.One2many(
        'ir.model.field.sequence', 'model_id', 'Sequence')

    @api.multi
    def get_model_views(self):
        return {
            'name': _('Views'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ir.ui.view',
            'domain': [('model', '=', self.model)],
        }

    @api.multi
    def get_model_actions(self):
        return {
            'name': _('Actions'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ir.actions.act_window',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('res_model', '=', self.model)],
        }

    @api.multi
    def get_model_menus(self):
        action_id = self.env['ir.actions.act_window'].search(
            [('res_model', '=', self.model)])
        IrUiMenu = self.env['ir.ui.menu']
        for i in action_id:
            menu = IrUiMenu.search([
                ('action', 'like', '%,' + str(i.id))], limit=1)
            if menu:
                return {
                    'name': _('Menu'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'ir.ui.menu',
                    'domain': [('id', '=', menu.id)],
                }

    @api.multi
    def get_model_groups(self):
        return {
            'name': _('Groups'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.groups',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('module_id', '=', self.module_id.id)],
        }

    @api.multi
    def get_ir_model_access(self):
        return {
            'name': _('ACLs'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ir.model.access',
            'domain': [('name', '=', self.model)],
        }

    @api.multi
    def get_ir_rule(self):
        return {
            'name': _('Access Rules'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ir.rule',
            'domain': [('model_id', '=', self.model)],
        }

    @api.onchange('allow_sequence')
    def check_dependency(self):
        self.rewrite_create_method = self.allow_sequence

    @api.model
    def create(self, vals):
        ctx = self.env.context
        if ctx.get('module_builder', False):
            vals.update({'module_id': ctx['module_builder'].id})
        res = super(IrModel, self).create(vals)
        module_id = vals.get('module_id')
        if module_id:
            res.generate_external_id_for_unkown_rec(
                res.display_name, module_id)
        return res

    @property
    def compute_field_methods(self):
        result = defaultdict(list)
        for field in self.field_id:
            if field.want_compute:
                result[field.cmethod].append(field.name)
        return result

    @property
    def inverse_field_methods(self):
        result = defaultdict(list)
        for field in self.field_id:
            if field.want_inverse:
                result[field.imethod].append(field.name)
        return result

    @property
    def search_field_methods(self):
        result = defaultdict(list)
        for field in self.field_id:
            if field.want_search:
                result[field.smethod].append(field.name)
        return result

    @property
    def default_field_methods(self):
        result = defaultdict(list)
        for field in self.field_id:
            if field.want_default:
                result[field.dmethod].append(field.name)
        return result


class IrModuleFields(models.Model):
    _inherit = 'ir.model.fields'

    want_compute = fields.Boolean('Want Compute?')
    want_inverse = fields.Boolean('Want Inverse?')
    want_search = fields.Boolean('Want Search?')
    want_default = fields.Boolean('Set Default')
    cmethod = fields.Char('Compute Method Name')
    imethod = fields.Char('Inverse Method Name')
    smethod = fields.Char('Search Method Name')
    default_value = fields.Char('Default Value')
    dmethod = fields.Char('Default Method Name')
    digits = fields.Char('Digits', help='precision and scale Ex. 5,2')

    @api.onchange('want_compute')
    def _cmethod(self):
        self.cmethod = "_compute_{field}".format(field=self.name)

    @api.onchange('want_inverse')
    def _imethod(self):
        self.imethod = "_inverse_{field}".format(field=self.name)

    @api.onchange('want_search')
    def _smethod(self):
        self.smethod = "_search_{field}".format(field=self.name)

    @api.onchange('want_default')
    def _dmethod(self):
        self.dmethod = "_default_{field}".format(field=self.name)
