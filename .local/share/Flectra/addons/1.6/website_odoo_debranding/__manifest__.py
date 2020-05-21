# Copyright 2016 Tecnativa, S.L. - Vicent Cubells
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Remove flectra.com bindings on website",
    "version": "1.0.1.0.0",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://gitlab.com/flectra-community/website",
    "license": "LGPL-3",
    "category": "Website",
    "depends": [
        'website',
    ],
    "data": [
        "templates/disable_flectra.xml",
    ],
    "installable": True,
}
