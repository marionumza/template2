flectra.define('MarketingAutomation.FcSideBar', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var framework = require('web.framework');
    var DomainSelectorDialog = require("web.DomainSelectorDialog");
    var Domain = require("web.Domain");


    var flow_chart_main = Widget.extend({
        template: 'marketing_automation.FlowChartSideBar',
        events: {
            'click #reload_activity': '_onReloadActivity',
            'click #fc_delete': '_OnDeleteNode',
            'click #fc_save_activity_builder': '_OnSaveActivityBuilder',
            'click #fc_exit_activity_builder': '_OnLeaveActivityBuilder',
            'click li.disabled': '_enableTab',
            'change input,select': '_updateActivityData',
            'click #domain_value': '_updateDomain'
        },
        custom_events: {
            'autoSaveActivity': 'save_activity',
            'setOperatorData': '_setSelectedData'
        },

        init: function (parent, flowchart, id) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.$flowChart = flowchart;
            this.active_id = id
        },

        _onReloadActivity: function () {
            this._loadActivity();
        },

        _loadActivity: function () {
            var self = this;
            var ir_model = self._fetch_or_write_data('search_read', 'ir.model', [], []);
            var mass_mailing = self._fetch_or_write_data('search_read', 'mail.mass_mailing', [['marketing_automation', '=', true]], []);
            var action_server = self._fetch_or_write_data('search_read', 'ir.actions.server', [], []);
            framework.blockUI();
            $.when(ir_model, mass_mailing, action_server).done(function (model, mail, server) {
                var data = [];
                if (model.length) {
                    _.each(model, function (e) {
                        data.push({id: e.id, text: e.display_name, model: e.model});
                    });
                    self.$el.find('input#model').select2({
                        placeholder: 'Select Model',
                        data: data
                    });
                    self.$el.find('input#model').attr('readonly', true);
                    data = [];
                }
                if (mail.length) {
                    _.each(mail, function (e) {
                        data.push({id: e.id, text: e.display_name});
                    });
                    self.$el.find('input#mail_template').select2({
                        placeholder: 'Select Mail Template',
                        data: data
                    });
                    data = [];
                }
                if (server.length) {
                    _.each(server, function (e) {
                        data.push({id: e.id, text: e.display_name});
                    });
                    self.$el.find('input#server_action').select2({
                        placeholder: 'Select Mail Template',
                        data: data
                    });
                    data = [];
                }
                framework.unblockUI();
            });
        },

        willStart: function () {
            var self = this;
            self._loadActivity();
            return this._super.apply(this, arguments)
        },

        _fetch_or_write_data: function (method_name, model_name, domain, args) {
            var self = this;
            var def = self._rpc({
                model: model_name,
                method: method_name,
                domain: domain,
                args: args
            });
            return def;
        },

        _updateActivityData: function (ev) {
            var self = this;
            var $target = $(ev.currentTarget);
            var id = $target.attr('id');
            var value = $target.val() || '';
            var data = this.operator_data;
            var whole_data = this.parent.$flowChart.flowchart('getData');
            var options = {};
            var model = false;
            switch (id) {
                case 'name':
                    options.name = value;
                    break;
                case 'model':
                    break;
                case 'mail_template':
                    options.mass_mailing_id = value;
                    break;
                case 'server_action':
                    break;
                case 'wait':
                    options.wait_for = value;
                    break;
                case 'waiting_type':
                    options.waiting_type = value;
                    break;
                case 'domain_value':
                    options.domain = '[[]]';
            }
            if (data.activity_type === 'send_mail') {
                model = 'mail.marketing.activity';
            } else if (data.activity_type === 'activity_wait') {
                model = 'mail.activity.waiting';
            }
            this._fetch_or_write_data('write', model,
                [], [[data.id], options]).then(function (res) {
                if (res) {
                    var title = whole_data.operators[data.operator_id]['properties'].title;
                    if (options.wait_for) {
                        whole_data.operators[data.operator_id]['properties'].title = title.replace(/\d/g, value);
                    }
                    if (options.waiting_type) {
                        if (title.search('minutes') !== -1) {
                            title = title.replace('minutes', value);
                        } else if (title.search('hours') !== -1) {
                            title = title.replace('hours', value);
                        } else if (title.search('day') !== -1) {
                            title = title.replace('day', value);
                        } else if (title.search('week') !== -1) {
                            title = title.replace('week', value);
                        } else if (title.search('month') !== -1) {
                            title = title.replace('month', value);
                        }
                        whole_data.operators[data.operator_id]['properties'].title = title;
                    }
                    if (options.name) {
                        whole_data.operators[data.operator_id]['properties'].title = value;
                    }
                    self.parent.$flowChart.flowchart('setData', whole_data);
                    self.save_activity();
                }
            });
        },

        _updateDomain: function (ev) {
            ev.preventDefault();
            var self = this;
            var whole_data = this.parent.$flowChart.flowchart('getData');
            var data = this.operator_data;
            var model = self.$el.find('#model').select2('data');
            var $input = $(ev.currentTarget);
            var dialog = new DomainSelectorDialog(self, model.model, $input.val(), {
                readonly: false
            }).open();
            dialog.on("domain_selected", self, function (e) {
                $input.val(Domain.prototype.arrayToString(e.data.domain));
                self._rpc({
                    route: '/marketing_automation/write-domain-flowchart',
                    params: {
                        domain: $input.val(),
                        active_id: data.id
                    }
                }).done(function (res) {
                    if (res) {
                        whole_data.operators[data.operator_id]['properties'].title = "When " + $input.val();
                        self.parent.$flowChart.flowchart('setData', whole_data);
                        self.save_activity();
                    }
                })
            });
        },

        _OnDeleteNode: function () {
            var self = this;
            var data = self.operator_data;
            if (data) {
                if (data.id == 'start') {
                    self.do_warn('Readonly!', 'Selected Node Cannot Be Deleted');
                    return;
                }
                self._rpc({
                    route: '/marketing_automation/ma-unlink-record-flowchart',
                    params: {
                        data: data
                    }
                }).done(function () {
                    self.save_activity();
                    self.parent.$flowChart.flowchart('deleteSelected');
                    self.operator_data = null;
                });
            }
        },

        _setSelectedData: function (ev) {
            this.operator_data = ev.data;
            this._fillActivityInputForConfig(ev.data)
        },

        clear_before_fetch: function ($config_controls) {
            $config_controls.find('#name').val('');
            $config_controls.find('#model').select2('val', '');
            $config_controls.find('#mail_template').select2('val', '');
            $config_controls.find('#server_action').select2('val', '');
            $config_controls.find('#wait').val('');
            $config_controls.find('#domain_value').val('');
        },

        _fillActivityInputForConfig: function (data) {
            var self = this;
            var $config_controls = self.$el.find('.config-controls');
            self.clear_before_fetch($config_controls);
            if (data.type === 'operator') {
                $config_controls.find('.form-group').addClass('hidden');
                self.$el.find('li.active').next('li').find('a').trigger('click', {
                    validated: true
                });
                switch (data.activity_type) {
                    case 'send_mail':
                        var res = self._fetch_or_write_data('search_read', 'mail.marketing.activity', [['id', '=', data.id]], []);
                        res.done(function (vals) {
                            var v = vals[0];
                            var $name = $config_controls.find('#name');
                            var $model = $config_controls.find('#model');
                            var $mail_template = $config_controls.find('#mail_template');
                            $name.val(v.display_name || '');
                            $model.select2('val', v.model_id[0] || '');
                            $mail_template.select2('val', v.mass_mailing_id[0] || '');
                            $name.parent().removeClass('hidden');
                            $model.parent().removeClass('hidden');
                            $mail_template.parent().removeClass('hidden');
                        });
                        break;
                    case 'action':
                        var res = self._fetch_or_write_data('search_read', 'mail.marketing.activity', [['id', '=', data.id]], []);
                        res.done(function (vals) {
                            var v = vals[0];
                            var $name = $config_controls.find('#name');
                            var $model = $config_controls.find('#model');
                            var $action = $config_controls.find('#server_action');
                            $name.val(v.display_name || '');
                            $model.select2('val', v.model_id[0] || '');
                            $action.select2('val', v.ir_actions_server_id[0] || '');
                            $name.parent().removeClass('hidden');
                            $model.parent().removeClass('hidden');
                            $action.parent().removeClass('hidden');
                        });
                        break;
                    case 'activity_wait':
                        var res = self._fetch_or_write_data('search_read', 'mail.activity.waiting', [['id', '=', data.id]], []);
                        res.done(function (vals) {
                            var v = vals[0];
                            var $wait = $config_controls.find('#wait');
                            var $for = $config_controls.find('#waiting_type');
                            $wait.val(v.wait_for || '');
                            $for.val(v.waiting_type);
                            $wait.parent().removeClass('hidden');
                            $for.parent().removeClass('hidden');
                        });
                        break;
                    case 'domain_rules':
                        var res = self._fetch_or_write_data('search_read', 'mail.activity.rules', [['id', '=', data.id]], []);
                        res.done(function (vals) {
                            var v = vals[0];
                            var $model = $config_controls.find('#model');
                            var $domain = $config_controls.find('#domain_value');
                            $model.select2('val', v.model_id[0] || '');
                            $domain.val(v.domain || '');
                            $model.parent().removeClass('hidden');
                            $domain.parent().parent().removeClass('hidden');
                        });
                        break;
                }
            }
        },
        _OnLeaveActivityBuilder: function () {
            var self = this;
            self.do_action({
                type: 'ir.actions.act_window',
                res_id: self.active_id,
                res_model: 'mail.marketing',
                views: [[false, 'form']],
                target: 'current',
            }, {
                clear_breadcrumbs: true
            }).done(function () {
                self.parent.enable_flectra_sidebar();
            })
        },

        _OnSaveActivityBuilder: function () {
            var self = this;
            self.save_activity().done(function (res) {
                self.do_notify('Saved!', 'Activity Saved Successfully');
            });
        },

        save_activity: function () {
            var self = this;
            var data = self.parent.$flowChart.flowchart('getData');
            return self._rpc({
                route: '/marketing_automation/ma-save-activity-builder-state',
                params: {
                    data: JSON.stringify(data),
                    active_id: self.active_id
                }
            })
        },

        start: function () {
            var self = this;
            self.register_drag_drop_container();
        },

        register_drag_drop_container: function () {
            var self = this;
            self.$el.find('.fc_drag_menu_container').draggable({
                helper: "clone",
                stack: ".flowchart-container",
            });
        },

        _enableTab: function (ev, valid) {
            if (valid) {
                return valid.validated;
            }
            ev.stopPropagation();
            ev.preventDefault();
            ev.stopImmediatePropagation();
        }
    });
    return flow_chart_main;
});