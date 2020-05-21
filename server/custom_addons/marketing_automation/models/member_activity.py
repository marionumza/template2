# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class MemberActivity(models.Model):
    _name = 'member.activity'

    name = fields.Char('Name')
    mail_activity_id = fields.Many2one('mail.marketing.activity',
                                       string='Mail Activity')
    wait_for = fields.Integer(related='mail_activity_id.wait_for',
                              string='Wait for')
    waiting_type = fields.Selection(related='mail_activity_id.waiting_type',
                                    string='Waiting Type')
    marketing_type = fields.Selection(
        related='mail_activity_id.marketing_type',
        string='Mail Activity')
    action_type = fields.Selection(related='mail_activity_id.action_type',
                                   string='Activity Type')
    state = fields.Selection([('new', 'New'), ('in_progress', 'In Progress'),
                              ('completed', 'Completed'),
                              ('canceled', 'Canceled')], default='new',
                             string='Status')
    schedule_date = fields.Datetime('Schedule Date')
    parent_id = fields.Many2one('member.activity', ondelete="cascade",
                                string='Parent member activity')
    child_line = fields.One2many('member.activity', 'parent_id',
                                 'Member activity')
    mail_member_id = fields.Many2one('mail.member', ondelete="cascade",
                                     string='Mail member')
    mass_mailing_id = fields.Many2one('mail.mass_mailing',
                                      string='Mail Template')
    res_id = fields.Integer('Resource Id')
    statistics_ids = fields.One2many('mail.mail.statistics',
                                     'member_activity_id',
                                     string='Mail Statistics')
    rule_id = fields.Many2one('mail.activity.rules', ondelete="cascade",
                              string='Rule')
    marketing_config_id = fields.Many2one(
        'marketing.config',
        related="mail_activity_id.marketing_config_id",
        store=True,
        string='Marketing')
    model_id = fields.Many2one('ir.model', string='Model',
                               related='rule_id.model_id',
                               store=True, change_default=True)
    model_name = fields.Char(string='Model name',
                             related='model_id.model', store=True)
    domain = fields.Char(string='Domain', related='rule_id.domain', store=True)

    def execute_activity(self):
        marketing = self.mail_activity_id.mail_marketing_id
        self.state = 'in_progress'
        marketing.with_context(
            {'member_activity_id': self.id}).execute_marketing_activity_mails()
