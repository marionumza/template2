# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api, _


class ModelBuilderDependency(models.Model):
    _name = 'module.builder.dependency'

    name = fields.Char('Name', compute='_compute_get_name', required=True)
    dtype = fields.Selection([
        ('module', _('Built-in Module Name')),
        ('manual', _('Custom Module Name')),
        ('project', _('Module Builder Name'))
    ], 'Type', default='manual', store=False, search=True)
    module_id = fields.Many2one(
        'module.builder.main', 'Module', ondelete='cascade')
    dmodule_id = fields.Many2one(
        'ir.module.module', 'Dependency', store=False, search=True)
    dmodule_name = fields.Char('Dependency', index=True)
    dproject_id = fields.Many2one(
        'module.builder.main', 'Dependency', store=False, search=True)

    @api.multi
    @api.depends('dmodule_id', 'dproject_id', 'dmodule_name')
    def _compute_get_name(self):
        for record in self:
            record.name = record.dmodule_id.name or \
                          record.dproject_id.name or record.dmodule_name
            record.dmodule_name = record.name
