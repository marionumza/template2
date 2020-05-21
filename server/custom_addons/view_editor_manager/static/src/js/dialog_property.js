flectra.define('view_editor_manager.DialogProperty', function (require) {
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
            self.trigger('update_arch', options);
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
                if (attr_name === 'groups') {
                    self.get_group_id(target.select2('data')[0]['id']).then(function (resp) {
                        _.each(resp, function (e) {
                            attrs['attr_value'] = e.complete_name;
                            self.update_arch(attrs);
                        });
                    });
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
            self.trigger('update_arch', options);
        },
        init: function (parent, model, attributes, fields_in_view, fields_not_in_view, arch) {
            this._super(parent);
            this.arr = [];
            this.parent = parent;
            this.model = model;
            this.element_attrs = attributes;
            this.fields_in_view = fields_in_view;
            this.fields_not_in_view = fields_not_in_view;
            this.arch = arch;
            this.field_attributes = this.fields_in_view[this.element_attrs['attrs']['name']];
            this.update_attribute_value();
            this.options = {};
            var params = {
                title: 'Property Dialog',
                size: 'large',
                buttons: [{
                    text: "Close",
                    close: true
                }]
            };
            this._super(parent, params);
        },
        update_attribute_value: function () {
            var self = this;
            self.field_attributes = _.extend({}, self.field_attributes, this.element_attrs.attrs);
        },
        start: function () {
            var self = this, data = [], widget = [];
            var options = {'op': 'get', 'model': this.model, 'field_name': this.safeGet(this.field_attributes, 'name')};
            self.get_security_groups(data);
            self.get_fields_widget(widget);
            self.get_set_default_value(options);
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

        get_pairs:function(registry){
            return _.chain(registry.map).pairs();
        },

        get_filtered_data: function (field) {
            var self = this;
            return _.contains(field[1].prototype.supportedFieldTypes,
                self.safeGet(self.field_attributes, 'type')) && field[0].indexOf('.') < 0;
        },

        get_fields_widget: function (widget) {
            var self = this;
            var pairs = self.get_pairs(field_registry);
            var widgets = pairs.filter(function (arr) {
                return self.get_filtered_data(arr);
            });
            self.field_widgets = widgets.map(function (array) {
                return array[0];
            })._wrapped;
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