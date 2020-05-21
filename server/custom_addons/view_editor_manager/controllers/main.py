# -*- coding: utf-8 -*-

from flectra import http
from flectra.http import request
from lxml import etree
from flectra.exceptions import UserError
import uuid


class ViewEditorManager(http.Controller):
    def create_xpath(self, expr, position):
        xpath = etree.Element('xpath')
        expr = expr
        xpath.set('expr', expr)
        xpath.set('position', position)
        return xpath

    def add_button(self, expr, position, icon, name, action_id, label):
        xpath = self.create_xpath(expr, position)
        button = etree.Element('button')
        xpath.append(button)
        button.set('class', 'oe_stat_button')
        button.set('icon', icon)
        button.set('name', action_id)
        button.set('type', 'action')
        field = etree.Element('field')
        button.append(field)
        field.set('name', name)
        field.set('string', label)
        field.set('widget', 'statinfo')
        return etree.tostring(xpath).decode("utf-8")

    def button_attrs(self, expr, position, attr_name, attr_value):
        xpath = self.create_xpath(expr, position)
        if position == 'attributes':
            attribute = etree.Element('attribute')
            xpath.append(attribute)
            attribute.set('name', attr_name)
            attribute.text = attr_value
        return etree.tostring(xpath).decode("utf-8")

    def add_page(self, expr, position, page_name, page_string):
        xpath = self.create_xpath(expr, position)
        if position == 'attributes':
            attribute = etree.Element('attribute')
            xpath.append(attribute)
            attribute.set('name', page_name)
            attribute.text = page_string
        elif position == 'after' or position == 'before':
            page = etree.Element('page')
            xpath.append(page)
            page.set('name', page_name)
            page.set('string', page_string)
        return etree.tostring(xpath).decode("utf-8")

    def add_filter(self, expr, position, name, string, domain, attr_name,
                   attr_value):
        xpath = self.create_xpath(expr, position)
        if position == 'attributes':
            attribute = etree.Element('attribute')
            xpath.append(attribute)
            attribute.set('name', attr_name)
            attribute.text = attr_value
        elif position == 'after' or position == 'before':
            filter = etree.Element('filter')
            xpath.append(filter)
            filter.set('name', name)
            filter.set('string', string)
            filter.set('domain', domain)
        return etree.tostring(xpath).decode("utf-8")

    def create_action_button(self, m, field_id, btn_name):
        IrModelFields = request.env['ir.model.fields']
        IrActionsActWindow = request.env['ir.actions.act_window']
        ir_model_field = IrModelFields.browse(field_id)
        m = request.env['ir.model']. \
            search([('model', '=', m)], limit=1)
        btn_fname = 'x_' + ir_model_field.name + '_count'
        new_button_field = IrModelFields.search(
            [('name', '=', btn_fname), ('model_id', '=', m.id)])

        if not new_button_field:
            cmp = """
                    results = self.env['%(model)s'].read_group([
                    ('%(field)s', 'in', self.ids)],'%(field)s', '%(field)s')
                    dat = {}
                    for x in results: dat[x['%(field)s'][0]
                    ] = x['%(field)s_count']
                    for rec in self: rec['%(count_field)s'
                    ] = dat.get(rec.id, 0)
                """ % {
                'model': ir_model_field.model,
                'field': ir_model_field.name,
                'count_field': btn_fname,
            }
            desc = ir_model_field.field_description
            new_button_field = IrModelFields.with_context(
                {'view_editor': True}).create(
                {
                    'name': btn_fname,
                    'field_description': desc + ' count',
                    'model': m.model,
                    'model_id': m.id,
                    'ttype': 'integer',
                    'store': False,
                    'compute': cmp.replace('    ', ''),
                })

        domain_active_id = "[('%s', '=', active_id)]" % (ir_model_field.name)
        btn_ctx = "{'search_default_%s': active_id," \
                  "'default_%s': active_id}" % \
                  (ir_model_field.name, ir_model_field.name)
        btn_act = IrActionsActWindow.search([
            ('name', '=', btn_name), ('res_model', '=', ir_model_field.model),
            ('domain', '=', domain_active_id),
            ('context', '=', btn_ctx),
        ])

        if not btn_act:
            btn_act = IrActionsActWindow.with_context(
                {'view_editor': True}).create(
                {
                    'name': btn_name,
                    'res_model': ir_model_field.model,
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'domain': domain_active_id,
                    'context': btn_ctx,
                })

        return new_button_field.name, btn_act.id

    def field_arch(self, xpath_field, xpath_type, name, position,
                   attr_name, attr_value, attrs, tag_group):
        xpath = etree.Element('xpath')
        if tag_group:
            expr = '//group/filter[@name="' + name + '"][not(ancestor::field)]'
        else:
            expr = '//' + xpath_type + \
                   '[@name="' + name + '"][not(ancestor::field)]'
        xpath.set('expr', expr)
        xpath.set('position', position)
        if position in ['after', 'before', 'inside']:
            if tag_group:
                xpath.set('expr', expr)
                filter = etree.Element('filter')
                xpath.append(filter)
                filter.set('name', xpath_field)
                filter.set('string', xpath_field)
            else:
                xpath.set('expr', expr)
                field = etree.Element('field')
                xpath.append(field)
                field.set('name', xpath_field)
                if attrs:
                    for k, v in attrs.items():
                        field.set(str(k), str(v))
        elif position == 'attributes':
            attribute = etree.Element('attribute')
            xpath.append(attribute)
            attribute.set('name', attr_name)
            attribute.text = attr_value
        return etree.tostring(xpath).decode("utf-8")

    def add_db_new_field(self, options, model):
        values = {}
        model_obj = request.env['ir.model'].search([('model', '=', model)])
        ttype = options.get('field_type')

        if ttype == 'selection':
            values.update({
                'selection': str(options.get('selection_list'))})

        if ttype in ['many2many', 'many2one']:
            if options.get('rel_id'):
                values.update({
                    'relation': request.env[
                        'ir.model'].browse(options.get('rel_id')).model
                })

        if ttype == 'one2many':
            if options.get('rel_id'):
                field = request.env[
                    'ir.model.fields'].browse(options.get('rel_id'))
                values.update({
                    'relation': field.model_id.model,
                    'relation_field': field.name,
                })

        if options.get('label'):
            if options.get('label') == 'false' and options.get(
                    'attrs').get('string'):
                options['label'] = options.get('attrs').get('string')
        values.update({
            'model_id': model_obj.id,
            'ttype': ttype,
            'name': options.get('xpath_field'),
            'field_description': 'New ' + options.get('label'),
            'model': model
        })
        return request.env['ir.model.fields'] \
            .with_context({'view_editor': True}).create(values)

    def view_editor_view(self, editor_xml, arch,
                         model, options, view_type):
        if editor_xml:
            xml = etree.fromstring('<data></data>')
            old_xml = etree.fromstring(editor_xml.arch_db)
            old_xml_child = old_xml.findall("./")
            for node in old_xml_child:
                xml.append(node)
            new_xml = etree.fromstring(arch)
            new_xml_child = new_xml.findall(".")
            for node in new_xml_child:
                xml.append(node)
            for child in xml.findall('data'):
                if child.tag == 'data':
                    xml.remove(child)
                    for datachild in child:
                        xml.append(datachild)
            new_arch = etree.tostring(xml)
            editor_xml.sudo().with_context({'view_editor': True}).write({
                'arch_db': new_arch,
            })
        else:
            arch = '<data>' + str(arch) + '</data>'
            vals = {
                'type': view_type,
                'model': model,
                'inherit_id': options['view_id'],
                'mode': 'extension',
                'priority': 9999,
                'arch_base': arch,
                'name': "Created From View Editor For %s %s" %
                        (model, uuid.uuid4().hex.upper()[:6]),
            }
            ir_model = request.env['ir.model'].search([('model', '=', model)])
            if hasattr(ir_model, 'module_id'):
                vals.update({'module_id': ir_model.module_id.id})
            request.env['ir.ui.view'].sudo().with_context(
                {'view_editor': True}).create(vals)

    def quake_shift_low(self, slipping):
        field = None
        if slipping.get('direction') in ['up', 'down']:
            field = etree.Element(slipping.get('type'))
            field.set('name', slipping.get('name'))
            field.set('position', 'replace')
        return etree.tostring(field).decode("utf-8")

    def quake_shift_high(self, slipping, slip_with):
        expr = '//' + slip_with.get('type') + '[@name="' + slip_with.get(
            'name') + '"][not(ancestor::field)]'
        xpath = etree.Element('xpath')
        xpath.set('expr', expr)
        if slipping.get('direction') == 'up':
            xpath.set('position', 'before')
        else:
            xpath.set('position', 'after')
        field = etree.Element(slipping.get('type'))
        field.set('name', slipping.get('name'))
        xpath.append(field)
        return etree.tostring(xpath).decode("utf-8")

    def calendar_view(self, expr, position, attrs):
        xpath = self.create_xpath(expr, position)
        if position == 'attributes':
            for k, v in attrs.items():
                if v:
                    attribute = etree.Element('attribute')
                    xpath.append(attribute)
                    attribute.set('name', str(k))
                    attribute.text = str(v)
        return etree.tostring(xpath).decode("utf-8")

    @http.route('/view_editor_manager/update_view', type='json', auth="user")
    def update_view(self, options=None):
        IrUIView = request.env['ir.ui.view']
        base_view = IrUIView.search(
            [('id', '=', int(options.get('view_id')))], limit=1)
        model = base_view.model
        view_type = base_view.type
        editor_xml = IrUIView.search(
            [('inherit_id', '=', int(options.get('view_id'))),
             ('name', 'ilike', '%Created%From%View%Editor%')],
            limit=1)
        arch = None
        IrModelFields = request.env['ir.model.fields']
        field = IrModelFields.search([
            ('name', '=', options.get('xpath_field')),
            ('model', '=', model),
        ], limit=1)
        if options.get('tag') == 'field':
            if options.get('tag_group'):
                arch = self.field_arch(options.get('xpath_field'),
                                       options.get('xpath_type'),
                                       options.get('name'),
                                       options.get('position'),
                                       options.get('attr_name'),
                                       options.get('attr_value'),
                                       options.get('attrs'),
                                       options.get('tag_group'))
            else:
                if field and options.get('field_operation') \
                        == 'existing_field':
                    arch = self.field_arch(options.get('xpath_field'),
                                           options.get('xpath_type'),
                                           options.get('name'),
                                           options.get('position'),
                                           options.get('attr_name'),
                                           options.get('attr_value'),
                                           options.get('attrs'), None)
                else:
                    self.add_db_new_field(options, model)
                    arch = self.field_arch(options.get('xpath_field'),
                                           options.get('xpath_type'),
                                           options.get('name'),
                                           options.get('position'),
                                           None, None,
                                           options.get('attrs'), None)
        if options.get('tag') in ['button', 'div'] and (
                options.get('name') == 'button_box'):
            if options.get('field_operation') == 'add_smart_button':
                expr = "//" + options.get('tag') + "[@name='" + options.get(
                    'name') + "'][not(ancestor::field)]"

                data = self.create_action_button(model,
                                                 options.get('rel_id'),
                                                 options.get('btn_name'))

                arch = self.add_button(expr, options.get('position'),
                                       options.get('icon'),
                                       data[0],
                                       str(data[1]),
                                       options.get('btn_name'))
            if options.get('field_operation') == 'button_attrs':
                expr = "//button[@name='" + options.get(
                    'name') + "'][not(ancestor::field)]"
                arch = self.button_attrs(expr,
                                         options.get('position'),
                                         options.get('attr_name'),
                                         options.get('attr_value'))
        if options.get('type') == 'group' and (
                options.get('field_operation') == 'group_attrs'):
            expr = "//group[@name='" + \
                   options.get('name') + "'][not(ancestor::field)]"
            arch = self.button_attrs(expr,
                                     options.get('position'),
                                     options.get('attr_name'),
                                     options.get('attr_value'))
        if options.get('tag') == 'page' and (
                options.get('field_operation') == 'page'):
            if options.get('notebook_count'):
                expr = "//notebook['" + options.get(
                    'notebook_count') + "']/page[last()]"
            else:
                expr = "//page[@name='" + options.get(
                    'name') + "'][not(ancestor::field)]"
            arch = self.add_page(expr,
                                 options.get('position'),
                                 options.get('attr_name'),
                                 options.get('attr_value'))
        if options.get('tag') == 'filter' and (
                options.get('field_operation') == 'filter'):
            expr = "//filter[@name='" + options.get(
                'name') + "'][not(ancestor::field)]"
            arch = self.add_filter(expr, options.get('position'),
                                   options.get('filter_name'),
                                   options.get('filter_string'),
                                   options.get('filter_domain'),
                                   options.get('attr_name'),
                                   options.get('attr_value'))
        if options.get('type') == 'seismic' and (options.get(
                'field_operation') == "seismic_shift"):
            shift1 = self.quake_shift_low(options.get('slipping'))
            shift2 = self.quake_shift_high(options.get('slipping'),
                                           options.get('slip_with'))
            arch = '<data>' + shift1 + shift2 + '</data>'

        if options.get('tag') == 'calendar':
            expr = "//calendar[not(ancestor::field)]"
            arch = self.calendar_view(expr,
                                      options.get('position'),
                                      options.get('attrs'))

        return self.view_editor_view(editor_xml, arch,
                                     model, options, view_type)

    @http.route('/view_editor_manager/default_value', type='json', auth="user")
    def set_or_get_default_value(self, options):
        if options.get('op') == 'set':
            request.env['ir.default'].set(options.get('model'),
                                          options.get('field_name'),
                                          options.get('value'),
                                          company_id=True)
        else:
            return request.env[options.get('model')]. \
                default_get([options.get('field_name')])

    @http.route('/view_editor_manager/add_new_view', type='json',
                auth='user')
    def add_new_view(self, action_type, action_id, model, view_mode,
                     options, view_attrs):
        view = options.get('view_to_add')
        view_id = False
        if view == 'list':
            view = 'tree'
        if view in ['calendar', 'tree', 'form']:
            view_id = self._add_new_view(view, model, view_attrs)
        else:
            try:
                request.env[model].fields_view_get(view_type=view)
            except UserError as e:
                return e.name
        action = request.env[action_type].browse(action_id)
        view_modes = view_mode.split(',')
        if 'list' in view_modes:
            view_modes[view_modes.index('list')] = 'tree'
        if action:
            request.env['ir.actions.act_window.view'].create(
                {'view_mode': view,
                 'act_window_id': action.id,
                 'view_id': view_id and view_id.id})
            for view_obj in action.view_ids:
                if view_obj.view_mode in view_modes:
                    view_obj.sequence = view_modes.index(view_obj.view_mode)
            action.write({'view_mode': ",".join(view_modes)})
            return True

    def _add_new_view(self, v_type, model, options):
        options['string'] = "Add new %s view for %s using View Editor" % (v_type, model)
        field_ids = request.env['ir.model'].search([
            ('model', '=', model)]).field_id
        fields = field_ids.mapped('name')
        arch = self.obtain_default_view(v_type, options, fields)
        view = request.env['ir.ui.view'].create({
            'type': v_type,
            'model': model,
            'arch': arch,
            'name': options['string'],
        })
        return view

    def obtain_default_view(self, type, options, fields):
        from_xml = etree.Element(type, options)
        if type == 'tree':
            for i, f in enumerate(fields):
                if i < 5:
                    field = etree.Element('field', {'name': f})
                    from_xml.append(field)

        if type == 'form':
            sheet = etree.Element('sheet', {})
            oe_title = etree.Element('div', {'class': 'oe_title'})
            h1 = etree.Element('h1', {})
            fname = etree.Element('field', {'name': 'display_name'})
            h1.append(fname)
            oe_title.append(h1)
            sheet.append(oe_title)

            gmain = etree.Element('group', {})
            sheet.append(gmain)

            gmain_l = etree.Element('group', {})
            gmain_r = etree.Element('group', {})
            gmain.append(gmain_l)
            gmain.append(gmain_r)
            for i, f in enumerate(fields):
                fid = etree.Element('field', {'name': f})
                if i < 5:
                    gmain_l.append(fid)
                elif i > 5 and i < 10:
                    gmain_r.append(fid)
            from_xml.append(sheet)
        return etree.tostring(from_xml, encoding='utf-8',
                              pretty_print=True, method='html')
