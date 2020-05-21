# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class ActivityWaiting(models.Model):
    _name = 'mail.activity.waiting'
    activity_id = fields.Many2one('mail.marketing.activity',
                                  string='Mail activity')
    destination_id = fields.Many2one('mail.marketing.activity',
                                     string='Destination Mail activity')
    rule_id = fields.Many2one('mail.activity.rules',
                              string='Activity Rules')
    wait_for = fields.Integer('Wait for', default=1)
    waiting_type = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('day', 'Day'),
         ('week', 'Week'),
         ('month', 'Month')], string='Waiting Type', default='hours')
    conditional_option = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                          string='Option')
    action_type = fields.Selection(
        [('email_open', 'Email Opened'), ('child_activity', 'Child Activity'),
         ('send_mail', 'Send mail'), ('email_not_open', 'Email Not Opened'),
         ('email_replied', 'Email Replied'),
         ('email_not_replied', 'Email Not Replied'),
         ('email_click', 'Email Clicked'),
         ('email_not_click', 'Email Not Clicked'),
         ('email_bounced', 'Email Bounced')], string='Action Type',
        default='send_mail')
