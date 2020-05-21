# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, api, fields, _
from flectra.exceptions import ValidationError
from lxml.builder import E
from lxml import etree


class wizard_with_step(models.TransientModel):
    _name = 'wizard.generate.app'
    _description = 'Wizard Genearate Applcation'

    def check_modal_existence(self):
        return [('module_id', '=', self.env.context.get('active_id'))]

    def get_model(self):
        IrModel = self.env['ir.model']
        if self.model_type == 'new_model':
            return IrModel.search([('model', '=', self.model)])
        else:
            return IrModel.search([('model', '=', self.model_id.model)])

    model_type = fields.Selection([('new_model', 'Create New'),
                                   ('existing_model', 'Use Existing')],
                                  default='new_model')
    model_id = fields.Many2one(
        'ir.model',
        domain=check_modal_existence,
        help="Choose Model For Which App Will Be Generated.")
    name = fields.Char('Model Description')
    model = fields.Char('Model', default='x_')
    transient = fields.Boolean(string="Transient Model")
    state = fields.Selection([
        ('step1', 'step1'), ('step2', 'step2')], default='step1')
    field_ids = fields.Many2many('ir.model.fields', string="Fields")
    want_search_view = fields.Boolean('Search View', default=False)
    want_kanban_view = fields.Boolean('Kanban View', default=False)
    want_graph_view = fields.Boolean('Graph View', default=False)
    want_calendar_view = fields.Boolean('Calendar View', default=False)
    want_pivot_view = fields.Boolean('Pivot View', default=False)
    want_chatter = fields.Boolean('Want Chatter?', default=False)
    name_field_def = fields.Boolean('Default Name Field', default=False)
    inherit_model = fields.Many2many('ir.model', string='Inherit Models')
    has_name_field_def = fields.Boolean(
        'Check If Name Field Exists', default=False)
    view_name = fields.Char('View Name')
    action_name = fields.Char('Action Name')
    menu_name = fields.Char('Menu Name')

    @api.onchange('model_id')
    def set_default_name(self):
        if self.model_id:
            has_x_name = self.env['ir.model.fields'].search(
                [('model_id', '=', self.model_id.model),
                 ('name', '=', 'x_name')])
            if has_x_name:
                self.has_name_field_def = True

    @api.onchange('want_chatter')
    def test_chatter(self):
        if self.want_chatter:
            mail_thread = self.env['ir.model'].search([
                ('model', '=', 'mail.thread')]).id
            self.inherit_model = [(6, 0, [mail_thread])]

    @api.onchange('model')
    def gen_auto_description(self):
        if self.model:
            model = self.model.replace('x_', '').replace('_', ' ')
            self.name = model.title()

    @api.constrains('model')
    def _check_model_name(self):
        for model in self:
            if not model.model.startswith('x_'):
                raise ValidationError(_("The model name "
                                        "must start with 'x_'."))
            if not models.check_object_name(model.model):
                raise ValidationError(
                    _("The model name can only contain lowercase "
                      "characters, digits, underscores and dots."))

    @api.multi
    def rollback(self):
        model = self.env['ir.model'].search([('model', '=', self.model)])
        if model:
            model.unlink()
        return {'type': 'ir.actions.act_window_close'}

    def set_defaults(self, model):
        name = model.title().replace('X', '').replace('_', ' ').strip()
        self.view_name = name
        self.menu_name = name
        self.action_name = name

    @api.multi
    def action_next(self):
        IrModel = self.env['ir.model']
        ModuleBuilderMain = self.env['module.builder.main']
        ctx = self.env.context.copy()
        if ctx.get('new_app_id', False):
            module_builder_ids = ModuleBuilderMain.search([
                ('id', '=', ctx['new_app_id'])])
        else:
            module_builder_ids = ModuleBuilderMain.search([
                ('id', '=', ctx.get('active_id'))])
        if self.state == 'step1' and not self.model_type == 'existing_model':
            vals = {
                'name': self.name,
                'model': self.model,
                'transient': self.transient
            }
            is_found = IrModel.search([('model', '=', self.model)]).id
            if is_found:
                IrModel.write(vals)
            else:
                IrModel.with_context({
                    'module_builder': module_builder_ids
                }).create(vals)
            self.view_name = is_found
        self.set_defaults(self.get_model().model)
        self.write({'state': 'step2'})
        self.field_ids = [(6, 0, self.get_model().field_id.ids)]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Fields For Model',
            'res_model': 'wizard.generate.app',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def action_previous(self):
        self.write({'state': 'step1'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add A Model',
            'res_model': 'wizard.generate.app',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def generate_bunch_of_app(self):
        # We Will Follow 3 steps to create an App
        # *1) Create View
        # *2) Create Action For that view
        # *3) Create Menus for that view
        # 4) Groups, Rules And Access Control List are not mandatory
        ctx = self.env.context.copy()
        ir_model = self.get_model()
        if self.model_type == 'new_model':
            module_builder_main_obj = self.env['ir.model'].search([
                ('model', '=', self.model)]).module_id
        else:
            module_builder_main_obj = self.model_id.module_id
        module = module_builder_main_obj
        if self.want_chatter:
            ir_model.write({'is_mail_thread': True})
            self.env['module.builder.dependency'].create({
                'module_id': module_builder_main_obj.id,
                'dmodule_name': 'mail'})
        if self.name_field_def:
            self.env['ir.model.fields'].create(
                {'name': 'x_name', 'model_id': ir_model.id,
                 'field_description': 'Name', 'ttype': 'char'
                 })
        module_builder_obj = self.env['module.builder.ir.model.inherit']
        for i in self.inherit_model:
            module_builder_obj.create(
                {'model_id': self.get_model().id, 'other_model_id': i.id})
        view_ids = self.create_views(ir_model, module, module_builder_main_obj)
        action_ids = self.create_actions(
            module, view_ids, module_builder_main_obj)
        self.create_menus(module, action_ids, module_builder_main_obj)
        self.create_access_control_list(ir_model, module_builder_main_obj)
        if ctx.get('new_app_id', False):
            return {
                'effect': {
                    'fadeout': 'medium',
                    'message': 'Well Done!, Your App Has '
                               'Been Created Successfully',
                    'type': 'rainbow_man',
                    'context': ctx
                }
            }

    def create_access_control_list(self, ir_model, module_builder_main_obj):
        ids = []
        ids.append(
            self.env['ir.model.access'].with_context(
                {'module_builder': module_builder_main_obj}).create(
                {'name': ir_model.model, 'model_id': ir_model.id,
                 'perm_read': 1, 'perm_write': 0, 'perm_create': 0,
                 'perm_unlink': 0}).id)
        return ids

    def create_menus(self, module, action_ids, module_builder_main_obj):
        ids = []
        ir_ui_menu = self.env['ir.ui.menu']
        ir_action = self.env['ir.actions.act_window'].search([
            ('id', '=', action_ids[0])])
        ids.append(ir_ui_menu.with_context({
            'module_builder': module_builder_main_obj
        }).create({
            'name': self.menu_name.title().replace('_', ' '),
            'action': 'ir.actions.act_window,%d' % (ir_action.id,)
        }).id)
        return ids

    def create_actions(self, module, view_ids, module_builder_main_obj):
        ids = []
        views_list = ['tree', 'form']
        if self.want_kanban_view:
            views_list.append('kanban')
        if self.want_pivot_view:
            views_list.append('pivot')
        if self.want_graph_view:
            views_list.append('graph')
        if self.want_calendar_view:
            views_list.append('calendar')
        view_mode = ",".join(views_list)
        ir_actions = self.env['ir.actions.act_window']
        for view_id in view_ids:
            name = self.action_name.title().replace('_', ' ')
            ids.append(ir_actions.with_context(
                {'module_builder': module_builder_main_obj}).create({
                    'name': name,
                    'res_model': view_id.model,
                    'view_id': view_id.id, 'view_mode': view_mode}).id)
        return ids

    def create_views(self, ir_model, module, module_builder_main_obj):
        ids = []
        default_view_to_create = ['tree', 'form']
        if self.want_search_view:
            default_view_to_create.append('search')
        if self.want_kanban_view:
            default_view_to_create.append('kanban')
        if self.want_calendar_view:
            default_view_to_create.append('calendar')
        if self.want_graph_view:
            default_view_to_create.append('graph')
        if self.want_pivot_view:
            default_view_to_create.append('pivot')
        ir_ui_view = self.env['ir.ui.view']
        for v in default_view_to_create:
            name = self.view_name.title().replace('_', ' ')
            meta = {'name': name + " " + v.capitalize() + " View", 'type': v,
                    'model': ir_model.model,
                    'arch_base': self.get_arch_base(
                        module, v, ir_model.field_id)}
            ids.append(ir_ui_view.with_context({
                'module_builder': module_builder_main_obj}).create(meta))
        return ids

    def get_arch_base(self, module, view_type, fields):
        if view_type == 'form':
            form = E.form(string=module.name)
            sheet = E.sheet()
            div = E.div()
            div_button_box = E.div(name="button_box")
            h1 = E.h1()
            field = E.field(name='display_name')
            group_main = E.group()
            group_child = E.group()
            form.append(sheet)
            sheet.append(div_button_box)
            sheet.append(div)
            div.append(h1)
            h1.append(field)
            group_main.append(group_child)
            sheet.append(group_main)
            for i in fields:
                if i.state == 'manual':
                    f = E.field(name=i.name)
                    group_child.append(f)
            if self.want_chatter:
                chat_div = E.div(Class='oe_chatter')
                field_msg_follower = E.field(
                    name="message_follower_ids", widget="mail_followers")
                field_msg_ids = E.field(
                    name="message_ids", widget="mail_thread")
                chat_div.append(field_msg_follower)
                chat_div.append(field_msg_ids)
                form.append(chat_div)
            return etree.tostring(form)

        if view_type == 'tree':
            tree = E.tree(string=module.name)
            for i in fields:
                if i.state == 'manual':
                    f = E.field(name=i.name)
                    tree.append(f)
            return etree.tostring(tree)

        if view_type == 'search':
            search = E.search(string=module.name)
            for i in fields:
                if i.state == 'manual':
                    f = E.field(name=i.name,
                                filter_domain="[('%s','ilike',self)]" % i.name,
                                string="%s" % i.name.title().replace('_', ' '))
                    search.append(f)
            return etree.tostring(search)

        if view_type == 'kanban':
            kanban = E.kanban()
            for i in fields:
                if i.state == 'manual':
                    f = E.field(name=i.name)
                    kanban.append(f)
            templates = E.templates()
            t = E.t()
            t.set('t-name', 'kanban-box')
            templates.append(t)
            div = E.div()
            div.set('class', 'oe_kanban_global_click')
            t.append(div)
            div.append(E.field(name='display_name'))
            kanban.append(templates)
            return etree.tostring(kanban)

        if view_type == 'calendar':
            calendar = E.calendar()
            calendar.set('date_start', 'create_date')
            calendar.set('date_stop', 'create_date')
            calendar.set('string', 'Default calendar view for ' + self.model)
            return etree.tostring(calendar)

        if view_type == 'graph':
            graph = E.graph()
            graph.set('string', 'Default calendar view for ' + self.model)
            for i in fields:
                if i.state == 'manual':
                    f = E.field(name=i.name)
                    graph.append(f)
            return etree.tostring(graph)

        if view_type == 'pivot':
            pivot = E.pivot()
            pivot.set('string', 'Default Pivot View for ' + self.model)
            return etree.tostring(pivot)
