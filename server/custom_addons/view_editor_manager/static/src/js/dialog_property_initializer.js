flectra.define('view_editor_manager.DialogPropertyInitializer', function (require) {
    "use strict";
    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');
    var field_registry = require('web.field_registry');
    var misc = require('view_editor_manager.Miscellaneous');

    return Dialog.extend({
        template: 'view_editor.tree_view_properties',
        events: {
            'change input[type=checkbox]': 'onCheckChange',
            'change input[type=text]': 'onTextChange'
        },
        onCheckChange: function (ev) {
            var self = this;
            var target = $(ev.target);
            var attr_name = target.attr('id');
            var checked = target.prop("checked") ? '1' : '0';
            var attrs = {
                'attr_name': attr_name,
                'attr_value': checked
            };
            var options = {};
            options.name = self.safeGet(this.field_attributes, 'name');
            options.position = 'attributes';
            options = _.extend(options, attrs);
            self.update_field_attrs(options);
        },
        onTextChange: function (ev) {
            var self = this;
            var target = $(ev.target);
            var attr_name = target.attr('id');
            var attr_value = target.val();
            if (attr_name === 'default') {
                var params = {
                    'op': 'set',
                    'model': this.model,
                    'field_name': this.safeGet(this.field_attributes, 'name'),
                    'value': attr_value
                };
                self.get_set_default_value(params);
            } else {
                var attrs = {
                    'attr_name': attr_name,
                    'attr_value': attr_value
                };
                if (attr_name === 'name') {
                    attrs['attr_value'] = 'x_' + attr_value.replace(/[^A-Z0-9]+/ig, "_").toLowerCase();
                }
                else if (attr_name === 'groups') {
                    if (target.select2('data')[0]) {
                        self.get_group_id(target.select2('data')[0]['id']).then(function (resp) {
                            _.each(resp, function (e) {
                                attrs['attr_value'] = e.complete_name;
                                self.update_arch(attrs);
                            });
                        });
                    }
                } else {
                    if (attr_name === 'widget') {
                        attrs['attr_value'] = target.select2('data')['text'];
                    }
                    self.update_arch(attrs);
                }
            }
        },
        update_arch: function (attrs) {
            var self = this, options = {};
            options.name = self.safeGet(this.field_attributes, 'name');
            options.position = 'attributes';
            options = _.extend(options, attrs);
            self.update_field_attrs(options)
        },
        update_field_attrs: function (params) {
            var key = params['attr_name'], value = params['attr_value'];
            this.new_attrs = $.extend(this.new_attrs, {[key]: value});
        },
        init: function (parent, model, attributes, fields_in_view, fields_not_in_view, arch) {
            this._super(parent);
            this.arr = [];
            this.new_attrs = {};
            this.parent = parent;
            this.model = model;
            this.element_attrs = attributes;
            this.fields_in_view = fields_in_view;
            this.fields_not_in_view = fields_not_in_view;
            this.field_attributes = this.fields_not_in_view[this.element_attrs['xpath_field']];
            this.arch = arch;
            this.options = {};
            var params = {
                title: 'Property Dialog',
                size: 'large',
                buttons: [{
                    text: "Update Properties",
                    classes: 'btn-primary',
                    click: this._onUpdate.bind(this)
                }, {
                    text: "Close",
                    close: true
                }]
            };
            this._super(parent, params);
        },
        start: function () {
            var self = this, data = [], widget = [];
            var options = {
                'op': 'get',
                'model': this.model,
                'field_name': this.safeGet(this.element_attrs, 'xpath_field')
            };
            if (self.element_attrs.field_operation === 'new_field') {
                self.set_attrs_new_field()
            }
            self.get_security_groups(data);
            self.get_fields_widget(widget);
            self.get_set_default_value(options);
        },
        set_attrs_new_field: function () {
            var label = this.element_attrs['label'];
            var name = this.element_attrs['xpath_field'];
            this.$el.find('input#string').val(label);
            this.$el.find('input#name').val(name);
        },
        _onUpdate: function () {
            this.trigger('update_attribute', this.new_attrs);
            this.close();
        },
        get_set_default_value: function (options) {
            var self = this;
            var response = misc.set_or_get_default_value(options);
            if (response) {
                response.then(function (resp) {
                    self.$el.find('#default').val(Object.values(resp)[0]);
                });
            }
        },
        get_group_id: function (id) {
            return rpc.query({
                model: 'ir.model.data',
                method: 'search_read',
                domain: [['res_id', '=', id], ['model', '=', 'res.groups']]
            })
        },
        get_security_groups: function (data) {
            var self = this;
            rpc.query({
                model: 'res.groups',
                method: 'search_read'
            }).then(function (resp) {
                _.each(resp, function (e) {
                    data.push({id: e.id, text: e.display_name})
                });
                self.$el.find('input#groups').select2({
                    placeholder: 'Security Groups',
                    data: data,
                    multiple: true,
                    value: []
                });
            });
        },
        get_fields_widget: function (widget) {
            var self = this;
            self.field_widgets = _.chain(field_registry.map).pairs().filter(function (arr) {
                return _.contains(arr[1].prototype.supportedFieldTypes,
                    self.safeGet(self.field_attributes, 'type')) && arr[0].indexOf('.') < 0;
            }).map(function (array) {
                return array[0];
            }).sortBy().value();
            for (var i = 0; i < self.field_widgets.length; i++) {
                widget.push({id: i, text: self.field_widgets[i]})
            }
            self.$el.find('#widget').select2({
                placeholder: 'Widgets',
                data: widget,
                multiple: false,
                value: []
            });
        },
        safeGet: function (obj, prop) {
            return (obj == null ? undefined : obj[prop]);
        }
    });
});