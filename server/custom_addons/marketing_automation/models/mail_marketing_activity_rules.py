# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class ActivityRules(models.Model):
    _name = 'mail.activity.rules'

    activity_id = fields.Many2one('mail.marketing.activity',
                                  string='Mail activity')
    mapping_field = fields.Char(string='Mapped Field')
    timmer_id = fields.Many2one('mail.activity.waiting',
                                string='Timmer')
    destination_true_id = fields.Many2one('mail.marketing.activity',
                                          string='Destination Mail activity')
    destination_false_id = fields.Many2one('mail.marketing.activity',
                                           string='Destination Mail activity')
    waiting_true_id = fields.Many2one('mail.activity.waiting',
                                      string='Destination Mail Timmer(Yes)')
    waiting_false_id = fields.Many2one('mail.activity.waiting',
                                       string='Destination Mail Timmer(No)')
    model_id = fields.Many2one('ir.model', string='Model', change_default=True)
    model_name = fields.Char(string='Model name', related='model_id.model')
    domain = fields.Char(string='Domain', default="[]")
    conditional_option = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string='Option')
    action_type = fields.Selection(
        [('email_open', 'Email Opened'), ('child_activity', 'Child Activity'),
         ('send_mail', 'Send mail'), ('email_not_open', 'Email Not Opened'),
         ('email_replied', 'Email Replied'),
         ('email_not_replied', 'Email Not Replied'),
         ('email_click', 'Email Clicked'),
         ('email_not_click', 'Email Not Clicked'),
         ('email_bounced', 'Email Bounced')], string='Action Type',
        default='send_mail')

    @api.model
    def create(self, vals):
        activity = super(ActivityRules, self).create(vals)
        if activity.destination_true_id:
            activity.destination_true_id.write({'domain': activity.domain})
        if activity.destination_false_id:
            activity.destination_false_id.write({'domain': activity.domain})
        return activity

    @api.multi
    def write(self, vals):
        activity = super(ActivityRules, self).write(vals)
        config = self.activity_id.marketing_config_id
        if self.domain:
            field_name = self.mapping_field
            field_obj = self.env['ir.model.fields'].search(
                [('name', '=', field_name),
                 ('model_id', '=', self.model_id.model)],
                limit=1)

        if config and field_obj:
            field_name = []
            if config.child_line:
                for child in config.child_line:
                    field_name.append(child.field_id)
                if field_obj not in field_name:
                    config.write(
                        {'child_line': [(0, 0,
                                         {'model_id': field_obj.model_id.id,
                                          'field_id': field_obj.id})]})
            else:
                config.write(
                    {'child_line': [(0, 0, {'model_id': field_obj.model_id.id,
                                            'field_id': field_obj.id})]})

        if self.destination_true_id or vals.get('domain', False):
            self.destination_true_id.write({'domain': self.domain})
        if self.destination_false_id or vals.get('domain', False):
            self.destination_false_id.write({'domain': self.domain})
        return activity
