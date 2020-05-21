flectra.define('view_editor_manager.ViewRendererEngine', function (require) {
    "use strict";
    var Widget = require('web.Widget');
    var renderers = require('view_editor_manager.Renderers');
    var view_registry = require('web.view_registry');

    return Widget.extend({
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.action = options.action;
            this.fields_view = options.fields_view;
            this.active_view = options.active_view;
            this.view_env = options.view_env;
        },
        start_engine: function () {
            var def = this.start();
            if (def)
                return def;
            else
                return $.Deferred().reject('View not editable, View editor state will reset...');
        },
        start: function () {
            var self = this;
            var editing_view = self.fields_view[self.active_view];
            if (editing_view) {
                var editor_params = {
                    mode: 'readonly',
                    arch: editing_view.arch
                };
                var R = renderers.get(self.active_view);
                var View = view_registry.get(self.active_view);
                if (R && View) {
                    self.view = new View(editing_view, self.view_env);
                    return self.view.CreateBuilderEditor(self, R, editor_params);
                }
                if (self.active_view === 'search') {
                    var search_view = new R(self, editing_view);
                    return $.Deferred().resolve(search_view);
                }
            }
        }
    });
});

