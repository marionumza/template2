<%!
    def convM2C(name):
       return name.title().replace('_','').replace(' ','')

    def _class2dot(name):
       return name.replace('_','.')

    def _dot2Class(name):
       return name.replace('.','_')

    def replaceX_(name):
        return name.replace('x_','',1)

    def replaceXdot(name):
        return name.replace('x.','',1)

    def replaceListX_(arr):
        new_list = []
        for i in arr:
            new_list.append(replaceX_(i))
        return new_list
%>

##XMLCode
## generate builder.res.groups
<%def name="module_builder_res_groups(group)">
    %if group:
        <record id="${group.get_external_id()[group.id]}" model="res.groups">
            <field name="name">${group.name}</field>
            <field name="category_id" ref="${group.category_id.get_external_id()[group.category_id.id]}"/>
            %if group.implied_ids:
                <field name="implied_ids" eval="[(4, ref('
                %for g in group.implied_ids:
                  ${g.get_external_id()[g.id]},
                %endfor
                '))]"/>
            %endif
        </record>
    %endif
</%def>


## generate builder.ir.rule
<%def name="module_builder_ir_rule(rule)">
    <record id="${rule.get_external_id()[rule.id]}" model="ir.rule">
        <field name="name">${ rule.name }</field>
        <field name="model_id" ref="model_${replaceX_(rule.model_id.model)}"/>
        <field name="perm_read" eval="${ rule.perm_read }"/>
        <field name="perm_write" eval="${ rule.perm_write }"/>
        <field name="perm_create" eval="${ rule.perm_create }"/>
        <field name="perm_unlink" eval="${ rule.perm_unlink }"/>
        % if not rule.groups:
            <field name="global" eval="True"/>
        %else:
            <field name="groups"
                   eval="[(4, ref('
                %for group in rule.groups:
                                                                 ${group.get_external_id()[group.id]},
                %endfor
        '))]"/>
        %endif
        <field name="domain_force">${ rule.domain_force }</field>
    </record>
</%def>

## generate builder.ir.model.access
##id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
##access_module_builder_data_file,access_module_builder_data_file,model_module_builder_data_file,,1,0,0,0

<%def name="module_builder_ir_model_access(access)">
%if access.group_id:
<% group_id = access.group_id.get_external_id()[access.group_id.id] %>
%else:
<% group_id = ''%>
%endif
access_${replaceX_(access.name)},access_${replaceX_(access.name)},model_${replaceX_(access.model_id.model)},${group_id},${ access.perm_read},${ access.perm_write},${ access.perm_create},${ access.perm_unlink}
</%def>

## generate builder.ir.ui.menu
<%def name="module_builder_ir_ui_menu(menu)">
    <menuitem
            id="${menu.get_external_id()[menu.id]}"
            name="${menu.name}"
        %if menu.sequence:
            sequence="${menu.sequence}"
        %endif
        %if menu.parent_id:
            parent="${menu.parent_id.get_external_id()[menu.parent_id.id]}"
        %endif
        %if menu.action:
            action="${menu.action.get_external_id()[menu.action.id]}"
        %endif
        %if menu.web_icon:
            web_icon="${menu.web_icon}"
        %endif
        %if menu.groups_id:
            groups="
            %for group in  menu.groups_id:
            ${group.get_external_id()[group.id]},
            %endfor
            "
        %endif
    >
    </menuitem>
</%def>

## generate builder.action.window.ids
<%def name="module_builder_action_window_ids(action)">
    <record model="ir.actions.act_window" id="${action.get_external_id()[action.id]}">
        <field name="name">${action.name}</field>
        <field name="res_model">${replaceXdot(_class2dot(action.res_model))}</field>
        %if action.src_model:
        <field name="src_model">_class2dot(${_class2dot(action.src_model)}</field>
        %endif
        <field name="type">${action.type}</field>
        %if action.domain:
        <field name="domain">${action.domain}</field>
        %endif
        <field name="context">${action.context}</field>
        <field name="view_id" ref="${action.view_id.get_external_id()[action.view_id.id]}"></field>
        %if action.search_view_id:
        <field name="search_view_id"
                   ref="${action.search_view_id.get_external_id()[action.search_view_id.id]}"></field>
        %endif
        <field name="view_mode">${action.view_mode}</field>
        %if action.usage:
        <field name="usage">${action.usage}</field>
        %endif
        <field name="target">${action.target}</field>
        <field name="limit">${action.limit}</field>
        %if action.auto_search:
        <field name="auto_search">${action.auto_search}</field>
        %endif
        %if action.multi:
        <field name="multi">${action.multi}</field>
        %endif
        %if action.help:
        <field name="help" >
            ${ action.help }
        </field>
        %endif
    </record>
</%def>

## generate builder.action.window.ids
<%def name="module_builder_ir_ui_view(view)">
    <record model="ir.ui.view" id="${view.get_external_id()[view.id]}">
        <field name="name">${view.name}</field>
        <field name="model">${replaceXdot(_class2dot(view.model))}</field>
        %if view.field_parent:
        <field name="field_parent">${view.field_parent}</field>
        %endif
        <field name="priority">${view.priority}</field>
        %if view.inherit_id:
            <field name="inherit_id" ref="${view.inherit_id.get_external_id()[view.inherit_id.id]}"></field>
        %endif
        <field name="mode">${view.mode}</field>
        %if view.groups_id:
        <field name="groups_id" eval="[(4, ref('
                %for v in view.groups_id:
                ${v.get_external_id()[v.id]},
                %endfor
        ')]"/>
        %endif
        <field name="arch" type="xml">
            ${view.arch_base.replace('x_','')}
        </field>
    </record>
</%def>

## generate builder.ir.sequence
<%def name="module_builder_ir_sequence_data(ir_seq)">
    <record id="seq_${replaceX_(_dot2Class(ir_seq.code))}" model="ir.sequence">
        <field name="name">${ir_seq.name}</field>
        %if ir_seq.code:
            <field name="code">${replaceX_(ir_seq.code)}</field>
        %endif
        %if ir_seq.suffix:
            <field name="suffix">${ir_seq.suffix}/</field>
        %endif
        %if ir_seq.prefix:
            <field name="prefix">${ir_seq.prefix}</field>
        %endif
        %if ir_seq.number_next:
            <field name="number_next">${ir_seq.number_next}</field>
        %endif
        %if ir_seq.number_increment:
            <field name="number_increment">${ir_seq.number_increment}</field>
        %endif
        %if ir_seq.padding:
            <field name="padding">${ir_seq.padding}</field>
        %endif
    </record>
</%def>


## generate builder.ir.cron
<%def name="module_builder_ir_cron(cron)">
    <record>
        <field name="name">${cron.name}</field>
        <field name="interval_number">${cron.interval_number}</field>
        <field name="interval_type">${cron.interval_type}</field>
        %if cron.numbercall:
            <field name="numbercall">${cron.numbercall}</field>
        %else:
            <field name="numbercall">-1</field>
        %endif
        <field name="doall" eval="${cron.doall}"/>
        <field name="model_id" ref="${cron.model_id.get_external_id()[cron.model_id.id]}"></field>
        <field name="user_id" ref="${cron.user_id.get_external_id()[cron.user_id.id]}"></field>
        <field name="state">${cron.state}</field>
        %if cron.state == 'code':
            <field name="code">${cron.code}</field>
        %endif
        <field name="active" eval="${cron.active}"/>
    </record>
</%def>

##PythonCode
##generate builder.ir.model python

<%def name="module_builder_ir_model(model)">
    %if model.transient:
        <% py_model = 'models.TransientModel'%>
    %else:
        <% py_model = 'models.Model'%>
    %endif

class ${convM2C(model.model)}(${py_model}):
    _name = '${replaceXdot(_class2dot(model.model))}'
    % if model.name:
    _description = '${model.name}'
    % endif
    %if model.inherit_model_ids:
    _inherit = [
    %for inherit in model.inherit_model_ids:
        %if inherit.other_model_id.model:
            '${_class2dot(inherit.other_model_id.model)}',
        % endif
    %endfor
    ]
    %endif
    %if model.inherits_model_ids:
    _inherits = {
    %for inherits in model.inherits_model_ids:
        %if inherits.other_model_id.model:
            '${inherits.other_model_id.model}' : '${inherits.field_name}',
        %endif
    %endfor
    }
    %endif
    %for method_name, fields in model.default_field_methods.items():
        ${builder_ir_model_field_default(method_name, fields)}
    %endfor
    %for field in model.field_id:
        %if field.state == 'manual':
            ${module_builder_ir_model_fields(field)}
        %endif
    %endfor
    %for method_name, fields in model.compute_field_methods.items():
        ${builder_ir_model_field_compute(method_name, fields)}
    %endfor
    %for method_name, fields in model.inverse_field_methods.items():
        ${builder_ir_model_field_inverse(method_name, fields)}
    %endfor
    %for method_name, fields in model.search_field_methods.items():
        ${builder_ir_model_field_search(method_name, fields)}
    %endfor
    %for method in model.method_ids:
        ${builder_ir_model_method(method)}
    %endfor
    %if model.rewrite_create_method:
    @api.model
    def create(self, vals):
        %if model.allow_sequence:
        %for i in model.field_sequence_ids:
        vals['${replaceX_(i.m_field_ids.name)}'] = self.env['ir.sequence'].next_by_code('${replaceX_(i.sequence_id.code)}') + vals['${replaceX_(i.m_field_ids.name)}'] or _('New')
        %endfor
        %endif
        return super(${convM2C(model.model)}, self).create(vals)
    %endif

    %if model.rewrite_write_method:
    @api.multi
    def write(self, vals):
        return super(${convM2C(model.model)},self).write(vals)
    %endif

    %if model.rewrite_unlink_method:
    @api.multi
    def unlink(self):
        return super(${convM2C(model.model)},self).unlink()
    %endif
</%def>

<%def name="module_builder_ir_model_fields(field)">
    ${replaceX_(field.name)} = fields.${field.ttype.capitalize()}(
    %if field.ttype == 'many2many':
        %if field.relation:
            relation='${replaceX_(field.relation)}',
        %endif
        %if field.relation_table:
            relation_table='${replaceX_(field.relation_table)}',
        %endif
        %if field.column1 and field.column2 :
            column1='${field.column1}', column2='${field.column2}',
        %endif
    %endif
    %if field.ttype == 'many2one':
        %if field.relation:
            '${replaceX_(field.relation)}',
        %endif
        %if field.on_delete:
            on_delete='${field.on_delete}',
        %endif
    %endif
    %if field.ttype == 'one2many':
        %if field.relation:
            relation='${replaceX_(field.relation)}',
        %endif
        %if field.relation_field:
            relation_field='${replaceX_(field.relation_field)}',
        %endif
    %endif
    %if field.ttype == 'many2many' or field.ttype == 'many2one' or field.ttype == 'one2many':
        %if field.domain:
            domain='${field.domain}',
        %endif
    %endif
    %if field.ttype == 'char' or field.ttype == 'reference':
        %if field.size:
            size=${field.size},
        %endif
    %endif
    %if field.ttype == 'text' or field.ttype == 'char' or field.ttype == 'html':
        %if field.translate:
            translate=True,
        %endif
    %endif
    %if field.ttype == 'selection' or field.ttype == 'reference':
        selection=${field.selection},
    %endif
    %if field.required:
        required=True,
    %endif
    %if field.readonly:
        readonly=True,
    %endif
    %if field.store:
        store=True,
    %endif
    %if field.index:
        index=True,
    %endif
    %if field.copy:
        copy=True,
    %endif
    %if field.track_visibility:
        track_visibility='${field.track_visibility}',
    %endif
    %if field.field_description:
        string='${field.field_description}',
    % endif
    %if field.help:
        help='''${ field.help }''',
    %endif
    %if field.digits:
        digits=(${field.digits}),
    %endif
    %if field.related:
        related='${field.related}',
    %endif
    %if field.groups:
        groups='
        %for group in field.groups:
            ${group.get_external_id()[group.id]},
        %endfor
        '
    %endif
    %if field.want_compute:
        compute='${replaceX_(field.cmethod)}',
    %endif
    %if field.want_inverse:
        inverse='${replaceX_(field.imethod)}',
    %endif
    %if field.want_search:
        search='${replaceX_(field.smethod)}',
    %endif
    %if field.want_default:
        default=${replaceX_(field.dmethod)},
    %endif
    )
</%def>
<%def name="builder_ir_model_field_compute(method_name, fields)">
    @api.one
    def ${replaceX_(method_name)}(self):
    %for field in fields:
        self.${replaceX_(field)} = False
    %endfor
</%def>

<%def name="builder_ir_model_field_inverse(method_name, fields)">
    @api.one
    def ${replaceX_(method_name)}(self):
    %for field in fields:
        #self. = self.${replaceX_(field)}
    % endfor
        pass
</%def>

<%def name="builder_ir_model_field_search(method_name, fields)">
    def ${replaceX_(method_name)}(self, operator, value):
        return [
    %for field in fields:
        ('${replaceX_(field)}', operator, value)
    %endfor
        ]
</%def>

<%def name="builder_ir_model_field_default(method_name, fields)">
    @api.model
    def ${replaceX_(method_name)}(self):
        return False
</%def>

<%def name="builder_ir_model_method(method)" >
    %if method.type == 'sm':
        %if method.arguments:
        <% margs = method.arguments %>
        %else:
        <% margs = '' %>
        %endif
    @api.model
    def ${method.name}(self,${margs}):
        pass
    %elif method.type == 'si':
    @api.one
    %if method.use_cache:
    @api.depends('${','.join(replaceListX_(method.field_names))}')
    %endif
         %if method.arguments:
        <% margs = method.arguments %>
        %else:
        <% margs = '' %>
        %endif
    def ${method.name}(self,${margs}):
        pass
    %elif method.type == 'onchange':
    @api.onchange('${','.join(replaceListX_(method.field_names))}')
    def ${method.name}(self):
        pass
    %elif method.type == 'constraint':
    @api.constrains('${ ','.join(replaceListX_(method.field_names))}')
    def ${method.name}(self):
        pass
    %elif method.type == 'multi':
        %if method.arguments:
        <% margs = method.arguments %>
        %else:
        <% margs = '' %>
        %endif
    @api.multi
    def ${method.name}(self,${margs}):
        pass
    %endif
</%def>