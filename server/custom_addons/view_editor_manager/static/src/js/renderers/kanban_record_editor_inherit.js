flectra.define('view_editor_manager.KanbanEditor', function (require) {
    "use strict";
    var KanbanRecord = require('web.KanbanRecord');

    return KanbanRecord.extend({

        init: function (parent, state, options) {
            if (state)
                this._super.apply(this, arguments);
            else
                return $.Deferred().reject();
        },

        _render: function () {
            this._super.apply(this, arguments);
            this.$el.addClass('kanban-full');
        },

        _processField: function ($field, field_name) {
            var self = this;
            $field = this._super.apply(this, arguments);
            var field = this.record[field_name];
            var node = {
                tag: 'field',
                attrs: field
            };
            this.setNodeSelectable($field);
            $field.click(function (ev) {
                self.trigger_up('_onKanbanRecord', {
                    current: $field,
                    node: node
                })
            });
            return $field
        },
        _processWidget: function ($field, field_name) {
            var self = this;
            var widget = this._super.apply(this, arguments);
            var field = this.record[field_name];
            var node = {
                tag: 'field',
                attrs: field
            };
            this.setNodeSelectable(widget.$el);
            widget.$el.click(function (ev) {
                self.trigger_up('_onKanbanRecord', {
                    current: widget.$el,
                    node: node
                })
            });
            return widget
        },
        setNodeSelectable: function ($node) {
            $node.addClass('view_editor_element')
        }

    });
});