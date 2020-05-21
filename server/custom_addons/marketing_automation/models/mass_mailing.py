# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    marketing_automation = fields.Boolean(
        string='Marketing Automation')
