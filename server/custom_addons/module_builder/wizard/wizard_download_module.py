# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, api, fields


class ModuleGenerate(models.TransientModel):
    _name = 'module.builder.download.module.wizard'

    @api.model
    def _get_generators(self):
        return self.env[
            'module.builder.generator.base']._get_generator_module()

    generator = fields.Selection(
        _get_generators, 'Version',
        required=True, default='module.builder.generator.fv1')

    @api.multi
    def generate(self):
        ids = self.env.context.get('active_ids') or (
            [self.env.context.get('active_id')
             ] if self.env.context.get('active_id') else [])
        return {
            'type': 'ir.actions.act_url',
            'url': '/module_builder/generate/{generator}/{ids'
                   '}'.format(ids=','.join([str(i) for i in ids]),
                              generator=self.generator),
            'target': 'self'
        }
