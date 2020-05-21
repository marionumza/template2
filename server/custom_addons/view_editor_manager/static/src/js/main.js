flectra.define('view_editor_manager.Main', function (require) {
    "use strict";
    var core = require('web.core');
    var Context = require('web.Context');
    var Dialog = require('web.Dialog');
    var DialogAddFields = require('view_editor_manager.DialogAddFields');
    var DialogPropertyInitializer = require('view_editor_manager.DialogPropertyInitializer');
    var DialogProperty = require('view_editor_manager.DialogProperty');
    var DialogButton = require('view_editor_manager.AddButtonDialog');
    var RendererEngine = require('view_editor_manager.ViewRendererEngine');
    var misc = require('view_editor_manager.Miscellaneous');
    var dom = require('web.dom');
    var Widget = require('web.Widget');

    var Main = Widget.extend({
        custom_events: {
            '_onNodeSelect': 'onNodeSelect',
            '_onKanbanRecord': 'onKanbanRecord',
            '_onPageSelect': 'onPageSelect',
            '_onColSelect': '_onColSelect',
            '_onAddStatButton': 'onAddStatButton',
            '_onAddPage': 'onAddPage',
            '_onUpdateCalendar': 'onUpdateCalendar',
        },
        init: function (parent, context, options) {
            this._super.apply(this, arguments);
            this.action = options.action;
            this.action_descr = options.action_desc;
            this.active_view = options.active_view;
            this.view_env = options.view_env;
            this.systray = options.systray;
        },
        start: function () {
            var self = this, options = {};
            options.load_filter = true;
            var views = this.action_descr.views.slice();
            var search_view_id = self.action_descr.search_view_id && this.action_descr.search_view_id[0];
            views.push([search_view_id || false, 'search']);
            var context = new Context(_.extend({}, this.action_descr.context));
            var view_def = this.loadViews(this.action_descr.res_model, context, views, options);
            var view = _.find(views, function (el) {
                return el[1] === self.active_view;
            });
            self.view_id = view && view[0];
            if (!self.view_id) {
                _.each(self.action.widget.view_order, function (e, i) {
                    if (e['type'] === self.active_view) {
                        self.view_id = e.fields_view.view_id;
                    }
                })
            }

            view_def.then(function (fields_view) {
                if (!self.view_id) {
                    var v = fields_view[self.active_view];
                    self.view_id = v && v['view_id'];
                    if (!self.view_id) {
                        self.do_notify('View', 'Not Found');
                        return;
                    }
                }
                var options = {
                    action: self.action,
                    fields_view: fields_view,
                    active_view: self.active_view,
                    view_env: self.view_env
                };
                self.fields_view = fields_view[self.active_view];
                var engine = new RendererEngine(self, options);
                engine.start_engine().done(function (res) {
                    var fragment = document.createDocumentFragment();
                    res.appendTo(fragment).then(function () {
                        dom.append(self.$el, [fragment], {
                            in_DOM: true,
                            callbacks: []
                        });
                    });
                }).fail(function (res) {
                    self.do_notify('View Editor', res);
                    setTimeout(function () {
                        self.systray.reset_everything($('#view_editor_toggle'));
                    }, 500);
                });
            });
        },
        _onColSelect: function (ev) {
            var $target = ev.data.current;
            var node = ev.data.node;
            if (!node) {
                return;
            }
            $('td,th').removeClass('view_editor_element_col_selected');
            this.$el.find('.table_controls').remove();
            this.$el.find('.p_controls').remove();
            $('td:nth-child(' + ($target.index() + 1) + ')').addClass('view_editor_element_col_selected');
            $('th:nth-child(' + ($target.index() + 1) + ')').addClass('view_editor_element_col_selected');
            var $nodeAdd = $('<span class="p_controls">').append('<i class="fa fa-plus">');
            var $nodeProp = $('<span class="p_controls">').append('<i class="fa fa-cogs">');
            var $nodeDelete = $('<span class="p_controls">').append('<i class="fa fa-trash">');
            $target.append($('<span>').addClass('table_controls').append($nodeAdd).append($nodeProp).append($nodeDelete));
            $nodeAdd.bind('click', {node: node, widget: this}, this.onAddNode);
            $nodeProp.bind('click', {node: node, widget: this}, this.onPropNode);
            $nodeDelete.bind('click', {node: node, widget: this}, this.onDeleteNode);
        },
        onPageSelect: function (ev) {
            var $target = ev.data.current;
            var node = ev.data.node;
            this.$el.find('.view_editor_element_selected').removeClass('view_editor_element_selected');
            this.$el.find('.page_controls').remove();
            this.$el.find('.p_controls').remove();
            $target.addClass('view_editor_element_selected');
            var $nodeProp = $('<span class="p_controls">').append('<i class="fa fa-cogs">');
            var $nodeDelete = $('<span class="p_controls">').append('<i class="fa fa-trash">');
            $target.find('a').append($('<span>').addClass('page_controls').append($nodeProp).append($nodeDelete));
            $nodeProp.bind('click', {node: node, widget: this}, this.onPropNode);
            $nodeDelete.bind('click', {node: node, widget: this}, this.onDeleteNode);
        },
        onKanbanRecord: function (ev) {
            var $target = ev.data.current;
            var node = ev.data.node;
            var $nodeAdd = $('<span class="p_controls">').append('<span class="fa fa-plus">');
            var $nodeProp = $('<span class="p_controls">').append('<span class="fa fa-cogs">');
            var $nodeDelete = $('<span class="p_controls">').append('<span class="fa fa-trash">');
            this.$el.find('.view_editor_kanban_element_selected').removeClass('view_editor_kanban_element_selected');
            this.$el.find('.p_controls').remove();
            $target.addClass('view_editor_kanban_element_selected');
            $target.append($nodeAdd);
            $target.append($nodeProp);
            $target.append($nodeDelete);
            $nodeAdd.bind('click', {node: node, widget: this}, this.onAddNode);
            $nodeProp.bind('click', {node: node, widget: this}, this.onPropNode);
            $nodeDelete.bind('click', {node: node, widget: this}, this.onDeleteNode);
        },
        onNodeSelect: function (ev) {
            var $target = ev.data.current;
            var node = ev.data.node;
            var $nodeAdd = $('<td class="p_controls">').append('<span class="fa fa-plus">');
            var $nodeProp = $('<td class="p_controls">').append('<span class="fa fa-cogs">');
            var $nodeDelete = $('<td class="p_controls">').append('<span class="fa fa-trash">');
            this.$el.find('.view_editor_element_selected').removeClass('view_editor_element_selected');
            this.$el.find('.p_controls').remove();
            $target.addClass('view_editor_element_selected');
            $target.append($nodeAdd);
            $target.append($nodeProp);
            $target.append($nodeDelete);
            $nodeAdd.bind('click', {node: node, widget: this}, this.onAddNode);
            $nodeProp.bind('click', {node: node, widget: this}, this.onPropNode);
            $nodeDelete.bind('click', {node: node, widget: this}, this.onDeleteNode);
        },
        onAddPage: function (ev) {
            var self = this;
            var children = ev.data.node.children;
            var node = children[children.length - 1];
            var model = self.action_descr.res_model;
            self.fields_in_view = self.fields_view.fields;
            self.fields_not_in_view = _.omit(self.fields_in_view, Object.keys(self.fields_view.fieldsInfo[self.active_view]));
            var dialog_add_fields = new DialogAddFields(self, model, node, self.fields_in_view, self.fields_not_in_view).open();
            dialog_add_fields.on('update_arch', self, function (options) {
                options.view_id = self.view_id;
                options.xpath_type = options.tag;
                options.notebook_count = ev.data.current.attr('notebook_count');
                misc.update_view(options).then(function (resp) {
                    if (resp)
                        self.restart();
                });
            });
        },
        onAddStatButton: function (ev) {
            var node = ev.data.node;
            var self = this;
            var model = self.action_descr.res_model;
            var dialog_smart_button = new DialogButton(self, model).open();
            dialog_smart_button.on('save_button_info', self, function (options) {
                options.view_id = self.view_id;
                options.field_operation = 'add_smart_button';
                options = _.extend(node, options);
                options.name = options.attrs.name;
                misc.update_view(options).then(function (resp) {
                    if (resp)
                        self.restart();
                });
            })
        },
        onAddNode: function (ev) {
            var node = ev.data.node;
            var self = ev.data.widget;
            var model = self.action_descr.res_model;
            self.fields_in_view = self.fields_view.fields;
            self.fields_not_in_view = _.omit(self.fields_in_view, Object.keys(self.fields_view.fieldsInfo[self.active_view]));
            var dialog_add_fields = new DialogAddFields(self, model, node, self.fields_in_view, self.fields_not_in_view).open();
            dialog_add_fields.on('update_arch', self, function (options) {
                options.view_id = self.view_id;
                options.xpath_type = options.tag;
                if (options.tag === 'field') {
                    var dialog = new DialogPropertyInitializer(self, model, options, self.fields_in_view, self.fields_not_in_view, self.fields_view.arch).open();
                    dialog.on('update_attribute', self, function (attributes) {
                        if (attributes['name']) {
                            options.xpath_field = attributes['name'];
                            delete attributes['name'];
                        }
                        options.name = options.attrs['name'];
                        options.attrs = _.extend({}, attributes);
                        delete options.attrs['name'];
                        misc.update_view(options).then(function (resp) {
                            if (resp)
                                self.restart();
                        });
                    });
                }
                else {
                    options.name = options.attrs['name'];
                    delete options.attrs['name'];
                    misc.update_view(options).then(function (resp) {
                        if (resp)
                            self.restart();
                    });
                }
            });
        },
        onPropNode: function (ev) {
            var node = ev.data.node;
            var self = ev.data.widget;
            var model = self.action_descr.res_model;
            self.fields_in_view = self.fields_view.fields;
            self.fields_not_in_view = _.omit(self.fields_in_view, Object.keys(self.fields_view.fieldsInfo[self.active_view]));
            var dialog = new DialogProperty(self, model, node, self.fields_in_view, self.fields_not_in_view, self.fields_view.arch).open();
            dialog.on('update_arch', this, function (options) {
                options.view_id = self.view_id;
                if (node.tag === 'page') {
                    options.field_operation = 'page';
                } else if (node.tag === 'filter') {
                    options.field_operation = 'filter';
                } else if (node.type === 'button') {
                    options.field_operation = 'button_attrs';
                } else if (node.type === 'group') {
                    options.field_operation = 'group_attrs';
                } else {
                    options.field_operation = 'existing_field';
                }
                options.xpath_field = options.name;
                options.xpath_type = 'field';
                options = _.extend(node, options);
                misc.update_view(options).then(function (resp) {
                    if (resp)
                        self.restart();
                });
            });
        },
        onDeleteNode: function (ev) {
            var node = ev.data.node;
            var self = ev.data.widget;
            Dialog.confirm(this, ("Are you sure you want to remove this item?"), {
                confirm_callback: function () {
                    var options = {};
                    options.view_id = self.view_id;
                    options.position = 'replace';
                    if (node.tag === 'page') {
                        options.field_operation = 'page';
                    } else if (node.tag === 'filter') {
                        options.field_operation = 'filter';
                    } else if (node.type === 'button') {
                        options.field_operation = 'button_attrs';
                    } else if (node.type === 'group') {
                        options.field_operation = 'group_attrs';
                    } else {
                        options.field_operation = 'existing_field';
                    }
                    options = _.extend(node, options);
                    options.name = options.attrs.name;
                    options.xpath_field = options.attrs.name;
                    options.xpath_type = 'field';
                    misc.update_view(options).then(function (resp) {
                        if (resp)
                            self.restart();
                    });
                }
            });
        },
        onUpdateCalendar: function (ev) {
            var self = this;
            var options = {};
            options.tag = 'calendar';
            options.view_id = self.view_id;
            options.position = 'attributes';
            options.field_operation = 'calendar';
            options.attrs = ev.data;
            misc.update_view(options).then(function (resp) {
                if (resp)
                    self.restart();
            });
        },
        restart: function () {
            var self = this;
            self.do_action('main', {
                action: self.action,
                action_desc: self.action_descr,
                view_env: self.view_env,
                active_view: self.active_view,
                view_type: self.active_view,
                no_state_change: true
            });
        },
        do_action: function (action, options) {
            return this._super.apply(this, arguments);
        },
        destroy: function () {
            this._super.apply(this, arguments);
            var systray = this.systray;
            if (systray)
                systray.reset_everything($('#view_editor_toggle'));
        }
    });

    core.action_registry.add('main', Main);

});
