# Part of Flectra See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

import pytz
from dateutil.relativedelta import relativedelta
from flectra import api, fields, models


class MailMailStats(models.Model):
    _inherit = 'mail.mail.statistics'

    member_activity_id = fields.Many2one('member.activity',
                                         string='Members Activity')

    def convert_datetime_with_utc(self, date):
        if date:
            user_tz = pytz.timezone(
                self.env.context.get('tz') or self.env.user.tz or 'UTC')
            return fields.Datetime.from_string(date).replace(
                tzinfo=pytz.utc).astimezone(user_tz)

    def calculate_schedule_date(self, activity):
        current_date = datetime.now()
        schedule_time = False
        if activity.waiting_type == 'month':
            schedule_time = current_date + relativedelta(
                month=activity.wait_for)
        elif activity.waiting_type == 'week':
            schedule_time = current_date + timedelta(
                weeks=activity.wait_for)
        elif activity.waiting_type == 'day':
            schedule_time = current_date + timedelta(
                days=activity.wait_for)
        elif activity.waiting_type == 'hours':
            schedule_time = current_date + timedelta(
                hours=activity.wait_for)
        elif activity.waiting_type == 'minutes':
            schedule_time = current_date + timedelta(
                minutes=activity.wait_for)
        return schedule_time

    @api.model
    def create(self, vals):
        if vals.get('mass_mailing_id') and self.env.context.get('activity_id'):
            vals.update(
                {'member_activity_id': self.env.context.get('activity_id')})
        return super(MailMailStats, self).create(vals)

    def set_opened(self, mail_mail_ids=None, mail_message_ids=None):
        member_activity_obj = self.env['member.activity']
        statistics = super(MailMailStats, self).set_opened(
            mail_mail_ids, mail_message_ids)
        activities = member_activity_obj.search(
            [('state', '=', 'in_progress'),
             ('action_type', 'in', ['email_open', 'email_not_open']),
             ('schedule_date', '=', False)])
        for activity in activities:
            activity.schedule_date = self.calculate_schedule_date(activity)
        return statistics

    def set_clicked(self, mail_mail_ids=None, mail_message_ids=None):
        member_activity_obj = self.env['member.activity']
        statistics = super(MailMailStats, self).set_clicked(
            mail_mail_ids, mail_message_ids)
        activities_click = member_activity_obj.search(
            [('state', '=', 'in_progress'),
             ('action_type', 'in', ['email_click', 'email_not_click']),
             ('schedule_date', '=', False)])
        for activity in activities_click:
            activity.schedule_date = self.calculate_schedule_date(activity)
        return statistics

    def set_replied(self, mail_mail_ids=None, mail_message_ids=None):
        member_activity_obj = self.env['member.activity']
        statistics = super(MailMailStats, self).set_replied(
            mail_mail_ids, mail_message_ids)
        activities_receive = member_activity_obj.search(
            [('state', '=', 'in_progress'),
             ('action_type', 'in', ['email_replied', 'email_not_replied']),
             ('schedule_date', '=', False)])
        for activity in activities_receive:
            activity.schedule_date = self.calculate_schedule_date(activity)
        return statistics

    def set_bounced(self, mail_mail_ids=None, mail_message_ids=None):
        member_activity_obj = self.env['member.activity']
        statistics = super(MailMailStats, self).set_bounced(
            mail_mail_ids, mail_message_ids)
        activities_bounced = member_activity_obj.search(
            [('state', '=', 'in_progress'),
             ('action_type', '=', 'email_bounced'),
             ('schedule_date', '=', False)])
        for activity in activities_bounced:
            activity.schedule_date = self.calculate_schedule_date(activity)
        return statistics
