flectra.define('module_builder.FormController', function (require) {
    "use strict";
    var FormController = require('web.FormController');
    return FormController.include({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            var $res = self._super.apply(this, arguments);
            $res.done(function () {
                setTimeout(function () {
                    self.$el.find('input[name="shortdesc"]').focus();
                }, 10);
            });
        },
        autofocus: function () {
            var self = this;
            var $res = self._super.apply(this, arguments);
            setTimeout(function () {
                self.$el.find('input[name="shortdesc"]').focus();
            }, 10);
        },
        _onButtonClicked: function (event) {
            var self = this;
            this._super.apply(this, arguments);
            var attrs = event.data.attrs;
            if (attrs && attrs['class']) {
                if (attrs['class'].indexOf('rollback_model_for_me') > -1) {
                    self._rpc({
                        model: 'wizard.generate.app',
                        method: 'rollback',
                        args: [],
                    })
                }
            }
        }
    })
});
