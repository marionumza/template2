# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api


class IrActionsActWindow(models.Model):
    _inherit = 'ir.actions.act_window'

    module_id = fields.Many2one(
        'module.builder.main', 'Module', index=1, ondelete='cascade')

    @api.model
    def create(self, vals):
        ctx = self.env.context
        if ctx.get('module_builder', False):
            vals.update({'module_id': ctx['module_builder'].id})
        res = super(IrActionsActWindow, self).create(vals)
        module_id = vals.get('module_id')
        if module_id:
            res.generate_external_id_for_unkown_rec(
                res.display_name, module_id)
        return res
