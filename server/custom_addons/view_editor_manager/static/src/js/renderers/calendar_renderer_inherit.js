flectra.define('view_editor_manager.CalendarRenderer', function (require) {
    "use strict";
    var CalendarRenderer = require('web.CalendarRenderer');
    var DialogCalendarEditor = require('view_editor_manager.DialogCalendarEditor');

    return CalendarRenderer.extend({
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            this._super.apply(this, arguments);
            var $sidebar = this.$el.find('.o_calendar_sidebar');
            $sidebar.append(
                $('<button>')
                    .addClass('btn btn-primary calendar_edit_button')
                    .text('Edit Calendar')
                    .bind('click', self, self._onClick)
            );
            this.order_by_asc();
        },
        _onClick: function (ev) {
            var $widget = ev.data;
            new DialogCalendarEditor($widget, $widget.ordered_fields, $widget.arch.attrs).open();
        },
        order_by_asc: function () {
            this.ordered_fields = _.sortBy(this.state.fields, function (field) {
                return field.string.toLowerCase();
            });
        }
    });
});