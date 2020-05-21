# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra.tools import mute_logger
from flectra.addons.marketing_automation.tests.test_campaign_flow import \
    MarketingAutomationTest


class MarketingCampaignTest(MarketingAutomationTest):

    @mute_logger('flectra.addons.base.ir.ir_model', 'flectra.models')
    def test_simple_flow(self):
        Activity = self.env['mail.marketing.activity']

        campaign_id = self.env['mail.marketing'].create({
            'name': 'Test Campaign',
            'marketing_config_id': self.test_cfg_id.id,
        })

        mass_mailing_id = self.env['mail.mass_mailing'].create({
            'name': 'Test Email',
            'mailing_model_id': self.test_cfg_id.id,
            'body_html': '<div>Test Email Body</div>',
            'marketing_automation': True,
        })

        Activity.create({
            'name': 'Activity campaign',
            'mail_marketing_id': campaign_id.id,
            'action_type': 'send_mail',
            'marketing_config_id': self.test_cfg_id.id,
            'mass_mailing_id': mass_mailing_id.id,
            'marketing_type': 'send_mail',
        })

        # User starts and syncs its campaign
        campaign_id.get_started()
        self.assertEqual(campaign_id.state, 'draft')

        campaign_id._confirm_mail_marketing()
        self.assertEqual(campaign_id.get_count(), 40)
