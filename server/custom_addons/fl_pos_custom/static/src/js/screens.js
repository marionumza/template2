flectra.define('fl_pos_custom.screens', function(require) {
"use strict";

    var core = require('web.core');
    var screens = require('point_of_sale.screens');

    screens.ClientListScreenWidget.include({
        show: function(){
            this._super.apply(this, arguments);
            var self = this;
            this.$('.new-customer').click(function(){
                self.display_client_details('edit',{
                    'state_id': self.pos.company.state_id,
                    'country_id': self.pos.company.country_id,
                });
            });
        },
    });
});
