flectra.define('MarketingAutomation.FlowChart', function (require) {
    'use strict';

    var core = require('web.core');
    var Widget = require('web.Widget');
    var SideBar = require('MarketingAutomation.FcSideBar');
    var DialogMailMarketing = require('MarketingAutomation.DialogMailMarketing');
    var QWeb = core.qweb;

    var flow_chart_main = Widget.extend({
        template: 'marketing_automation.FlowChart',
        events: {
            'click .minimap-controls > div': 'onZoomListener'
        },
        init: function (parent, context) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.context = context;
            this.res_model = context.res_model || 'mail.marketing';
            this.active_id = context.context.active_id;
            this.disable_flectra_sidebar();
        },

        getActivities: function () {
            var self = this;
            return self._rpc({
                model: 'mail.marketing',
                method: 'search_read',
                domain: [['id', '=', self.active_id]]
            });
        },

        _getFlowCartData: function () {
            var self = this;
            return self.$flowChart.flowchart('getData');
        },

        register_zoom_listener: function () {
            var self = this;
            //use TimeOut As We Are unable to locate $zoom container before initialization
            setTimeout(function () {
                self.$zoom = self.$flowChart;
                self.currentZoom = 2;

                // Panzoom initialization...
                self.$zoom.panzoom();
                // Centering panzoom
                self.$zoom.panzoom('pan', -(self.$zoom.width() / 4), -(self.$zoom.height() / 4));
            }, 10);
        },

        onZoomListener: function (ev) {
            var self = this;
            var $target = $(ev.currentTarget);
            var possibleZooms = [0.5, 0.75, 1, 2, 3];

            if ($target.hasClass('minimap-zoom-out')) {
                if (self.currentZoom !== 0) {
                    self.currentZoom--;
                }
            }

            if ($target.hasClass('minimap-zoom-in')) {
                if (self.currentZoom !== 4) {
                    self.currentZoom++;
                }
            }

            if ($target.hasClass('minimap-zoom-reset')) {
                self.currentZoom = 2;
            }
            $target.parents('.minimap-controls').find('.minimap-zoom-state').find('i').text(possibleZooms[self.currentZoom] + 'x');
            self.$flowChart.flowchart('setPositionRatio', possibleZooms[self.currentZoom]);
            self.$zoom.panzoom('zoom', possibleZooms[self.currentZoom], {
                disablePan: true,
                animate: true,
                focal: ev
            });
        },

        _onLinkSelect: function (link_id) {
            var from_op = this._getFlowCartData()['links'][link_id]['fromOperator'];
            var to_op = this._getFlowCartData()['links'][link_id]['toOperator'];
            var f_class = this._getFlowCartData()['operators'][from_op]['properties']['custom_class'];
            var t_class = this._getFlowCartData()['operators'][to_op]['properties']['custom_class'];
            var link_text = this._getFlowCartData()['links'][link_id]['link_text'];
            if (link_text) {
                link_text = link_text.toLowerCase();
            }
            var data = {
                active_id: this.active_id,
                parent: from_op.split('_')[2],
                child: to_op.split('_')[2],
                f_activity_type: f_class,
                t_activity_type: t_class,
                action_type: link_text,
                type: 'link'
            };
            this.side_bar.trigger_up('setOperatorData', data);
            return true;
        },

        _onAfterChange: function (changeType) {
            var self = this;
            if (changeType === 'link_create' && self.fortune_shined
                && (self.link_id || self.link_id === 0) && self.bgcolor) {
                self.$flowChart.flowchart('setLinkMainColor', self.link_id, self.bgcolor);
                self.fortune_shined = undefined;
            }
        },

        _shallIConnectLink: function (link_data) {
            var self = this;
            var from = link_data['fromOperator'];
            var to = link_data['toOperator'];
            var data = self._getFlowCartData();
            var is_valid_link = true;
            _.each(data.links, function (e, i) {
                if ((from == e['fromOperator']) && (to == e['toOperator'])) {
                    is_valid_link = false;
                }
            });

            return is_valid_link;
        },

        _onLinkCreate: function (linkId, linkData) {
            var self = this, action_type;
            var is_link_valid = true;
            if (!linkData['link_text']) {
                is_link_valid = false;
            }
            if (self.fortune_shined) {
                is_link_valid = self._shallIConnectLink(linkData);
                if (is_link_valid) {
                    self.link_id = linkId;
                    linkData['link_text'] = self.text;
                    action_type = self.text && self.text.toLowerCase().replace('on', "").trim().replace(/\ /g, '_');
                    if(!action_type) return;
                    var fdata = self._getFlowCartData();
                    var from = linkData.fromOperator.split('_')[2];
                    var to = linkData.toOperator.split('_')[2];
                    var from_act_type = fdata['operators'][linkData.fromOperator]['properties']['activity_type'];
                    var to_act_type = fdata['operators'][linkData.toOperator]['properties']['activity_type'];
                    var data = {
                        parent: from,
                        child: to,
                        from_activity: from_act_type,
                        to_activity: to_act_type,
                        res_model: self.res_model,
                        active_id: self.active_id,
                        action_type: action_type,
                    };
                    self._rpc({
                        route: '/marketing_automation/write-parent-child-relation',
                        params: {
                            data: data
                        }
                    }).done(function (res) {
                        if (res) {
                            self.side_bar.trigger_up('autoSaveActivity');
                        } else {
                            is_link_valid = res;
                            self.$flowChart.flowchart('deleteLink', linkId);
                            self.do_warn('Invalid Connection', 'The Link Cannot Be Connected!');
                        }
                    });
                } else {
                    self.do_warn('Invalid Connection', 'The Link Cannot Be Connected!');
                }
            }
            return is_link_valid;
        },

        _onOperatorMouseOver: function (operatorId, $el) {
            var self = this;
            var currentOperatorData = self._getFlowCartData()['operators'][operatorId]['properties']['outputs'];
            var key = _.keys(currentOperatorData)[0];
            var sublinks = currentOperatorData[key]['sublinks'];
            var count_sublinks = sublinks.length;
            var circle_class = 'circle' + '-' + count_sublinks + '-wheel';
            var wheel = QWeb.render('marketing_automation.FortuneWheel', {
                list: sublinks,
                circle_class: circle_class
            });
            $el.find('.circle-text').remove();
            $el.find('.' + circle_class).remove();
            $el.find('.flowchart-operator-outputs').find('.flowchart-operator-connector').prepend(wheel);
            $el.find('.' + circle_class + ' li').on('mouseover', function (ev) {
                var $t = $(ev.currentTarget);
                var s = $t.find('.text').attr('string');
                var c = $t.find('.text').css('background-color');
                $el.find('.circle-text').text(s);
                $el.find('.circle-text').css('color', c);
            });

            $el.find('.' + circle_class + ' li').on('mouseout', function (ev) {
                $el.find('.circle-text').text('');
            });

            $el.find('.' + circle_class + ' li').on('mousedown', function (ev) {
                self.fortune_shined = true;
                var $t = $(ev.currentTarget);
                var c = $t.find('.text').css('background-color');
                self.bgcolor = c;
                self.text = $(ev.target).attr('string');
                setTimeout(function () {
                    $el.find('.' + circle_class).remove();
                    $el.find('.circle-text').remove();
                }, 100);
            });

            return true
        },

        _onOperatorMouseOut: function (operatorId, $el) {
            var self = this;
            var currentOperatorData = self._getFlowCartData()['operators'][operatorId]['properties']['outputs'];
            var key = _.keys(currentOperatorData)[0];
            var sublinks = currentOperatorData[key]['sublinks'];
            var count_sublinks = sublinks.length;
            var circle_class = 'circle' + '-' + count_sublinks + '-wheel';
            $el.find('.' + circle_class).remove();
            $el.find('.circle-text').remove();
            return true;
        },

        _onOperatorSelected: function (operatorId) {
            var data = {
                type: 'operator',
                id: operatorId.split('_')[2],
                operator_id:operatorId,
                activity_type: this._getFlowCartData()['operators'][operatorId]['properties']['activity_type']
            };
            this.side_bar.trigger_up('setOperatorData', data);
            return true;
        },

        start: function () {
            var self = this;
            self.$flowChart = self.$el.find('#main_container');
            self.side_bar = new SideBar(this, this.$flowChart, this.active_id);
            self.side_bar.prependTo(self.$el);
            self.getActivities().then(function (values) {
                if (values[0]) {
                    self.register_zoom_listener();
                    var data = JSON.parse(values[0]['activity_builder_data']) || {};
                    if ($.isEmptyObject(data.operators)) {
                        var id = "flow_chart_start_" + _.uniqueId(4);
                        data = {
                            "operators": {
                                [id]: {
                                    "properties": {
                                        "title": "start",
                                        "multipleLinksOnOutput": true,
                                        "multipleLinksOnInput": true,
                                        "inputs": {"input_139": {"label": ""}},
                                        "outputs": {"output_140": {"label": "", "sublinks": [{"text": "on Trigger"}]}},
                                        "activity_type": "activity_start",
                                        "fa_icon": "fa fa-star",
                                        "custom_class": "flowchart-event-operator"
                                    }, "top": 420, "left": 1154
                                }
                            }, "links": {}, "operatorTypes": {}
                        }
                    }
                    // Apply the plugin on a standard, empty div...
                    self.$flowChart.flowchart({
                        data: data,
                        onLinkSelect: self._onLinkSelect.bind(self),
                        onLinkCreate: self._onLinkCreate.bind(self),
                        onOperatorMouseOver: self._onOperatorMouseOver.bind(self),
                        onOperatorMouseOut: self._onOperatorMouseOut.bind(self),
                        onAfterChange: self._onAfterChange.bind(self),
                        onOperatorSelect: self._onOperatorSelected.bind(self)
                    });
                    self.$flowChart.droppable({
                        accept: ".fc_drag_menu_container",
                        drop: self.onDrop.bind(self),
                    });
                } else {
                    self.do_warn('Not Editable!', 'Record Not Found');
                    self.do_action('marketing_automation.act_open_mail_marketing_view', {
                        clear_breadcrumbs: true
                    }).then(function () {
                        self.destroy();
                    });
                }
            });
        },

        onDrop: function (event, ui) {
            var self = this;
            var $draggable = ui.draggable;
            var dialog = new DialogMailMarketing(self, $draggable).open();
            dialog.on('create_record', self, function (data) {
                data = _.extend({'res_model': self.res_model, active_id: self.active_id}, data);
                self._rpc({
                    route: '/marketing_automation/ma-create-record-flowchart',
                    params: {
                        data: data
                    }
                }).done(function (res) {
                    if (res) {
                        self.createNewNode(data, ui, res);
                        self.side_bar.trigger_up('autoSaveActivity');
                    }
                });
            });
        },

        create_inputs: function (data, arr) {
            _.each(arr, function (e) {
                var id = 'input_' + [_.uniqueId(1)];
                $.extend(data.properties.inputs, {[id]: {'label': e}});
            });
        },

        create_outputs: function (data, arr) {
            _.each(arr, function (e) {
                var id = 'output_' + [_.uniqueId(1)];
                $.extend(data.properties.outputs,
                    {
                        [id]: {
                            'label': e['label'],
                            'sublinks': e['sublinks']
                        }
                    });
            });
        },

        createNewNode: function (data, ui, res) {
            var self = this;
            var activity_type = data['activity_type'];
            var operatorId = 'flow_chart_' + res + '_' + _.uniqueId(3);
            var operatorData = {
                properties: {
                    title: data.name,
                    multipleLinksOnOutput: true,
                    multipleLinksOnInput: true,
                    inputs: {},
                    outputs: {}
                }
            };
            var elOffset = ui.offset;
            var containerOffset = self.$flowChart.parent().offset();
            if (elOffset.left > containerOffset.left &&
                elOffset.top > containerOffset.top &&
                elOffset.left < containerOffset.left + self.$flowChart.parent().width() &&
                elOffset.top < containerOffset.top + self.$flowChart.parent().height()) {
                var flowchartOffset = self.$flowChart.offset();
                var relativeLeft = elOffset.left - flowchartOffset.left;
                var relativeTop = elOffset.top - flowchartOffset.top;
                var positionRatio = self.$flowChart.flowchart('getPositionRatio');
                relativeLeft /= positionRatio;
                relativeTop /= positionRatio;
                operatorData.top = relativeTop;
                operatorData.left = relativeLeft;
            }
            operatorData['properties']['activity_type'] = activity_type;
            if (activity_type === 'send_mail') {
                operatorData['properties']['fa_icon'] = 'fa fa-envelope';
                operatorData['properties']['custom_class'] = 'flowchart-action-operator';
                self.create_inputs(operatorData, ['']);
                self.create_outputs(operatorData, [
                    {
                        'label': '',
                        'sublinks': [{text: 'on Send Mail'}, {text: 'on Email Bounced'}, {text: 'on Child Activity'}, {text: 'on Email Open'}, {text: 'on Email Not Open'}, {text: 'Email Replied'}, {text: 'Email Not Replied'}, {text: 'on Email Click'}, {text: 'on Email Not Click'}]
                    }]);
            }
            else if (activity_type === 'action') {
                operatorData['properties']['fa_icon'] = 'fa fa-microchip';
                operatorData['properties']['custom_class'] = 'flowchart-action-operator';
                self.create_inputs(operatorData, ['']);
                self.create_outputs(operatorData, [
                    {'label': '', 'sublinks': [{text: 'on Child Activity'}]}]
                );
            }
            else if (activity_type === 'activity_wait') {
                operatorData['properties']['fa_icon'] = 'fa fa-clock-o';
                operatorData['properties']['custom_class'] = 'flowchart-fcontrol-operator';
                self.create_inputs(operatorData, ['']);
                self.create_outputs(operatorData, [
                    {'label': '', 'sublinks': [{text: 'Wait'}]}]
                );
            }
            else if (activity_type === 'domain_rules') {
                operatorData['properties']['fa_icon'] = 'fa fa-circle-o-notch';
                operatorData['properties']['custom_class'] = 'flowchart-domain-operator';
                self.create_inputs(operatorData, ['']);
                self.create_outputs(operatorData, [
                    {'label': '', 'sublinks': [{text: 'Yes'}, {text: 'No'}]}]
                );
            } else if (activity_type === 'activity_start') {
                operatorData['properties']['fa_icon'] = 'fa fa-star';
                operatorData['properties']['custom_class'] = 'flowchart-event-operator';
                self.create_inputs(operatorData, ['']);
                self.create_outputs(operatorData, [
                    {'label': '', 'sublinks': [{text: 'Trigger'}]}]
                );
            }
            self.$flowChart.flowchart('createOperator', operatorId, operatorData);
        },

        disable_flectra_sidebar: function () {
            $('#f_menu_toggle').addClass('fl-sidebar-disable');
            $('#f_user_toggle').addClass('fl-sidebar-disable');
            $('#f_apps_search').addClass('fl-sidebar-disable');
            $('.f_launcher').addClass('f_launcher_close fl-sidebar-disable');
        },

        enable_flectra_sidebar: function () {
            $('#f_menu_toggle').removeClass('fl-sidebar-disable');
            $('#f_user_toggle').removeClass('fl-sidebar-disable');
            $('#f_apps_search').removeClass('fl-sidebar-disable');
            $('.f_launcher').removeClass('f_launcher_close fl-sidebar-disable');
        },

        destroy: function () {
            this._super.apply(this, arguments);
            this.enable_flectra_sidebar();
        }

    });

    core.action_registry.add('flow_chart_main', flow_chart_main);
    return flow_chart_main;
});