flectra.define('view_editor_manager.Renderers', function (require) {
    "use strict";
    var FormRenderer = require('view_editor_manager.FormRenderer');
    var ListRenderer = require('view_editor_manager.ListRenderer');
    var VirtualSearchView = require('view_editor_manager.VirtualSearchView');
    var KanbanRenderer = require('view_editor_manager.KanbanRenderer');
    var CalendarRenderer = require('view_editor_manager.CalendarRenderer');

    return {
        get_renderers: function () {
            return {
                form: FormRenderer,
                list: ListRenderer,
                kanban: KanbanRenderer,
                search: VirtualSearchView,
                calendar: CalendarRenderer
            }
        },
        get: function (r) {
            return this.get_renderers()[r];
        }
    }
});
