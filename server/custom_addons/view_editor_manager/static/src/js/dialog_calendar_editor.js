flectra.define('view_editor_manager.DialogCalendarEditor', function (require) {
    "use strict";
    var Dialog = require('web.Dialog');

    return Dialog.extend({
        template: 'view_editor_manager.calendar_view',
        init: function (parent, fields, attrs) {
            this.ordered_fields = fields;
            this.parent = parent;
            this.attrs = attrs;
            var options = {
                title: 'Calendar Editor',
                size: 'medium',
                buttons: [
                    {
                        text: "save",
                        classes: 'btn-success',
                        click: _.bind(this.save_data, this)
                    },
                    {text: "Cancel", classes: 'btn-danger', close: true}
                ]
            };
            this._super(parent, options);
        },
        start: function () {
            var self = this;
            self._opened.done(function () {
                self.set_values_to_fields();
            });
        },
        set_values_to_fields: function () {
            var self = this;
            _.each(self.attrs, function (e, i) {
                var select = $('select#' + i);
                var input = $('input#' + i);
                if (select.length && i !== 'mode') {
                    select.find(':selected').val(e);
                    select.find(':selected').text(self.parent.state.fields[e].string);
                } else {
                    if (select.has('option:contains(' + e + ')').length) {
                        $("select#mode option[value=" + e + "]").prop('selected', true);
                    }

                }
                if (input.length) {
                    input.prop('checked', (e === 'True'));
                }
            });
        },
        save_data: function () {
            var self = this;
            var quick_add = self.$el.find('#quick_add');
            var date_start = self.$el.find('#date_start');
            var date_stop = self.$el.find('#date_stop');
            var date_delay = self.$el.find('#date_delay');
            var color = self.$el.find('#color');
            var all_day = self.$el.find('#all_day');
            var mode = self.$el.find('#mode');
            var calendar_data = {
                quick_add: quick_add[0].checked,
                date_start: date_start.val() || false,
                date_stop: date_stop.val() || false,
                date_delay: date_delay.val() || false,
                color: color.val() || false,
                all_day: all_day.val() || false,
                mode: mode.val() || false
            };
            self.trigger_up('_onUpdateCalendar', calendar_data);
            self.close();
        }
    })
});