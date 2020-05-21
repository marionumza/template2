flectra.define('module_builder.color_picker', function (require) {
    "use strict";

    var fields = require('web.basic_fields');
    var registry = require('web.field_registry');

    var FColor = fields.FieldChar.extend({
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            self._super.apply(this, arguments);
            if (self.mode !== 'readonly') {
                var id = _.uniqueId();
                var $color_picker = $('<input>').addClass('hidden').attr('type', 'color').attr('id', id);
                self.$el.addClass('color_picker');
                setTimeout(function () {
                    self.$el.after($color_picker);
                    self.$el.off('click').on('click', function () {
                        self.onColorPicker(id);
                    });
                }, 5);
            }
        },
        onColorPicker: function (id) {
            var self = this;
            var $color_picker = $('input#' + id);
            $color_picker.trigger('click');
            $color_picker.on('change', function (e) {
                var $target = $(e.currentTarget);
                self.$el.val($target.val()).trigger('input');
                self.$el.trigger('change');
            });
        }
    });
    registry.add('color', FColor);
    return FColor
});
