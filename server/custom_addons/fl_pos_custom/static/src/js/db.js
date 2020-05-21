flectra.define('fl_pos_custom.db', function (require) {
"use strict";

    var PosDB = require('point_of_sale.DB');
    var core = require('web.core');

    PosDB.include({
        add_partners: function(partners){
            var updated_count = this._super(partners);
            if (updated_count) {
                for (var id in this.partner_by_id) {
                    var partner = this.partner_by_id[id];
                    partner.address = (partner.street || '') +', '+
                                      (partner.zip || '')    +' '+
                                      (partner.city || '')   +', '+
                                      (partner.state_id ? partner.state_id[1] + ', ': '') +
                                      (partner.country_id[1] || '');
                }
            }
            return updated_count;
        },
    });
    return PosDB;
});
