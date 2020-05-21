from flectra import http
from flectra.http import request


class MarketingAutomation(http.Controller):

    @http.route('/marketing_automation/ma-create-record-flowchart',
                type='json',
                auth='public')
    def create_record_from_flow_chart(self, data):
        if data:
            activity_type = data['activity_type']
            if activity_type in ['send_mail', 'action']:
                model = request.env[data.pop('res_model')].search(
                    [('id', '=', data['active_id'])])
                if activity_type == 'send_mail':
                    data['mail_template'] = self.create_mail_template(data)
                    if data['mail_template']:
                        data['mass_mailing_id'] = data['mail_template']
                if activity_type == 'action':
                    data['action'] = self.create_server_action(data)
                    if data['action']:
                        data['ir_actions_server_id'] = data['action']
                act = request.env['mail.marketing.activity'].create(data)
                model.write({'mail_activity_line': [(4, act.id)]})
                return act.id
            if activity_type in ['activity_wait']:
                model = request.env['mail.activity.waiting'].create(data)
                return model.id

            if activity_type in ['domain_rules']:
                domain = request.env['mail.activity.rules'].create(data)
                return domain.id

    @http.route('/marketing_automation/ma-unlink-record-flowchart',
                type='json',
                auth='public')
    def unlink_record_from_flow_chart(self, data):
        if data and data['type'] == 'operator':
            activity_type = data['activity_type']
            if activity_type in ['send_mail', 'action']:
                act = request.env['mail.marketing.activity'].search(
                    [('id', '=', data['id'])])
                act.unlink()

            if activity_type in ['activity_wait']:
                request.env['mail.activity.waiting'].search(
                    [('id', '=', data['id'])]).unlink()

            if activity_type in ['domain_rules']:
                request.env['mail.activity.rules'].search(
                    [('id', '=', data['id'])]).unlink()
        elif data and data['type'] == 'link':
            from_activity = data['f_activity_type']
            to_activity = data['t_activity_type']

            start = ["flowchart-event-operator"]

            action = ['flowchart-action-operator']
            action_model = 'mail.marketing.activity'

            flow_control = ['flowchart-fcontrol-operator']
            flow_control_model = 'mail.activity.waiting'

            domain_rules = ['flowchart-domain-operator']
            domain_rules_model = 'mail.activity.rules'

            if from_activity in action and to_activity in action:
                parent = request.env[action_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[action_model].search(
                    [('id', '=', data['child'])])
                child.write({'parent_id': False, 'action_type': False})
                return True

            elif from_activity in action and to_activity in flow_control:
                parent = request.env[action_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[flow_control_model].search(
                    [('id', '=', data['child'])])
                child.write({'activity_id': False, 'action_type': False})
                parent.write({'rule_id': False})
                return True

            elif from_activity in action and to_activity in domain_rules:
                parent = request.env[action_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[domain_rules_model].search(
                    [('id', '=', data['child'])])
                parent.write({'rule_id': False})
                child.write({'activity_id': False, 'action_type': False})
                return True

            elif from_activity in flow_control and to_activity in action:
                parent = request.env[flow_control_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[action_model].search(
                    [('id', '=', data['child'])])
                parent.write({'destination_id': False})
                if parent.conditional_option == 'yes':
                    parent.rule_id.write({'destination_true_id': False})
                else:
                    parent.rule_id.write({'destination_false_id': False})
                child.write({'waiting_id': False})
                child.write({'parent_id': False,
                             'action_type': False})
                return True

            elif from_activity in flow_control and to_activity in domain_rules:
                parent = request.env[flow_control_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[domain_rules_model].search(
                    [('id', '=', data['child'])])
                parent.write({'rule_id': False})
                child.write({'activity_id': False,
                             'action_type': False,
                             'timmer_id': False})
                parent.activity_id.write({'rule_id': False})
                return True

            elif from_activity in domain_rules and to_activity in action:
                parent = request.env[domain_rules_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[action_model].search(
                    [('id', '=', data['child'])])
                if data['action_type'] == 'yes':
                    child.write({'conditional_option': False,
                                 'action_type': False,
                                 'parent_id': False, 'waiting_id': False,
                                 'domain': False})
                    parent.write({'destination_true_id': False})
                else:
                    child.write({'conditional_option': False,
                                 'action_type': False,
                                 'parent_id': False, 'waiting_id': False,
                                 'domain': False})
                    parent.write({'destination_false_id': False})
                return True

            elif from_activity in domain_rules and to_activity in flow_control:
                parent = request.env[domain_rules_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[flow_control_model].search(
                    [('id', '=', data['child'])])
                if data['action_type'] == 'yes':
                    parent.write({'waiting_true_id': False})
                    child.write({'conditional_option': False,
                                 'action_type': False,
                                 'rule_id': False,
                                 'activity_id': False})
                else:
                    parent.write({'waiting_false_id': False})
                    child.write({'conditional_option': False,
                                 'rule_id': False,
                                 'action_type': False,
                                 'activity_id': False})
                return True

            elif from_activity in start and to_activity in domain_rules:
                parent = request.env['mail.marketing'].search(
                    [('id', '=', data['active_id'])])
                child = request.env[domain_rules_model].search(
                    [('id', '=', data['child'])])
                parent.write({'rule_id': False})
                return True

            elif from_activity in start and to_activity in flow_control:
                return True

            elif from_activity in start and to_activity in action:
                return True

            else:
                return False

    def create_server_action(self, data):
        if data['action']['id'] != 'is_new':
            id = data['action']['id']
        else:
            act = request.env['ir.actions.server'].create(
                {'name': data['action']['text'],
                 'model_id': data['model_id'],
                 'state': 'code'})
            id = act.id
        return id

    def create_mail_template(self, data):
        if data['mail_template']['id'] != 'is_new':
            id = data['mail_template']['id']
        else:
            mail = request.env['mail.mass_mailing'].create(
                {'name': data['mail_template']['text'],
                 'mailing_model_id': data['model_id'],
                 'marketing_automation': True})
            id = mail.id
        return id

    @http.route('/marketing_automation/write-parent-child-relation',
                type='json',
                auth='public')
    def write_parent_child_relation(self, data):
        if data:
            from_activity = data['from_activity']
            to_activity = data['to_activity']

            start = ["activity_start"]

            action = ['send_mail', 'action']
            action_model = 'mail.marketing.activity'

            flow_control = ['activity_wait']
            flow_control_model = 'mail.activity.waiting'

            domain_rules = ['domain_rules']
            domain_rules_model = 'mail.activity.rules'

            if from_activity in action and to_activity in action:
                parent = request.env[action_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[action_model].search(
                    [('id', '=', data['child'])])
                # Make Sure child Don't get override by another parent
                if child['parent_id']:
                    return False
                child.write({'parent_id': parent.id,
                             'action_type': data['action_type']})
                return True

            elif from_activity in action and to_activity in flow_control:
                parent = request.env[action_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[flow_control_model].search(
                    [('id', '=', data['child'])])
                # Make Sure child Don't get override by another parent
                if child['activity_id']:
                    return False
                child.write({'activity_id': parent.id,
                             'action_type': data['action_type']})
                return True

            elif from_activity in action and to_activity in domain_rules:
                parent = request.env[action_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[domain_rules_model].search(
                    [('id', '=', data['child'])])
                # Make Sure child Don't get override by another parent
                if child['activity_id']:
                    return False
                parent.write({'rule_id': child.id})
                child.write({'activity_id': parent.id,
                             'action_type': data['action_type']})
                return True

            elif from_activity in flow_control and to_activity in action:
                parent = request.env[flow_control_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[action_model].search(
                    [('id', '=', data['child'])])
                # Make Sure child Don't get override by another parent
                if child['parent_id']:
                    return False
                parent.write({'destination_id': child.id})
                if parent.conditional_option == 'yes':
                    parent.rule_id.write({'destination_true_id': child.id})
                    child.write({'conditional_option': 'yes'})
                elif parent.conditional_option == 'no':
                    parent.rule_id.write({'destination_false_id': child.id})
                    child.write({'conditional_option': 'no'})
                child.write({'waiting_id': parent.id})
                child.write({'parent_id': parent.activity_id.id,
                             'action_type': parent.action_type})
                return True

            elif from_activity in flow_control and to_activity in domain_rules:
                parent = request.env[flow_control_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[domain_rules_model].search(
                    [('id', '=', data['child'])])
                # Make Sure child Don't get override by another parent
                if child['activity_id']:
                    return False
                if parent.rule_id:
                    return False
                parent.write({'rule_id': child.id})
                child.write({'activity_id': parent.activity_id.id,
                             'action_type': parent.action_type,
                             'timmer_id': parent.id})
                parent.activity_id.write({'rule_id': child.id})
                return True

            elif from_activity in domain_rules and to_activity in action:
                parent = request.env[domain_rules_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[action_model].search(
                    [('id', '=', data['child'])])
                # Make Sure child Don't get override by another parent
                if child['parent_id']:
                    return False
                if data['action_type'] == 'yes':
                    if parent.timmer_id:
                        child.write({'waiting_id': parent.timmer_id.id})
                    parent.write({'destination_true_id': child.id})
                    child.write({'conditional_option': 'yes',
                                 'action_type': parent.action_type,
                                 'parent_id': parent.activity_id.id})
                elif data['action_type'] == 'no':
                    if parent.timmer_id:
                        child.write({'waiting_id': parent.timmer_id.id})
                    parent.write({'destination_false_id': child.id})
                    child.write({'conditional_option': 'no',
                                 'action_type': parent.action_type,
                                 'parent_id': parent.activity_id.id})
                return True

            elif from_activity in domain_rules and to_activity in flow_control:
                parent = request.env[domain_rules_model].search(
                    [('id', '=', data['parent'])])
                child = request.env[flow_control_model].search(
                    [('id', '=', data['child'])])
                # Make Sure child Don't get override by another parent
                if child['activity_id']:
                    return False
                if parent.timmer_id:
                    return False
                if data['action_type'] == 'yes':
                    parent.write({'waiting_true_id': child.id})
                    child.write({'conditional_option': 'yes',
                                 'action_type': parent.action_type,
                                 'rule_id': parent.id,
                                 'activity_id': parent.activity_id.id})
                elif data['action_type'] == 'no':
                    parent.write({'waiting_false_id': child.id})
                    child.write({'conditional_option': 'no',
                                 'rule_id': parent.id,
                                 'action_type': parent.action_type,
                                 'activity_id': parent.activity_id.id})
                return True

            elif from_activity in start and to_activity in domain_rules:
                parent = request.env['mail.marketing'].search(
                    [('id', '=', data['active_id'])])
                child = request.env[domain_rules_model].search(
                    [('id', '=', data['child'])])
                parent.write({'rule_id': child.id})
                return True

            elif from_activity in start and to_activity in flow_control:
                return True

            elif from_activity in start and to_activity in action:
                return True
            else:
                return False
        else:
            return False

    @http.route('/marketing_automation/ma-save-activity-builder-state',
                type='json',
                auth='public')
    def save_activity_builder_state(self, data, active_id):
        if data:
            mail_marketing = request.env['mail.marketing'].search(
                [('id', '=', active_id)])
            mail_marketing.write({'activity_builder_data': data})
            return mail_marketing.id

    @http.route('/marketing_automation/write-domain-flowchart',
                type='json',
                auth='public')
    def write_domain_from_flow_chart(self, domain, active_id):
        if domain:
            request.env['mail.activity.rules'].search(
                [('id', '=', active_id)]).write({'domain': domain})
            return True
        return False
