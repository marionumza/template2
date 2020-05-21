# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class MailMember(models.Model):
    _name = 'mail.member'
    _rec_name = 'member'

    @api.model
    def get_records_selection(self):
        models = self.env['ir.model'].sudo().search([])
        return [(model.model, model.name) for model in models]

    def _compute_record_details(self):
        for obj in self:
            obj.member = self.env[obj.model_id.model].search(
                [('id', '=', obj.member_id)], limit=1)

    member_activity_line = fields.One2many('member.activity',
                                           'mail_member_id',
                                           string='Member Activity')
    member_id = fields.Integer(string='Record')
    member = fields.Reference(compute='_compute_record_details',
                              selection='get_records_selection',
                              string='Reference')
    schedule_date = fields.Datetime('Schedule Date')
    mail_marketing_id = fields.Many2one(
        'mail.marketing', string='Mail marketing', ondelete="cascade")
    marketing_config_id = fields.Many2one(
        'marketing.config',
        related="mail_marketing_id.marketing_config_id",
        store=True,
        string='Marketing')
    model_id = fields.Many2one('ir.model', string='Model',
                               related='mail_marketing_id.model_id')
