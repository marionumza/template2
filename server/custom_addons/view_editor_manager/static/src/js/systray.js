flectra.define('view_editor_manager.systray', function (require) {
    "use strict";

    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var session = require('web.session');

    var ViewEditorManagerTray = Widget.extend({
        template: 'view_editor_manager.activator',
        events: {
            "click a": "on_click",
        },

        on_click: function (e) {
            e.preventDefault();
            var self = this;
            var $target = $(e.currentTarget);
            var view = $target.attr('view');
            if (view) {
                self.trigger_up('view_editor_client', {
                    'view_type': view,
                    'systray': self
                });
                self.toggle_drop_down();
                self._start_view_editor_engine($target);
            } else {
                if (self.$el.hasClass('enabled')) {
                    self.reset_everything($target);
                } else {
                    self.check_available_views();
                }
            }
        },

        check_available_views: function () {
            var self = this;
            var def = $.Deferred();
            self.toggle_drop_down();
            self.trigger_up('fetch_views', {
                on_success: def.resolve.bind(def)
            });
            def.done(function (view_loader) {
                view_loader.done(function (fields_view) {
                    var views = Object.keys(fields_view);
                    self.$el.find('a.bg_icon_container').each(function (i, e) {
                        var v = $(e).attr('view');
                        var has_view_current_action = $.inArray(v, views);
                        if (has_view_current_action === -1 && v !== 'search') {
                            $(e).parent().find('.overlay_add').remove();
                            $(e).parent().addClass('not_active');
                            $(e).parent().append(
                                $('<div>').addClass('overlay_add').append(
                                    $('<span>').addClass('overlay_icon').html($('<span>').addClass('icon_view_text')
                                        .text('Add This View')).prepend(
                                        $('<i>').addClass('fa fa-plus-circle')
                                    )
                                ).bind('click',
                                    {
                                        widget: self,
                                        view_to_activate: v
                                    },
                                    self._onActivateView));
                        }else{
                            $(e).parent().removeClass('not_active');
                        }
                    });
                    self.toggle_drop_down();
                });
            });
        },
        _onActivateView: function (ev) {
            var self = ev.data.widget;
            var view_to_activate = ev.data.view_to_activate;
            self.trigger_up('activate_new_view', {
                view: view_to_activate
            })
        },
        reset_everything: function ($target) {
            var self = this;
            self._stop_view_editor_engine($target);
            self.trigger_up('view_editor_reset');
            self.toggle_drop_down();
        },
        toggle_drop_down: function () {
            var self = this;
            setTimeout(function () {
                var $d = self.$el.find('a[data-toggle]');
                var toggle = $d.attr('data-toggle');
                if (toggle) {
                    $d.attr('data-toggle', '');
                } else {
                    $d.attr('data-toggle', 'dropdown');
                }
            }, 5);
        },
        _start_view_editor_engine: function ($target) {
            if ($target.hasClass('bg_icon_container')) {
                if (!this.$el.hasClass("enabled")) {
                    this.$el.addClass('enabled');
                    this.$el.find('i.mech').attr('class', 'mech fa fa-cog fa-spin');
                }
            }
        },
        _stop_view_editor_engine: function () {
            this.$el.removeClass('enabled');
            this.$el.find('i.mech').attr('class', 'mech fa fa-cog');
        }
    });

    if (session.is_system) {
        SystrayMenu.Items.push(ViewEditorManagerTray);
    }

    return {
        ViewEditorManagerTray: ViewEditorManagerTray
    }
});
