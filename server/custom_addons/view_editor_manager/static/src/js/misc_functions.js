flectra.define('view_editor_manager.Miscellaneous', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');
    var data_manager = require('web.data_manager');
    var framework = require('web.framework');
    var core = require('web.core');

    return {

        add_new_view: function (action, options) {
            var self = this;
            var def = $.Deferred();
            var attrs = {};
            if (options.view_to_add === 'calendar') {
                attrs = {
                    'date_stop': 'write_date',
                    'date_start': 'create_date'
                };
            }
            core.bus.trigger('clear_cache');
            data_manager.invalidate();
            ajax.jsonRpc('/view_editor_manager/add_new_view', 'call', {
                action_type: action.type,
                action_id: action.id,
                model: action.res_model,
                view_mode: action.view_mode,
                options: options,
                view_attrs: attrs
            }).then(function (resp) {
                if (resp !== true) {
                    Dialog.alert(self, resp);
                    def.reject();
                } else {
                    self.get_new_action(action.id).then(function (act) {
                        def.resolve(act);
                    });
                }
            });
            return def;
        },
        get_new_action: function (id) {
            return data_manager.load_action(id).then(function (new_action) {
                return new_action;
            });
        },
        update_view: function (options) {
            var self = this;
            var def = $.Deferred();
            framework.blockUI();
            ajax.jsonRpc('/view_editor_manager/update_view', 'call', {
                options: options
            }).done(function (resp) {
                data_manager.invalidate();
                framework.unblockUI();
                def.resolve(1);
            }).fail(function (resp) {
                Dialog.alert(self, "Failed To Update View " + resp);
                framework.unblockUI();
                def.reject();
            });
            return def;
        },

        set_or_get_default_value: function (options) {
            var response = ajax.jsonRpc('/view_editor_manager/default_value', 'call', {
                options: options
            });
            if (options['op'] === 'set') {
                response.done(function (resp) {
                    data_manager.invalidate();
                });
            } else {
                return response;
            }
        },

        rstring: function (size) {
            var text = "";
            var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
            for (var i = 0; i < size; i++)
                text += possible.charAt(Math.floor(Math.random() * possible.length));
            return text.toLowerCase();
        },

    };
});