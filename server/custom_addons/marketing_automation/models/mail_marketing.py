# Part of Flectra See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta

import pytz
import logging
from dateutil.relativedelta import relativedelta
from flectra import api, fields, models, _
from flectra.exceptions import ValidationError
from flectra.tools import DEFAULT_SERVER_DATETIME_FORMAT
from flectra.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class MailMarketing(models.Model):
    _name = 'mail.marketing'
    _inherit = 'mail.thread'

    activity_builder_data = fields.Char(string="Activity Builder Data")
    name = fields.Char(string='Name')
    marketing_config_id = fields.Many2one('marketing.config',
                                          ondelete="cascade",
                                          string='Model')
    model_id = fields.Many2one('ir.model',
                               related='marketing_config_id.model_id',
                               store=True, string='Model(Main)',
                               change_default=True)
    model_name = fields.Char(string='Model name',
                             related='model_id.model')
    domain = fields.Char(string='Domain', default="[]")
    rule_id = fields.Many2one('mail.activity.rules',
                              string='Rule')
    mail_activity_line = fields.One2many('mail.marketing.activity',
                                         'mail_marketing_id',
                                         string='Mail Activity')
    mail_member_line = fields.One2many('mail.member',
                                       'mail_marketing_id',
                                       string='Mail Member')
    state = fields.Selection([('new', 'New'), ('draft', 'Draft'),
                              ('in_progress', 'In Progress'),
                              ('completed', 'Completed')], default='new',
                             string='Status')
    member_count = fields.Integer(compute='_compute_total_members',
                                  string='Total Members')
    need_update = fields.Boolean('Needs Update')

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

    def get_marketing_stats_ratio(self, id=None):
        domain = [['id', '=', id]] if id else []
        records = self.search(domain)
        result = {}
        for obj_mail_marketing in records:
            result[obj_mail_marketing.id] = []
            for obj_mail_activity in obj_mail_marketing.mail_activity_line:
                mass_mailing_id = obj_mail_activity.mass_mailing_id
                if mass_mailing_id:
                    result[obj_mail_marketing.id].append({
                        'name': mass_mailing_id.name,
                        'sent': mass_mailing_id.received_ratio / 100,
                        'opened': mass_mailing_id.opened_ratio / 100,
                        'clicked': mass_mailing_id.clicks_ratio / 100,
                        'bounced': mass_mailing_id.bounced_ratio / 100,
                        'replied': mass_mailing_id.replied_ratio / 100,
                        'exception': mass_mailing_id.failed / 100})

        overall_statistic = self.calculate_overall_mail_statistics(result)
        return {
            'overall_statistics': overall_statistic or [],
            'results_per_campaign': result or []
        }

    def calculate_overall_mail_statistics(self, result):
        stat = {}
        for key, lst in result.items():
            total_mail = len(lst)
            stat[key] = []
            if lst:
                stat[key].append({
                    'sent_ratio': round((sum(
                        [d['sent'] for d in lst]) / total_mail) * 100, 2),
                    'opened_ration': round((sum(
                        [d['opened'] for d in
                         lst]) / total_mail) * 100, 2),
                    'clicked_ratio':
                        round((sum(
                            [d['clicked'] for d in
                             lst]) / total_mail) * 100, 2),
                    'bounced_ratio': round((sum(
                        [d['bounced'] for d in
                         lst]) / total_mail) * 100, 2),
                    'replied_ratio': round((sum(
                        [d['replied'] for d in
                         lst]) / total_mail) * 100, 2),
                    'exception_ratio': round((sum(
                        [d['exception'] for d in
                         lst]) / total_mail) * 100, 2)})
            else:
                stat[key].append({'sent_ratio': 0,
                                  'opened_ration': 0,
                                  'clicked_ratio': 0,
                                  'bounced_ratio': 0,
                                  'replied_ratio': 0,
                                  'exception_ratio': 0})
        return stat or False

    def get_email_counts(self, field_name, record, from_date, to_date):
        if len(record) < 1:
            return []
        if len(record) < 2:
            record = str(record).replace(',', '')
        if from_date and to_date:
            self.env.cr.execute(
                """SELECT COUNT(*), DATE({date_field})
                            FROM mail_mail_statistics WHERE {date_field}
                            IS NOT NULL AND mass_mailing_id IN
                            (SELECT ID FROM mail_mass_mailing
                            WHERE ID IN {ids} AND {date_field}
                            BETWEEN '{f_dt}' AND '{t_dt}' AND
                            marketing_automation=True)
                            GROUP BY DATE({date_field})""".format(
                    date_field=field_name,
                    f_dt=from_date,
                    t_dt=to_date,
                    ids=record))
        else:
            self.env.cr.execute("""SELECT COUNT(*), DATE({date_field})
                    FROM mail_mail_statistics WHERE {date_field}
                    IS NOT NULL AND mass_mailing_id
                    IN (SELECT ID FROM mail_mass_mailing
                    WHERE ID IN {ids} AND
                    marketing_automation=True)
                    GROUP BY DATE({date_field})""".format(
                date_field=field_name,
                ids=record))
        return self.env.cr.dictfetchall()

    def get_marketing_stats(self, id=None, from_date=None, to_date=None):
        domain = [['id', '=', id]] if id else []
        marketing_automation = self.search(domain)
        activity = self.env['mail.marketing.activity'].search(
            [['mail_marketing_id', 'in', marketing_automation.ids]])
        mass_mailing = tuple((act.mass_mailing_id.ids[0]) for act in
                             activity if len(act.mass_mailing_id.ids))
        field_names = ['sent', 'opened', 'replied', 'exception', 'clicked',
                       'bounced']
        result = []
        date_list = []
        final_result = {}
        j_list = []
        for field_name in field_names:
            for mail_counts in self.get_email_counts(
                    field_name, mass_mailing, from_date, to_date):
                counts = {}
                counts['date'] = mail_counts['date']
                counts[field_name] = mail_counts['count']
                result.append(counts)

        for k in result:
            if k.get('date', False) not in date_list:
                date_list.append(k['date'])
                final_result[k['date']] = k
            else:
                final_result[k['date']].update(k)
        for j, v in final_result.items():
            for name in field_names:
                if name not in v:
                    v.update({name: 0})
            j_list.append(v)
        return j_list or []

    @api.multi
    def _compute_total_count(self):
        for object in self:
            activities = self.env['member.activity'].search(
                [('mail_activity_id.mail_marketing_id', '=', object.id)])
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
    def write(self, vals):
        for object in self:
            if object.state != 'new' and vals.get('mail_activity_line'):
                vals.update({'need_update': True})
        return super(MailMarketing, self).write(vals)

    @api.multi
    def action_completed(self):
        for object in self:
            object.state = 'completed'

    def check_campaign_state(self):
        for object in self.env['mail.marketing'].search([]):
            mail_line = object.mapped('mail_activity_line')
            has_in_progress = \
                mail_line.filtered(lambda r: r.state != "completed")
            if not has_in_progress:
                object.state = 'completed'

    @api.multi
    def get_started(self):
        for obj in self:
            if not obj.mail_activity_line:
                raise ValidationError(_(
                    "At least one activity is must to start "
                    "Marketing Automation for this model"))
            obj.state = 'draft'

    @api.multi
    def _compute_total_members(self):
        for object in self:
            object.member_count = len(object.mail_member_line.ids)

    @api.multi
    def get_count(self):
        return len(self.mail_member_line.ids)

    @api.model
    def _confirm_mail_marketing(self):
        mail_marketing = self.env['mail.marketing'].search([])
        mail_marketing.create_marketing_members()

    @api.multi
    def create_marketing_members(self):
        member_obj = self.env['mail.member']
        current_time = datetime.now()
        for obj in self:
            partners = member_obj.search(
                [('mail_marketing_id', '=', obj.id)]).mapped('member_id')
            partner_ids = self.env[obj.model_name].search(safe_eval(
                obj.domain)).filtered(lambda s: s.id not in partners)
            for partner in partner_ids:
                vals = {
                    'member': partner.name,
                    'schedule_date': current_time,
                    'mail_marketing_id': obj.id,
                    'member_id': partner.id,
                }
                member_obj.create(vals)
            obj.create_member_activities()
            obj.state = 'in_progress'

    @api.multi
    def create_member_activities(self):
        member_activity_obj = self.env['member.activity']
        _activity, field_name = None, None
        if self.rule_id:
            obj_ids = self.env[self.rule_id.model_name].search(
                safe_eval(self.rule_id.domain))
            field_ids = []
            if self.rule_id.model_name != \
                    self.marketing_config_id.model_id.model:
                field_name = self.rule_id.mapping_field
            for obj in obj_ids:
                if field_name:
                    field_ids.append(
                        getattr(obj[field_name],
                                self.marketing_config_id.field_id.name, False))
                else:
                    field_ids.append(
                        getattr(obj, self.marketing_config_id.field_id.name,
                                False))
        for activity in self.mapped('mail_activity_line'):
            activity.state = 'in_progress'
            for member in self.mapped('mail_member_line'):
                schedule_time = self.calculate_activity_date(
                    member, activity)
                if self.rule_id:
                    obj_fields = \
                        getattr(member.member,
                                self.marketing_config_id.field_id.name, False)
                    if obj_fields in field_ids:
                        _activity = self.rule_id.destination_true_id
                    else:
                        _activity = self.rule_id.destination_false_id
                else:
                    _activity = activity
                member_activity = member_activity_obj.search(
                    [('mail_activity_id', '=', _activity.id),
                     ('res_id', '=', member.member_id)])
                if _activity and not member_activity and \
                        not _activity.parent_id.rule_id:
                    member_activity = member_activity_obj.create(
                        {'name': _activity.name,
                         'mail_activity_id': _activity.id,
                         'mail_member_id': member.id,
                         'rule_id': _activity.rule_id.id,
                         'mass_mailing_id': _activity.mass_mailing_id.id,
                         'res_id': member.member_id,
                         'schedule_date': schedule_time,
                         'state': _activity.state})
                if _activity.child_line:
                    self._create_recursive_members_activity(
                        member, _activity, member_activity)
        self.need_update = False

    @api.multi
    def get_members(self):
        self.ensure_one()
        form_id = self.env.ref('marketing_automation.view_mail_member_form').id
        tree_id = self.env.ref('marketing_automation.view_mail_member_tree').id
        res = {
            'name': _('Members'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'mail.member',
            'type': 'ir.actions.act_window',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'view_id': False,
        }
        if self.mail_member_line:
            res.update({'domain': [('id', 'in',
                                    self.mail_member_line.ids or [])]})
        return res

    def _create_recursive_members_activity(
            self, member, activity, member_activity):
        member_activity_obj = self.env['member.activity']
        if activity.child_line:
            for child_activity in activity.child_line:
                child_activity.state = 'in_progress'
                schedule_time = self.calculate_activity_date(
                    member, child_activity)
                child_id = \
                    member_activity_obj.search(
                        [('mail_activity_id', '=', child_activity.id),
                         ('res_id', '=', member.member_id)])
                rule_id = child_activity.parent_id.rule_id
                con_opt = child_activity.conditional_option
                if not child_id and (not rule_id or not con_opt):
                    vals = {'name': child_activity.name,
                            'mail_activity_id': child_activity.id,
                            'mass_mailing_id': activity.mass_mailing_id.id,
                            'parent_id': member_activity.id,
                            'res_id': member.member_id,
                            'schedule_date': schedule_time,
                            'mail_member_id': member.id,
                            'state': child_activity.state}
                    if child_activity.rule_id:
                        vals.update({
                            'rule_id': child_activity.rule_id.id,
                        })
                    child_id = member_activity_obj.create(vals)
                    if child_activity.child_line:
                        self._create_recursive_members_activity(
                            member, child_activity, child_id)
        return True

    @api.multi
    def calculate_activity_date(self, member, activity):
        schedule_time = datetime.now()
        current_date = \
            member.schedule_date and datetime.strptime(
                member.schedule_date, DEFAULT_SERVER_DATETIME_FORMAT)
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
        if activity.action_type not in \
                ['send_mail', 'child_activity', 'email_not_open',
                 'email_not_replied', 'email_not_click']:
            schedule_time = False
        return schedule_time

    @api.model
    def _create_member_activities(self):
        mail_marketing = self.env['mail.marketing'].search([(
            'mail_member_line', '!=', False)])
        mail_marketing.create_member_activities()

    def convert_datetime_with_utc(self, date):
        if date:
            user_tz = pytz.timezone(
                self.env.context.get('tz') or self.env.user.tz or 'UTC')
            return fields.Datetime.from_string(date).replace(
                tzinfo=pytz.utc).astimezone(user_tz)

    def check_activity_validity(self, activity):
        validity = True
        if activity.mail_activity_id.activity_validity:
            date = activity.mail_member_id.schedule_date and \
                datetime.strptime(activity.mail_member_id.schedule_date,
                                  DEFAULT_SERVER_DATETIME_FORMAT)
            mail_activity = activity.mail_activity_id
            if mail_activity.activity_validity_type == 'month':
                valid_date = date + relativedelta(
                    month=mail_activity.activity_validity_time)
            elif mail_activity.activity_validity_type == 'week':
                valid_date = date + timedelta(
                    weeks=mail_activity.activity_validity_time)
            elif mail_activity.activity_validity_type == 'day':
                valid_date = date + timedelta(
                    days=mail_activity.activity_validity_time)
            elif mail_activity.activity_validity_type == 'hours':
                valid_date = date + timedelta(
                    hours=mail_activity.activity_validity_time)
            elif mail_activity.activity_validity_type == 'minutes':
                valid_date = date + timedelta(
                    minutes=mail_activity.activity_validity_time)
            current_time = datetime.now()
            validity = False
            if valid_date and valid_date <= current_time:
                validity = True
        return validity

    def get_recursive_member(self, activity):
        if not activity.mail_member_id:
            return self.get_recursive_member(activity.parent_id)
        return activity.mail_member_id.member_id

    def _execute_recursive_marketing_activity_mails(self, activity):
        if activity.child_line:
            for child_activity in activity.child_line:
                schedule_date = \
                    child_activity.schedule_date and \
                    datetime.strptime(child_activity.schedule_date,
                                      DEFAULT_SERVER_DATETIME_FORMAT)
                current_time = datetime.now()
                valid = self.check_activity_validity(child_activity)
                if valid and schedule_date and \
                        schedule_date <= current_time and \
                        child_activity.mail_activity_id.mass_mailing_id:
                    member = self.get_recursive_member(child_activity)
                    status = self.env['mail.marketing'].send_mail(
                        child_activity, member)
                    if status:
                        child_activity.state = 'completed'
                        child_activity.mail_activity_id.state = 'completed'
                    else:
                        activity.state = 'canceled'
                        activity.mail_activity_id.state = 'canceled'

                if valid and schedule_date and \
                    schedule_date <= current_time and \
                        child_activity.mail_activity_id.ir_actions_server_id:
                    status = False
                    try:
                        status = child_activity.mail_activity_id.\
                            ir_actions_server_id.run()
                    except Exception:
                        _logger.warning(_(
                            'Marketing Automation: activity <%s> Failed To '
                            'Execute'),
                            activity.mail_activity_id.ir_actions_server_id,
                            exc_info=True)
                    if status:
                        activity.state = 'completed'
                        activity.mail_activity_id.state = 'completed'
                    else:
                        activity.state = 'canceled'
                        activity.mail_activity_id.state = 'canceled'

                if child_activity.child_line:
                    self._execute_recursive_marketing_activity_mails(
                        child_activity)
        return True

    def _recursive_members_activity(
            self, member_activity, parent_activity, activity):
        member_activity_obj = self.env['member.activity']
        if activity.child_line:
            for child_activity in activity.child_line:
                child_activity.state = 'in_progress'
                schedule_time = \
                    self.calculate_activity_date(parent_activity,
                                                 child_activity)
                child_id = \
                    member_activity_obj.search(
                        [('mail_activity_id', '=', child_activity.id),
                         ('res_id', '=', parent_activity.res_id)])
                if not child_id:
                    child_id = member_activity_obj.create(
                        {'name': child_activity.name,
                         'mail_activity_id': child_activity.id,
                         'mass_mailing_id': activity.mass_mailing_id.id,
                         'parent_id': member_activity.id,
                         'res_id': parent_activity.res_id,
                         'schedule_date': schedule_time,
                         'state': child_activity.state})
                if child_activity.child_line:
                    self._recursive_members_activity(member_activity,
                                                     parent_activity,
                                                     activity)
        return True

    @api.multi
    def execute_marketing_activity(self):
        self.execute_marketing_activity_mails()

    @api.model
    def execute_marketing_activity_mails(self):
        domain = [('state', 'in', ['in_progress', 'new'])]
        if self.env.context.get('mail_marketing_id'):
            domain.append(('mail_member_id.mail_marketing_id', '=',
                           self.env.context.get('mail_marketing_id')))
        if self.env.context.get('member_activity_id'):
            domain.append(('id', '=', self.env.context.get(
                'member_activity_id')))
        activities = self.env['member.activity'].search(domain)
        for activity in activities:
            schedule_date = \
                activity.schedule_date and \
                datetime.strptime(activity.schedule_date,
                                  DEFAULT_SERVER_DATETIME_FORMAT)
            current_time = datetime.now()
            if activity.rule_id:
                member_activity_obj = self.env['member.activity']
                obj_ids = self.env[activity.rule_id.model_name].search(
                    safe_eval(activity.rule_id.domain))
                field_ids = []
                cfg = None
                map = None
                for config in activity.marketing_config_id.child_line:
                    if config.field_id.name in activity.rule_id.mapping_field:
                        cfg = config
                for obj in obj_ids:
                    field_ids.append(getattr(
                        obj, cfg.field_id.name, False))
                obj_fields = getattr(activity.mail_member_id.member,
                                     cfg.field_id.name,
                                     False)
                if activity.rule_id.model_name != \
                        activity.mail_member_id.member._name:
                    map = activity.mail_member_id.member in field_ids
                if obj_fields in field_ids or map:
                    activity_id = activity.rule_id.destination_true_id
                else:
                    activity_id = activity.rule_id.destination_false_id
                schedule_time = self.calculate_activity_date(activity,
                                                             activity_id)
                if activity_id:
                    member_activity = member_activity_obj.create(
                        {'name': activity_id.name,
                         'mail_activity_id': activity_id.id,
                         'mass_mailing_id': activity_id.mass_mailing_id.id,
                         'parent_id': activity.id,
                         'res_id': activity.res_id,
                         'mail_member_id': activity.mail_member_id.id,
                         'schedule_date': schedule_time,
                         'state': activity_id.state
                         })
                    if activity_id.child_line:
                        self._recursive_members_activity(member_activity,
                                                         activity, activity_id)

            valid = self.check_activity_validity(activity)
            if valid and schedule_date and schedule_date <= current_time and \
                    activity.mail_activity_id.mass_mailing_id:
                status = self.env['mail.marketing'].send_mail(activity,
                                                              activity.res_id)
                if status:
                    activity.state = 'completed'
                    activity.mail_activity_id.state = 'completed'
                else:
                    activity.state = 'canceled'
                    activity.mail_activity_id.state = 'canceled'

            if valid and schedule_date and schedule_date <= current_time and \
                    activity.mail_activity_id.ir_actions_server_id:
                status = False
                try:
                    status = \
                        activity.mail_activity_id.ir_actions_server_id.run()
                except Exception:
                    _logger.warning(_(
                        'Marketing Automation: activity <%s> Failed To '
                        'Execute'),
                        activity.mail_activity_id.ir_actions_server_id,
                        exc_info=True)
                if status:
                    activity.state = 'completed'
                    activity.mail_activity_id.state = 'completed'
                else:
                    activity.state = 'canceled'
                    activity.mail_activity_id.state = 'canceled'

            if activity.child_line:
                action_completed = \
                    self._execute_recursive_marketing_activity_mails(activity)
                if action_completed:
                    self.check_campaign_state()

    def send_mail(self, activity, member):
        statistic = self.env['mail.mail.statistics'].search([
            ('member_activity_id', '=', activity.parent_id.id),
            ('res_id', '=', activity.res_id)
        ])
        mass_mailing_id = \
            activity.mail_activity_id.mass_mailing_id
        context = {'activity_id': activity.id}
        if activity.action_type in ['send_mail', 'child_activity']:
            return mass_mailing_id.with_context(context).send_mail([member])
        else:
            if statistic and activity.action_type == 'email_open' and \
                    statistic.opened:
                return mass_mailing_id.with_context(context).send_mail([
                    member])

            elif statistic and activity.action_type == 'email_not_open' and \
                    not statistic.opened:
                return mass_mailing_id.with_context(context).send_mail([
                    member])

            elif statistic and activity.action_type == 'email_replied' and \
                    statistic.replied:
                return mass_mailing_id.with_context(context).send_mail([
                    member])

            elif statistic and activity.action_type == \
                    'email_not_replied' and not statistic.replied:
                return mass_mailing_id.with_context(context).send_mail([
                    member])

            elif statistic and activity.action_type == 'email_clicked' and \
                    statistic.clicked:
                return mass_mailing_id.with_context(context).send_mail([
                    member])

            elif statistic and activity.action_type == \
                    'email_not_click' and not statistic.clicked:
                return mass_mailing_id.with_context(context).send_mail([
                    member])

            elif statistic and activity.action_type == 'email_bounced' and \
                    statistic.bounced:
                return mass_mailing_id.with_context(context).send_mail([
                    member])
