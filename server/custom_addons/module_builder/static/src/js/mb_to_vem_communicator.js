flectra.define('module_builder.mb_to_vem_communicator', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');
    var list_models_widget = Widget.extend({
        init: function (parent, context) {
            this._super.apply(this, arguments);
            this.action_manager = parent;
            this.context = context;
            this.params = context.params;
        },
        start: function () {
            var self = this;
            self._super.apply(self, arguments);
            self.modal = self.__parentedParent;
            self.modal.size = "medium";
            self.set_modal_buttons();
            self.set_modal_content();
        },
        set_modal_content: function () {
            var self = this;
            if (self.params && self.params.model_ids) {
                var data = self.params.model_ids;
                self.$el.append($('<div>').append($('<input type="text" id="model_select2">')));
                self.$el.find('#model_select2').select2({
                    placeholder: 'Select An App',
                    data: data,
                    multiple: false,
                    value: []
                });
            }
        },
        set_modal_buttons: function () {
            var self = this;
            self.modal.buttons.push({text: 'Ok', classes: 'btn btn-primary', click: self.redirect_to_view_editor});
            self.modal.buttons.push({text: 'Close', classes: 'btn btn-danger', close: true});
        },
        redirect_to_view_editor: function () {
            var self = this;
            var data = self.$el.find('#model_select2').select2('data');
            if (data) {
                this.do_action({
                    id: data.action_id,
                    name: data.action_name,
                    type: 'ir.actions.act_window',
                    res_model: data.model,
                    views: [[false, 'list'], [false, 'form']],
                    view_mode: 'list',
                    view_type: 'list',
                    view_id: data.view_id,
                    target: 'main'
                }, {action_menu_id: data.menu_id}).then(function () {
                    $('#view_editor_toggle a[view=list]').trigger('click');
                });
            }

        },
        do_action: function (action, options) {
            this._super.apply(this, arguments);
        }
    });
    core.action_registry.add('builder_list_models', list_models_widget);
});
