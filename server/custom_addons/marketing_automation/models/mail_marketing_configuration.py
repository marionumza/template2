# Part of Flectra See LICENSE file for full copyright and licensing details.
from flectra import fields, models


class MarketingConfig(models.Model):
    _name = 'marketing.config'
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model', string='Model')
    field_id = fields.Many2one('ir.model.fields', string='Field',
                               domain="[('model_id', '=', model_id)]")
    child_line = fields.One2many('marketing.config.line', 'parent_id',
                                 string='Marketing Config Line')


class MarketingConfigLine(models.Model):
    _name = 'marketing.config.line'
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model', string='Model', change_default=True)
    field_id = fields.Many2one('ir.model.fields', string='Field',
                               domain="[('model_id', '=', model_id)]")
    parent_id = fields.Many2one('marketing.config', string='Config',
                                change_default=True)
