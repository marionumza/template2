# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import http
from flectra.http import content_disposition, request


class MainController(http.Controller):
    @http.route('/module_builder/generate/'
                '<string:generator>/<string:modules>',
                type='http', auth="user")
    def download(self, generator, modules, **kwargs):
        generator = request.env[generator]
        modules = request.env['module.builder.main'].search([
            ('id', 'in', modules.split(','))
        ])
        filename = "{name}.{ext}".format(
            name=modules[0].name if len(
                modules) == 1 else 'modules', ext="zip")
        zip_io = generator.get_zipped(modules)
        content = zip_io.getvalue()
        return request.make_response(
            content,
            headers=[
                ('Content-Type', 'plain/text' or 'application/octet-stream'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )
