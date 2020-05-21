flectra.define('view_editor_manager.FormRenderer', function (require) {
    "use strict";

    var FormRenderer = require('web.FormRenderer');
    return FormRenderer.extend({
        init: function (parent, state, params) {
            this.count_note_book = 0;
            return this._super.apply(this, arguments);
        },
        _renderTagNotebook: function (node) {
            var self = this;
            var $res = this._super.apply(this, arguments);
            self.count_note_book++;
            $res.attr('notebook_count', self.count_note_book);
            $res.find('ul').append(
                $('<li>').addClass('view_editor_element_page view_editor_element').append(
                    $('<a>').addClass('view_editor_add_page').append(
                        $('<i>').addClass('fa fa-plus')
                    )
                ).click(function (ev) {
                    ev.preventDefault();
                    self.trigger_up('_onAddPage', {
                        current: $res,
                        node: node
                    });
                })
            );
            return $res;
        },
        _renderTabHeader: function (page, page_id) {
            var self = this;
            var $res = this._super.apply(this, arguments);
            if (page.attrs.name) {
                $res.addClass('view_editor_element_page view_editor_element').click(function (ev) {
                    ev.preventDefault();
                    self.trigger_up('_onPageSelect', {
                        current: $res,
                        node: page
                    });
                });
            }
            return $res;
        },
        _renderTabPage: function () {
            var $res = this._super.apply(this, arguments);
            return $res;
        },
        _renderButtonBox: function (node) {
            var self = this;
            var $res = this._super.apply(this, arguments);
            $res.prepend($('<div>').addClass('btn btn-sm view_editor_stat_button')
                .append($('<div>').addClass('fa fa-plus fa-fw view_editor_button_icon')).click(function (ev) {
                    ev.preventDefault();
                    self.trigger_up('_onAddStatButton', {
                        current: this,
                        node: node
                    });
                })
            );
            return $res;
        },
        _renderNode: function (node) {
            var res = this._super.apply(this, arguments);
            if (res[0].tagName === 'A')
                res.addClass('view_editor_forced_closed');
            if (_.isObject(res)) {
                if (res.hasClass('o_chatter')) {
                    res.find('.btn-link').addClass('view_editor_forced_closed');
                }
            }
            return res;
        },
        _renderGenericTag: function (node) {
            var res = this._super.apply(this, arguments);
            return res;
        },
        _postProcessField: function (widget, node) {
            var $res = this._super.apply(this, arguments);
            return $res;
        },
        _renderInnerGroup: function (node) {
            var self = this;
            var $res = this._super.apply(this, arguments);
            $res.addClass('view_editor_element_groups');
            _.each(node.children, function (child) {
                if (child.tag === 'field') {
                    var $widget = $res.find('[name="' + child.attrs.name + '"]');
                    var $tr = $widget.closest('tr');
                    if ($tr.find('a').length) {
                        $tr.find('a').addClass('view_editor_forced_closed');
                    }
                    self.setNodeSelectable($tr, child);
                    if ($widget.is('.o_invisible_modifier')) {
                        $tr.find('.o_invisible_modifier')
                            .removeClass('o_invisible_modifier');
                        $tr.addClass('view_editor_invisible_modifier');
                    }
                }
            });
            return $res;
        },
        _renderInnerGroupField: function (node) {
            var $res = this._super.apply(this, arguments);
            return $res;
        },
        setNodeSelectable: function ($el, node) {
            var self = this;
            $el.addClass('view_editor_element').click(function (ev) {
                ev.preventDefault();
                self.trigger_up('_onNodeSelect', {
                    current: $el,
                    node: node
                });
            });
        }
    });
});