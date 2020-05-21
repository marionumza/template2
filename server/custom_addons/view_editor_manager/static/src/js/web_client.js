flectra.define('view_editor_manager.WebClient', function (require) {
    "use strict";
    var WebClient = require('web.WebClient');
    var Context = require('web.Context');
    var misc = require('view_editor_manager.Miscellaneous');
    var core = require('web.core');
    var qweb = core.qweb;

    WebClient.include({

        custom_events: _.extend({}, WebClient.prototype.custom_events, {
            'view_editor_client': '_on_view_editor_editing',
            'view_editor_reset': '_resetWebClient',
            'fetch_views': '_fetchViews',
            'activate_new_view': '_onActivateNewView'
        }),

        init: function () {
            this._super.apply(this, arguments);
        },
        _onActivateNewView: function (ev) {
            var options = {
                view_to_add: ev.data.view
            };
            var self = this;
            var action = this.action_manager.get_inner_action();
            var action_desc = action && action.action_descr || null;
            misc.add_new_view(action_desc, options).then(function (action) {
                self.do_action(action);
            });
        },
        _fetchViews: function (ev) {
            var self = this;
            core.bus.trigger('clear_cache');
            var act = self.action_manager.get_inner_action();
            misc.get_new_action(act.action_descr.id).done(function (action) {
                var action_desc = action || null;
                var views = action_desc.views.slice();
                var context = new Context(_.extend({}, action_desc.context));
                var view_loader = self.loadViews(action_desc.res_model, context, views, {});
                ev.data.on_success(view_loader);
            })

        },
        _resetWebClient: function () {
            var action = this._action;
            var active_view = action.get_active_view();
            if (action) {
                var res_id = action.widget.env.ids && action.widget.env.ids[0];
                if (!action.action_descr.res_id) {
                    action.action_descr.res_id = res_id;
                }
                this.do_action(action.action_descr, {
                    view_type: active_view,
                    clear_breadcrumbs: true
                }).done(function () {
                    var $mainNavbar = $('#oe_main_menu_navbar');
                    $mainNavbar.find('.view-editor-nav-container').remove();
                    $mainNavbar.stop().animate({backgroundColor: 'transparent'}, {duration: 5});
                    setTimeout(function () {
                        $('.f_toggle_buttons').removeClass('hidden');
                        $('.f_menu_systray').removeClass('hidden');
                        $('#f_menu_toggle').removeClass('view_editor_forced_closed');
                        $('#f_user_toggle').removeClass('view_editor_forced_closed');
                        $('#f_apps_search').removeClass('view_editor_forced_closed');
                        $('.f_launcher').removeClass('f_launcher_close view_editor_forced_closed');
                    }, 10);
                });
            }
        },
        _on_view_editor_editing: function (ev) {
            var self = this;
            var action = this.action_manager.get_inner_action();
            var action_desc = action && action.action_descr || null;
            var view_type = ev.data.view_type;
            var active_view = action && action.get_active_view();
            var res_id = (action.widget.env.ids && action.widget.env.ids[0]) || 1;
            if (!action.action_descr.res_id) {
                action.action_descr.res_id = res_id;
            }
            self._action = action;
            this.do_action('main', {
                action: action,
                action_desc: action_desc,
                active_view: view_type,
                view_type: view_type,
                view_env: this.action_manager.inner_widget.env,
                no_state_change: true,
                clear_breadcrumbs: true,
                systray: ev.data.systray
            }).done(function () {
                self.render_view_editor_nav();
            });
        },
        render_view_editor_nav: function () {
            var self = this;
            var $mainNavbar = $('#oe_main_menu_navbar');
            var $navControls = $(qweb.render('view_editor_manager.navbar'));
            $mainNavbar.stop().animate({backgroundColor: '#303131'}, {duration: 500})
            $mainNavbar.append($navControls);
            $('.f_toggle_buttons').addClass('hidden');
            $('.f_menu_systray').addClass('hidden');
            $('#f_menu_toggle').addClass('view_editor_forced_closed');
            $('#f_user_toggle').addClass('view_editor_forced_closed');
            $('#f_apps_search').addClass('view_editor_forced_closed');
            $('.f_launcher').addClass('f_launcher_close view_editor_forced_closed');
            $navControls.find('#view_edit_exit').click(function () {
                self._resetWebClient();
            });
        }
    });

});