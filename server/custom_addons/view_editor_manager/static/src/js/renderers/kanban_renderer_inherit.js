flectra.define('view_editor_manager.KanbanRenderer', function (require) {
    "use strict";
    var KanbanRenderer = require('web.KanbanRenderer');
    var KanbanEditor = require('view_editor_manager.KanbanEditor');

    return KanbanRenderer.extend({
        init: function () {
            this._super.apply(this, arguments);
            var state = this.state;
            state = this.is_grouped(state);
            this.kanbanRecord = state && state.data[0];
        },
        is_grouped: function (state) {
            this.isGrouped = !!this.state.groupedBy.length;
            if (this.isGrouped) {
                state = _.find(this.state.data, function (group) {
                    return group.count > 0;
                }) || this.state.data[0];
            }
            return state;
        },
        _render: function () {
            this._super.apply(this, arguments);
            this.$el.empty();
            this.$el.addClass('view_editor_kanban');
            this.$el.toggleClass('o_kanban_grouped', this.isGrouped);
            this.$el.toggleClass('o_kanban_ungrouped', !this.isGrouped);
            var fragment = document.createDocumentFragment();
            this._renderUngrouped(fragment);
            this._renderGhostDivs(fragment, 4);
            this.$el.append(fragment);
        },
        _renderUngrouped: function (fragment) {
            var self = this;
            var isDash = this.$el.hasClass('o_kanban_dashboard');
            this.recordEditor = new KanbanEditor(
                this, this.kanbanRecord, this.recordOptions, isDash);
            this.widgets.push(this.recordEditor);
            var def = this.isPromise(this.recordEditor);
            if (def) {
                this.recordEditor.fail(function (r) {
                    self.do_notify('Kanban', 'No Kanban Record Found');
                    return $.Deferred().reject();
                });
            } else {
                this.recordEditor.appendTo(fragment);
            }
        },

        isPromise: function (value) {
            if (typeof value === 'object' && typeof value.then !== "function") {
                return false;
            }
            var promiseThenSrc = String($.Deferred().then);
            var valueThenSrc = String(value.then);
            return promiseThenSrc === valueThenSrc;
        }

    });
});