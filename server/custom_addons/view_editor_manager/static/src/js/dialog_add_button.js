flectra.define('view_editor_manager.AddButtonDialog', function (require) {
    "use strict";
    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');
    var FA_ICONS = [];
    var set_icon = false;
    return Dialog.extend({
        init: function (parent, model) {
            this.model = model;
            this.active = 1;
            var options = {
                title: 'Add A Button',
                size: 'large',
                buttons: [
                    {
                        text: "save",
                        classes: 'btn-success',
                        click: _.bind(this.store_reserve, this)
                    },
                    {text: "Cancel", classes: 'btn-danger', close: true}
                ]
            };
            this._super(parent, options);
        },
        start: function () {
            var self = this, data = [], fields = [];
            FA_ICONS = [];
            var icons = $.getJSON("/view_editor_manager/static/lib/fontawesome/fa_icons.json", function (d) {
                $.each(d, function (key, val) {
                    data.push(key);
                });
                FA_ICONS = data;
            });

            self.$el.append($('<div class="col-md-12 mt8">').append($('<label>').text('Button Position'))
                .append($('<select id="input_slection_position">')
                    .append($('<option>').attr('id', 'inside').text('Inside'))
                    .attr('class', 'col-md-12 form-control')
                ));

            self.$el.append($('<div class="col-md-12 mt8">').append($('<label>').text('Button Label')).append($('<input ' +
                'id="input_text_field_id" ' +
                'placeholder="Button Text">').attr('class', 'col-md-12 form-control')
            ));

            icons.then(function () {
                var el = self.$el.append($('<div class="col-md-12 mt8">')
                    .append($('<div id="icon_container">')
                        .append($('<label>').text('Icons'))
                        .append($('<div id="fa_icon_picker" class="col-md-12">'))
                    ));
                el.find('#fa_icon_picker').iconpicker({
                    icons: FA_ICONS,
                    placement: 'inline',
                    animation: true,
                    selectedCustomClass: 'bg-primary'
                });
                el.find('.iconpicker-popover').css({'width': '100%'});
                self.$el.append($('<div class="col-md-12 mt8">').append($('<label>').text('Relation')).append($('<input ' +
                    'id="input_relation_field_m2o" >').attr('class', 'col-md-12')
                ));

                rpc.query({
                    model: 'ir.model.fields',
                    method: 'search_read',
                    domain: [['relation', '=', self.model], ['ttype', '=', 'many2one']]
                }).then(function (resp) {
                    _.each(resp, function (e) {
                        fields.push({
                            id: e.id,
                            text: e.field_description,
                            field_name: e.name
                        })
                    });
                    $('#input_relation_field_m2o').select2({
                        placeholder: 'Relational fields',
                        data: fields,
                        multiple: false,
                        value: []
                    });
                });
                el.find('#fa_icon_picker').on('iconpickerSelected', function (ev) {
                    set_icon = ev.iconpickerValue || false;
                });
            });

        },

        store_reserve: function () {
            var self = this;
            var options = {};
            var position = self.$el.find('#input_slection_position option:selected').attr('id');
            var btn_name = self.$el.find('#input_text_field_id').val();
            var selected_icon = set_icon;
            var relation_field = self.$el.find('#input_relation_field_m2o').select2('data');
            if (position && btn_name && selected_icon && relation_field) {
                options.position = position;
                options.btn_name = btn_name;
                options.icon = selected_icon.replace(/fa /g, '');
                options.field_name = self.$el.find('#input_relation_field_m2o').select2('data').field_name;
                options.rel_id = relation_field.id;
                self.trigger('save_button_info', options);
                self.close();
            } else {
                Dialog.alert(this, 'Please Input Data To Fields');
                return 0;
            }
        }
    });

});