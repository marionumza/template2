# -*- coding: utf-8 -*-

from flectra import api, fields, models,exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sales_order_type = fields.Selection([('Sales', 'Sales'), ('Service', 'Service')], string='Sales Order Type')
