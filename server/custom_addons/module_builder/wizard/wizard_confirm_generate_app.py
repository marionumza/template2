# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, api


class wizard_app_confirm(models.TransientModel):
    _name = 'wizard.app.confirm'
    _description = 'Confirm Create App Wizard'

    @api.multi
    def act_confirm_yes(self):
        ctx = self.env.context.copy()
        ctx.update({'module_builder': ctx.get('new_app_id')})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Fields For Model',
            'res_model': 'wizard.generate.app',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def act_confirm_no(self):
        ctx = self.env.context.copy()
        return {
            'effect': {
                'fadeout': 'medium',
                'message': 'Well Done!, '
                           'Your App Has Been Created Successfully',
                'type': 'rainbow_man',
                'context': ctx
            }
        }
