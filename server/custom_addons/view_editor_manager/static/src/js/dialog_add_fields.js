flectra.define('view_editor_manager.DialogAddFields', function (require) {
    "use strict";

    var Dialog = require('web.Dialog');
    var fields_manager = require('view_editor_manager.FieldsManager');
    var field_dialog = require('view_editor_manager.FieldCreatorDialog');
    var misc = require('view_editor_manager.Miscellaneous');

    return Dialog.extend({
        template: 'view_editor.tree_view_controllers',
        events: {
            'change select#field_selection': '_onFieldSelectionChange',
            'change select#field_pos_selection': '_onFieldPosSelectionChange'
        },
        init: function (parent, model, attributes, fields_in_view, fields_not_in_view) {
            this._super(parent);
            this.parent = parent;
            this.model = model;
            this.element_attrs = attributes;
            this.fields_in_view = fields_in_view;
            this.fields_not_in_view = fields_not_in_view;
            this.options = {};
            var params = {
                title: 'Add Fields',
                size: 'small',
                buttons: [{
                    text: "Update",
                    classes: 'btn-primary',
                    click: this._onUpdate.bind(this)
                }, {
                    text: "Close",
                    close: true
                }]
            };
            this._super(parent, params);
        },
        fetch_fields: function (fields) {
            var self = this;
            _.each(Object.keys(self.fields_not_in_view), function (e) {
                fields.push({
                    id: e,
                    text: self.fields_not_in_view[e].string,
                    field_type: self.fields_not_in_view[e].type,
                    field_name: e
                });
            });
            self.$el.find('#select2_fields').select2({
                placeholder: 'Select Field',
                data: fields,
                multiple: false,
                value: []
            });
        },
        fetch_new_fields: function (prototype, fields) {
            var self = this;
            _.each(prototype, function (e, i) {
                fields.push({
                    id: i,
                    text: e.label,
                    field_type: e.type,
                });
            });
            self.$el.find('#select2_fields').select2({
                placeholder: 'Select Field',
                data: fields,
                multiple: false,
                value: []
            });
        },
        start: function () {
            var self = this, fields = [];
            self.options = _.extend(self.element_attrs, self.options);
            self.options.position = 'after';
            if (self.element_attrs.tag === 'field') {
                self.options.field_operation = 'existing_field';
                self.fetch_fields(fields);
            }
            else if (self.element_attrs.tag === 'page') {
                self.options.field_operation = 'page';
            }
            else if (self.element_attrs.tag === 'filter') {
                self.options.field_operation = 'filter';
            }
        },
        update_field: function () {
            var self = this, def = null;
            if (self.options.field_operation === 'existing_field') {
                var xpath_field = $('#select2_fields').select2("val");
                self.options.xpath_field = xpath_field;
                self.trigger('update_arch', self.options);
                self.close();
            }
            else {
                var index = $('#select2_fields').select2("val");
                var new_field = self.fields_component_widget[index];
                var params = {};
                _.each(self.fields_component_widget, function (prototype) {
                    if (prototype['label'] === new_field['label']) {
                        if (_.contains(['selection', 'one2many', 'many2one', 'many2many'], prototype['type'])) {
                            def = $.Deferred();
                            var dialog = new field_dialog(self, self.model, prototype['type'], prototype).open();
                            dialog.on('save_field', self, function (values) {
                                params.xpath_field = "x_editor_" + misc.rstring(4);
                                params.label = prototype['label'] + ' ' + misc.rstring(4);
                                params.field_type = prototype['type'];
                                params.selection_list = values.selection ? values.selection : null;
                                params.rel_id = values.rel_id ? values.rel_id : null;
                                params.field_description = values.field_description ? values.field_description : null;
                                def.resolve(params);
                                dialog.close();
                            });
                            dialog.on('closed', self, function () {
                            });
                        } else {
                            def = $.Deferred();
                            params.xpath_field = "x_editor_" + misc.rstring(4);
                            params.label = prototype['label'] + ' ' + misc.rstring(4);
                            params.field_type = prototype['type'];
                            if (prototype['type'] === 'monetary') {
                                def = $.Deferred();
                                var monetary = _.findWhere(self.exist_fields_obj, {
                                    type: 'many2one',
                                    relation: 'res.currency',
                                    name: 'currency_id'
                                });
                                if (monetary) {
                                    def.resolve(params);
                                } else {
                                    Dialog.alert(self, 'You cannot add this field on' + self.model + ' model.');
                                    def.reject();
                                }
                            } else {
                                def.resolve(params);
                            }
                        }
                    }
                });
                $.when(def).then(function (values) {
                    self.options = _.extend(self.options, values);
                    self.trigger('update_arch', self.options);
                    self.close();
                });
            }
        },
        update_page: function () {
            var self = this;
            self.options.attr_name = 'x_' + self.$el.find('#name').val().replace(/[^A-Z0-9]+/ig, "_").toLowerCase();
            self.options.attr_value = self.$el.find('#string').val() || '';
            self.trigger('update_arch', self.options);
            self.close();
        },
        update_filter: function () {
            var self = this;
            self.options.filter_name = 'x_' + self.$el.find('#name').val().replace(/[^A-Z0-9]+/ig, "_").toLowerCase();
            self.options.filter_string = self.$el.find('#string').val() || '';
            self.options.filter_domain = self.$el.find('#domain').val() || '';
            self.trigger('update_arch', self.options);
            self.close();
        },
        _onUpdate: function () {
            var self = this;
            if (self.$el.find('#select2_fields').length) {
                if (!self.$el.find('#select2_fields').select2('data')) {
                    self.$el.find('#select2_fields').addClass('alert alert-danger');
                    return;
                }
            }
            switch (self.element_attrs.tag) {
                case 'field':
                    self.update_field();
                    break;
                case 'page':
                    self.update_page();
                    break;
                case 'filter':
                    self.update_filter();
            }
        },
        _onFieldSelectionChange: function (ev) {
            var self = this;
            var option = $("#field_selection option:selected").val();
            self.options.field_operation = option;
            var prototype = [], fields = [];
            self.$el.find('#select2_fields').select2('destroy');
            if (option === 'new_field') {
                var field_widget = fields_manager['new_fields'];
                _.each(field_widget, function (widget) {
                    prototype.push({
                        'label': new widget(self).__proto__.label,
                        'type': new widget(self).__proto__.ttype
                    });
                });
                prototype = prototype.sort(function (a, b) {
                    return a.label.localeCompare(b.label);
                });
                self.fetch_new_fields(prototype, fields);
                self.fields_component_widget = prototype;
            } else {
                self.fetch_fields(fields);
            }
        },
        _onFieldPosSelectionChange: function () {
            this.options.position = $("#field_pos_selection option:selected").val();
        }
    });
});