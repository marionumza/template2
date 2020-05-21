from flectra.tests import common


class MarketingAutomationTest(common.TransactionCase):

    def setUp(self):
        super(MarketingAutomationTest, self).setUp()

        test_config = self.env['marketing.config']
        model = self.env['ir.model'].search([('model', '=', 'res.partner')])
        field = self.env['ir.model.fields'].search(
            [('name', '=', 'id'), ('model_id.model', '=', 'res.partner')])
        self.test_cfg_id = test_config.create(
            {'model_id': model.id, 'field_id': field.id})

    def tearDown(self):
        super(MarketingAutomationTest, self).tearDown()
