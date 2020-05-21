flectra.define('fl_pos_custom.customer', function(require) {
"use strict";

    var models = require('point_of_sale.models');
    models.load_fields('res.company', ['state_id']);

    models.load_models({
        model:  'res.country.state',
        fields: ['name'],
        loaded: function(self,states){
            self.states = states;
            self.company.state = null;
            for (var i = 0; i < states.length; i++) {
                if (states[i].id === self.company.state_id[0]){
                    self.company.state = states[i];
                }
            }
        },
    });
});