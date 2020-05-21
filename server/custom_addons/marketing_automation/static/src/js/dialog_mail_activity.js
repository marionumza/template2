flectra.define('MarketingAutomation.DialogMailMarketing', function (require) {
    'use strict';

    var Dialog = require('web.Dialog');
    var DomainSelectorDialog = require("web.DomainSelectorDialog");
    var Domain = require("web.Domain");
    var rpc = require("web.rpc");
    var core = require("web.core");
    var qweb = core.qweb;

    return Dialog.extend({
        template: 'marketing_automation.MailMarketingFields',
        events: {
            'change #model_id': 'onModelChange',
            'click .domain_builder': 'onDomainBuilder'
        },
        init: function (parent, $draggable) {
            this._super(parent);
            this.parent = parent;
            this.$draggable = $draggable;
            this.activity_type = this.$draggable.attr('activity_type');
            this.marketing_type = this.$draggable.attr('marketing_type');
            this.options = {};
            var params = {
                title: 'Create Activity',
                size: 'medium',
                buttons: [{
                    text: "Create",
                    classes: 'btn-primary',
                    click: this._onSave.bind(this)
                }, {
                    text: "Close",
                    close: true
                }]
            };
            if (this.activity_type === 'send_mail') {
                params.buttons.splice(1, 0, {
                    text: 'Edit Mail Template',
                    classes: 'btn-primary',
                    click: this._onMailTemplateEdit.bind(this)
                });
            }
            this._super(parent, params);
        },
        _fetch_data: function (model_name, domain) {
            var self = this;
            var def = self._rpc({
                model: model_name,
                method: 'search_read',
                domain: domain
            });
            return def;
        },
        _onMailTemplateEdit: function (ev) {
            var self = this;
            var mail_template = self.$el.find('#mass_mailing_id').select2('data') || false;
            var model_id = self.$el.find('#model_id').select2('data');
            if (!mail_template || !model_id) {
                self.do_notify('Select Mail Template');
                return;
            }
            if (mail_template.id === 'is_new') {
                rpc.query({
                    model: 'mail.mass_mailing',
                    method: "create",
                    args: [{
                        name: mail_template.text,
                        mailing_model_id: model_id.id,
                        marketing_automation: true
                    }]
                }).done(function (id) {
                    self.edit_mail_template(id);
                });
            }
            else if (mail_template.id) {
                self.edit_mail_template(mail_template.id);
            }
        },

        edit_mail_template: function (id) {
            var self = this;
            self.do_action({
                target: 'new',
                type: 'ir.actions.act_url',
                url: 'web#id=' + id + '&view_type=form&model=mail.mass_mailing'
            });
        },

        start: function () {
            var self = this;
            self._fetch_data('marketing.config', []).then(function (val) {
                var data = [];
                var model = self.activity_type === 'send_mail' ? [['model', '=', ['crm.lead',
                    'event.registration',
                    'hr.applicant',
                    'res.partner',
                    'event.track',
                    'sale.order',
                    'mail.mass_mailing.list']]] : [];
                self._fetch_data('ir.model', model).then(function (vals) {
                    _.each(vals, function (e) {
                        data.push({id: e.id, text: e.display_name, model: e.model});
                    });
                    self.$el.find('#model_id').select2({
                        placeholder: 'Select Model',
                        data: data
                    });
                });
            });

        },
        onModelChange: function () {
            var self = this;
            var data = self.$el.find('#model_id').select2('data');
            var d = [], model, placeholder, el;
            if (self.activity_type === 'domain_rules') {
                $('button.domain_builder').parent().parent().removeClass('hidden');
                $('button.domain_builder').parent().parent().next().removeClass('hidden');
                return;
            }
            if (self.activity_type === 'send_mail') {
                d = [['mailing_model_id', '=', data.model], ['marketing_automation', '=', true]];
                model = 'mail.mass_mailing';
                el = '#mass_mailing_id';
                placeholder = 'Select Mail Template';
            }
            else if (self.activity_type === 'action') {
                d = [['model_id', '=', data.model]];
                model = 'ir.actions.server';
                el = '#action';
                placeholder = 'Select Server Action';
            }
            self.fetch_data(d, model, placeholder, el);
        },
        fetch_data: function (d, model, placeholder, el) {
            var self = this;
            self._fetch_data(model, d).then(function (vals) {
                var data = [];
                _.each(vals, function (e) {
                    data.push({id: e.id, text: e.display_name});
                });
                self.$el.find(el).select2({
                    createSearchChoice: function (term, d) {
                        if ($(d).filter(function () {
                            return this.text.localeCompare(term) === 0;
                        }).length === 0) {
                            return {id: 'is_new', text: term};
                        }
                    },
                    placeholder: placeholder,
                    allowClear: true,
                    data: data
                });
            });
        },

        check_validation: function (activity_type) {
            var self = this;
            if (activity_type === 'send_mail') {
                var name = self.$el.find('#name').val();
                var model_id = self.$el.find('#model_id').select2('data') || false;
                var mail_template = self.$el.find('#mass_mailing_id').select2('data') || false;
                if (name && model_id) {
                    if (!self.$el.find('#mass_mailing_id').hasClass('select2-offscreen')) {
                        return false;
                    }
                    if (!mail_template) {
                        return false;
                    }
                } else {
                    return false;
                }
            } else if (activity_type === 'action') {
                var name = self.$el.find('#name').val();
                var model_id = self.$el.find('#model_id').select2('data') || false;
                var action = self.$el.find('#action').select2('data') || false;
                if (name && model_id) {
                    if (!self.$el.find('#action').hasClass('select2-offscreen')) {
                        return false;
                    }
                    if (!action) {
                        return false;
                    }
                } else {
                    return false;
                }
            }
            else if (activity_type === 'domain_rules') {
                var model_id = self.$el.find('#model_id').select2('data') || false;
                var domain_value = self.$el.find('#domain_value').length || false;
                if (!model_id) {
                    return false;
                }
                if (domain_value) {
                    if (!self.$el.find('#domain_value').val()) {
                        return false;
                    }
                }
            }
            return true;
        },

        _onSave: function () {
            var self = this;
            var name = self.$el.find('#name').val();
            var model_id = self.$el.find('#model_id').select2('data');
            var mail_template = self.$el.find('#mass_mailing_id').select2('data') || false;
            var server_action = self.$el.find('#action').select2('data') || false;
            var wait_for_int = self.$el.find('#wait_for').val();
            var wait_for_type = self.$el.find('#waiting_type').val();
            var domain = self.$el.find('#domain_value').val();
            var valid = self.check_validation(self.activity_type);

            if (valid) {
                var data = {
                    name: name,
                    activity_type: self.activity_type,
                    marketing_type: self.marketing_type,
                    action: server_action,
                    model_id: model_id.id,
                    mail_template: mail_template,
                    wait_for: wait_for_int,
                    waiting_type: wait_for_type,
                    domain: domain
                };
                if (self.activity_type === 'send_mail') {
                    delete data['server_action'];
                    delete data['wait_for'];
                    delete data['waiting_type'];
                }
                else if (self.activity_type === 'action') {
                    delete data['mail_template'];
                }
                else if (self.activity_type === 'activity_wait') {
                    data['name'] = 'Wait For ' + data['wait_for'] + ' ' + data['waiting_type'];
                    delete data['marketing_type'];
                    delete data['action'];
                    delete data['server_action'];
                    delete data['model_id'];
                    delete data['mail_template'];
                }
                else if (self.activity_type === 'domain_rules') {
                    data['name'] = 'When ' + data['domain'];
                    data['mapping_field'] = $('.mapping_section').find('input:checked').val() || false;
                    delete data['marketing_type'];
                    delete data['action'];
                    delete data['server_action'];
                    delete data['mail_template'];
                    delete data['wait_for'];
                    delete data['waiting_type'];
                }
                self.trigger('create_record', data);
                self.close();
            }
        },

        onDomainBuilder: function (ev) {
            ev.preventDefault();
            var self = this;
            var $input = self.$el.find('#domain_value');
            var data = self.$el.find('#model_id').select2('data');
            var dialog = new DomainSelectorDialog(this, data.model, $input.val(), {
                readonly: false
            }).open();
            dialog.on("domain_selected", this, function (e) {
                $input.val(Domain.prototype.arrayToString(e.data.domain)).change();
                var f_arr = $.map(e.data.domain, function (e) {
                    if (e instanceof Array)
                        return e[0];
                });
                var $mapped = $(qweb.render('marketing_automation.mapping_radios', {
                    f_arr: f_arr
                }));
                $input.parent().parent().parent().next().html('');
                $input.parent().parent().parent().next().append($mapped);
                $mapped.find('input').first().attr('checked', true);
            });
        }
    })

});