flectra.define('view_editor_manager.VirtualSearchView', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var core = require('web.core');
    var qweb = core.qweb;

    return Widget.extend({
        className: "view_editor_search_view",
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.arch = options.arch;
            this.fields = options.fields
        },

        start: function () {
            var self = this;
            this.$el.empty();
            this.$el.html(qweb.render('view_editor_manager.searchRenderer', this.widget));
            this.node_attrs = [];
            _.each(this.arch.children, function (node, index) {
                self.node_attrs.push(node.attrs);
                if (node.tag === "field") {
                    self.add_field(node, index);
                } else if (node.tag === "filter") {
                    self.add_filter(node, index);
                } else if (node.tag === "separator") {
                    self.add_separator(node, index);
                } else if (node.tag === "group") {
                    self.loop_group_by(node, index);
                }
            });

            return this._super.apply(this, arguments);
        },
        add_field: function (el, index) {
            var self = this;
            var $tbody = this.$('.view_editor_search_autocompletion_fields tbody');
            var fstring = this.fields[el.attrs.name].string;
            var string = el.attrs.string || fstring;
            var field_name = el.attrs.name || null;
            var $row = $('<tr>').append(
                $('<td>').attr('index', index).attr('name', field_name).append(
                    $('<span>').text(string)
                ));
            if (field_name) {
                $row.addClass('view_editor_element operation_field');
                $row.click(function (ev) {
                    self.trigger_up('_onNodeSelect', {
                        'current': $row,
                        'node': el
                    });
                });
            }
            $tbody.append($row);
            return $row;
        },
        add_filter: function (el, index) {
            var self = this;
            var $tbody = this.$('.view_editor_search_filters tbody');
            var display_string = el.attrs.string || el.attrs.help;
            var field_name = el.attrs.name || null;
            var $row = $('<tr>').append(
                $('<td>').attr('index', index).attr('name', field_name).append(
                    $('<span>').text(display_string)
                ));
            if (field_name) {
                $row.addClass('view_editor_element operation_filter');
                $row.click(function (ev) {
                    self.trigger_up('_onNodeSelect', {
                        'current': $row,
                        'node': el
                    });
                });
            }
            $tbody.append($row);
            return $row;
        },
        add_separator: function (node, index) {
            var $tbody = this.$('.view_editor_search_filters tbody');
            var td = $('<td>').attr('index', index).append(
                $('<hr/>')
            );
            var $row = $('<tr class="view_editor_search_view_separator">').html(td);

            $tbody.append($row);
            return $row;
        },
        add_group_by: function (el, index) {
            var self = this;
            var $tbody = this.$('.view_editor_search_group_by tbody');
            var display_string = el.attrs.string;
            var field_name = el.attrs.name || null;
            var $row = $('<tr>').append(
                $('<td>').attr('index', index + 1).attr('name', field_name).append(
                    $('<span>').text(display_string)
                ));
            if (field_name) {
                $row.addClass('view_editor_element operation_group');
                $row.click(function (ev) {
                    el.tag = 'field';
                    el.tag_group = 'filter';
                    self.trigger_up('_onNodeSelect', {
                        'current': $row,
                        'node': el
                    });
                });
            }
            $tbody.append($row);
            return $row;
        },
        loop_group_by: function (groups, index) {
            var self = this;
            _.each(groups.children, function (node, i) {
                if (node.tag === "filter") {
                    self.add_group_by(node, i);
                }
            });
        }
    });
});
