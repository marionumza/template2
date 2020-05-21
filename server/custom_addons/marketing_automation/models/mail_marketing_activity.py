# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class MailMarketingActivity(models.Model):
    _name = 'mail.marketing.activity'

    def _default_domain(self):
        return \
            self.mail_marketing_id and self.mail_marketing_id.domain or False

    def _compute_waiting_time(self):
        for activity in self:
            activity.waiting_time = 0

    name = fields.Char('Name')
    activity_id = fields.Many2one('mail.marketing.activity',
                                  ondelete="cascade",
                                  string='Mail activity')
    waiting_id = fields.Many2one('mail.activity.waiting',
                                 ondelete="cascade",
                                 string='Activity Waiting')
    rule_id = fields.Many2one('mail.activity.rules', ondelete="cascade",
                              string='Rule')
    domain = fields.Char(string='Domain', related='rule_id.domain',
                         default="[]", store=True)
    conditional_option = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                          string='Option')
    wait_for = fields.Integer('Wait Time', related='waiting_id.wait_for')
    waiting_type = fields.Selection(
        [('hours', 'Hours'), ('minutes', 'Minutes'), ('day', 'Day'),
         ('week', 'Week'),
         ('month', 'Month')], related='waiting_id.waiting_type',
        string='Waiting Type', default='hours')
    waiting_time = fields.Integer(string='Waiting Time',
                                  compute="_compute_waiting_time")
    activity_validity = fields.Boolean(string='Validity')
    activity_validity_time = fields.Integer(
        string='Validity Time')
    activity_validity_type = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('day', 'Day'),
         ('week', 'Week'),
         ('month', 'Month')], string='Validity Type', default='hours')
    mail_marketing_id = fields.Many2one('mail.marketing', ondelete="cascade",
                                        string='Mail Marketing')
    marketing_config_id = fields.Many2one(
        'marketing.config',
        related="mail_marketing_id.marketing_config_id",
        store=True,
        string='Marketing')
    model_id = fields.Many2one('ir.model', string='Model')
    ir_actions_server_id = fields.Many2one(
        'ir.actions.server', 'Server action')
    mass_mailing_id = fields.Many2one('mail.mass_mailing',
                                      string='Mail Template')
    marketing_type = fields.Selection(
        [('send_mail', 'Send mail'),
         ('action', 'Server Action')])

    action_type = fields.Selection(
        [('email_open', 'Email Opened'),
         ('child_activity', 'Child Activity'),
         ('send_mail', 'Send mail'),
         ('email_not_open', 'Email Not Opened'),
         ('email_replied', 'Email Replied'),
         ('email_not_replied', 'Email Not Replied'),
         ('email_click', 'Email Clicked'),
         ('email_not_click', 'Email Not Clicked'),
         ('email_bounced', 'Email Bounced')], string='Action Type',
        default='send_mail')
    parent_id = fields.Many2one('mail.marketing.activity', ondelete="cascade",
                                string='Parent mail activity')
    child_line = fields.One2many('mail.marketing.activity',
                                 'parent_id',
                                 string='Child mail activity')
    state = fields.Selection([('new', 'New'), ('in_progress', 'In Progress'),
                              ('completed', 'Completed'), ('canceled',
                                                           'Canceled')],
                             default='new',
                             string='Status')
    sent_count = fields.Integer(string='Sent', compute='_compute_total_count')
    clicked_count = fields.Integer(string='Clicked',
                                   compute='_compute_total_count')
    replied_count = fields.Integer(string='Replied',
                                   compute='_compute_total_count')
    opened_count = fields.Integer(string='Opened',
                                  compute='_compute_total_count')
    bounced_count = fields.Integer(string='Bounced',
                                   compute='_compute_total_count')
    exception_count = fields.Integer(string='Exception',
                                     compute='_compute_total_count')

    @api.multi
    def _compute_total_count(self):
        for object in self:
            activities = self.env['member.activity'].search(
                [('mail_activity_id', '=', object.id)])
            total_list = ['sent', 'clicked', 'replied', 'opened', 'bounced',
                          'exception']
            vals = {el: 0 for el in total_list}
            for statistic in activities.mapped('statistics_ids'):
                double_dict1 = {k: v + 1 for (k, v) in vals.items() if
                                getattr(statistic, k, False)}
                vals.update(double_dict1)
            object.sent_count = vals.get('sent')
            object.clicked_count = vals.get('clicked')
            object.replied_count = vals.get('replied')
            object.opened_count = vals.get('opened')
            object.bounced_count = vals.get('bounced')
            object.exception_count = vals.get('exception')

    @api.multi
    def get_mail_status_statistics(self):
        self.ensure_one()
        form_id = self.env.ref(
            'mass_mailing.view_mail_mail_statistics_form').id
        tree_id = self.env.ref(
            'mass_mailing.view_mail_mail_statistics_tree').id
        res = {
            'name': _('Mail Statistics'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'mail.mail.statistics',
            'type': 'ir.actions.act_window',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'view_id': False,
        }
        activities = self.env['member.activity'].search(
            [('mail_activity_id', 'in', self.ids)])
        if activities:
            res.update({'domain': [('member_activity_id', 'in',
                                    activities.ids or [])]})
        return res

    @api.onchange('mail_marketing_id')
    def onchange_mail_marketing_id(self):
        for activity in self:
            if activity.mail_marketing_id:
                activity.domain = activity.mail_marketing_id.domain
