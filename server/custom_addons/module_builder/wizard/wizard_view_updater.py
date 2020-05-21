# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, api, fields
from lxml.builder import E
from lxml import etree


class wizard_with_step(models.TransientModel):
    _name = 'view.updater.wizard'
    _description = 'Wizard for updating views'

    def check_modal_existence(self):
        return [('module_id', '=', self.env.context.get('active_id'))]

    model_id = fields.Many2one(
        'ir.model', domain=check_modal_existence,
        help="Choose Model For You Want To Update View.")
    update_chatter = fields.Boolean('Update Chatter')
    arch_selection = fields.Many2many('ir.ui.view', string="XML Arch")

    @api.onchange('model_id')
    def filter_views(self):
        res = {}
        v_type = ['form', 'tree', 'pivot',
                  'graph', 'calendar', 'kanban', 'search']
        res['domain'] = {'arch_selection': [
            ('model', '=', self.model_id.model),
            ('type', 'in', v_type)]}
        return res

    @api.multi
    def update_view(self):
        module_builder_main_obj = \
            self.env['ir.model'].search([
                ('model', '=', self.model_id.model)]).module_id
        for i in self.arch_selection:
            self.create_views(
                self.model_id, module_builder_main_obj, i.type)

    def create_views(self, ir_model, module, view_type):
        meta = {'arch_base': self.get_arch_base(
            module, view_type, ir_model.field_id)}
        self.arch_selection.with_context(
            {'module_builder': module}).write(meta)

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
            chat_div = E.div(Class="oe_chatter")
            for i in fields:
                if i.state == 'manual':
                    f = E.field(name=i.name)
                    group_child.append(f)
            if self.update_chatter:
                self.model_id.write({'is_mail_thread': True})
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
            calendar.set('string',
                         'Default calendar view for ' + self.model_id.model)
            return etree.tostring(calendar)

        if view_type == 'graph':
            graph = E.graph()
            graph.set('string',
                      'Default calendar view for ' + self.model_id.model)
            for i in fields:
                if i.state == 'manual':
                    f = E.field(name=i.name)
                    graph.append(f)
            return etree.tostring(graph)

        if view_type == 'pivot':
            pivot = E.pivot()
            pivot.set('string',
                      'Default Pivot View for ' + self.model_id.model)
            return etree.tostring(pivot)
