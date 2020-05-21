flectra.define('view_editor_manager.ListRenderer', function (require) {
    "use strict";
    var ListRenderer = require('web.ListRenderer');

    return ListRenderer.extend({
        events: _.extend({}, ListRenderer.prototype.events, {
            'click th:not(.view_editor_element_th), td:not(.view_editor_element_td)': '_onColClick'
        }),
        init: function () {
            return this._super.apply(this, arguments);
        },
        _render: function () {
            var $res = this._super.apply(this, arguments);
            var self = this;
            this.$('th, td').addClass('view_editor_element_tab');
            this.$('th, td').hover(function (ev) {
                var tindex = parseInt($(this).index()) + 1;
                $('td:nth-child(' + tindex + ')').addClass('view_editor_element_col');
                $('th:nth-child(' + tindex + ')').addClass('view_editor_element_col');
            }, function () {
                var tindex = parseInt($(this).index()) + 1;
                $('td:nth-child(' + tindex + ')').removeClass('view_editor_element_col');
                $('th:nth-child(' + tindex + ')').removeClass('view_editor_element_col');
            });
            $res.done(function () {
                self.$el.find('.o_list_record_selector').remove();
            });
            return $res
        },
        _renderHeader: function () {
            var $header = this._super.apply(this, arguments);
            _.each($header.find('th'), function (th) {
                $(th).after($('<th>').addClass('view_editor_element_th'));
            });
            return $header;
        },
        _renderHeaderCell: function (node) {
            var $th = this._super.apply(this, arguments);
            return $th;
        },
        _renderRow: function () {
            var $row = this._super.apply(this, arguments);
            _.each($row.find('td'), function (td) {
                $(td).after($('<td>').addClass('view_editor_element_td'));
            });
            return $row;
        },
        _onColClick: function (ev) {
            ev.preventDefault();
            var $el = $(ev.currentTarget);
            var $heading = $el.closest('table').find('th').eq($el.index());
            var field_name = $heading.data('name');
            var node = _.find(this.columns, function (column) {
                return column.attrs.name === field_name;
            });
            this.trigger_up('_onColSelect', {
                node: node,
                current: $heading
            });
        }
    });
});