var app_id = null;
flectra.define('module_builder.rainbow_man', function (require) {
    "use strict";

    var RainbowMan = require('web.rainbow_man');
    return RainbowMan.include({
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (this.delay) {
                setTimeout(function () {
                    setTimeout(function () {
                        self.redirect_to_module_builder()
                    }, 600);
                }, this.delay);
            }
        },
        redirect_to_module_builder: function () {
            var options = this.options;
            var context = options.context;
            if (context) {
                if (context.new_app_id) {
                    app_id = context.new_app_id;
                    this.fire_action();
                }
            }
        },
        fire_action: function () {
            var location = window.location;
            var hash = location.hash.substr(1);
            var action_string = hash.substr(hash.indexOf('action=')).split('&')[0].split('=');
            var new_action = {};
            if (action_string[0] === 'action') {
                new_action[action_string[0]] = 'mbuilder_redirect';
                location.href = location.hash.replace(action_string[0] + "=" + action_string[1], $.param(new_action));
            } else {
                location.href = location.hash + '&action=mbuilder_redirect';
            }
        }
    });
});

flectra.define('module_builder.mbuilder_redirect', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');
    var session = require('web.session');
    var framework = require('web.framework');
    var mbuilder_redirect = Widget.extend({
        init: function (parent, options) {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            this._super.apply(this, arguments);
            var action = {
                type: 'ir.actions.act_window',
                res_model: 'module.builder.main',
                view_mode: 'form',
                view_type: 'form',
                res_id: app_id,
                views: [[false, 'form']],
                target: 'current',
                context: session.user_context
            };
            framework.blockUI();
            setTimeout(function () {
                self.do_action(action, {clear_breadcrumbs: true});
                framework.unblockUI();
            }, 1000);
        },
        do_action: function (action, options) {
            this._super.apply(this, arguments);
        }
    });
    core.action_registry.add('mbuilder_redirect', mbuilder_redirect);
});