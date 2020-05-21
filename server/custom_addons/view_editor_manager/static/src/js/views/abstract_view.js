flectra.define('view_editor_manager.AbstractView', function (require) {
    "use strict";
    var AbstractView = require('web.AbstractView');
    var ajax = require('web.ajax');

    return AbstractView.include({

        init: function () {
            this._super.apply(this, arguments);
        },
        CreateBuilderEditor: function (P, R, O) {
            var self = this;
            var defViews = self._loadSubviews(P)
            return defViews.then(function () {
                return self.RenderViewFromParams(P, R, O);
            });
        },
        RenderViewFromParams: function (P, R, O) {
            var self = this;
            var Defs = $.when(
                self._loadData(P),
                ajax.loadLibs(self)
            );
            return Defs.then(function (id) {
                return self.setView(id, P, R, O)
            });
        },
        setView: function (id, P, R, O) {
            var self = this;
            var m = self.getModel();
            var s = m.get(id);
            var p = _.extend({}, self.rendererParams, O);
            var r = new R(P, s, p);
            m.setParent(r);
            return r;
        }
    })

});