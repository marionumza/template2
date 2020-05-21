flectra.define('view_editor_manager.ActionManager', function (require) {
    "use strict";

    var ActionManager = require('web.ActionManager');

    ActionManager.include({

        do_action: function (action, options) {
            var self = this;
            self.check_executable(action);
            if (typeof action === "object") {
                if (options) {
                    if ('no_state_change' in (options)) {
                        action.no_state_change = options.no_state_change;
                    }
                }
            }
            return this._super.apply(this, arguments);
        },
        check_executable: function (action) {
            var $toggler = $('#view_editor_toggle');
            if (action === 'main' || action.tag === 'main')
                return;
            if (action.view_id === undefined) {
                $toggler.addClass("disabled in_active");
            } else {
                $toggler.removeClass("disabled in_active");
            }
        },
        do_push_state: function () {
            var action;
            var inner_act = this.inner_action;
            if (inner_act && (action = inner_act.get_action_descr())) {
                if (action.no_state_change)
                    return;
            }
            this._super.apply(this, arguments);
        }
    });

});
