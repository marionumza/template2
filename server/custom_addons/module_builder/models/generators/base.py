# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, api
from mako.lookup import TemplateLookup
import posixpath
import zipfile
import os
import io


class ModuleBuilderGeneratorBase(models.TransientModel):
    _name = 'module.builder.generator.base'

    def get_models(self):
        return self.env['ir.model'].search([
            ('model', 'ilike', '%module.builder.generator%'),
            ('model', '!=', 'module.builder.generator.base')
        ])

    @api.model
    def _get_generator_module(self):
        model_ids = self.get_models()
        return [
            (model.model, model.name)
            for model in model_ids
        ]

    @api.model
    def get_paths(self):
        dir_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'templates', '1.0')
        path = [os.path.abspath(dir_path)]
        return path

    @api.model
    def create_mako_env(self):
        mylookup = TemplateLookup(
            directories=self.get_paths(),
            output_encoding='utf-8',
            encoding_errors='replace')
        return mylookup

    @api.model
    def get_zipped(self, modules):
        mako_env = self.create_mako_env()
        files = ZipFile(mako_env)
        [self._get_generate_module(ModuleZipFile(
            files, module), module) for module in modules]
        return files.get_zip()

    @api.model
    def _get_generate_module(self, zip_file, module):
        raise NotImplementedError


class ZipFile(object):
    def __init__(self, mako_env=None,
                 compress_type=zipfile.ZIP_DEFLATED, external_attr=2175008768):
        self.mako_env = mako_env
        self.fileIO = io.BytesIO()
        self.zip = zipfile.ZipFile(self.fileIO, 'w')
        self.default_compress_type = compress_type
        self.default_external_attr = external_attr

    def register_template(self, filename, template, d, **kwargs):
        if not self.mako_env:
            raise ValueError('Mako Environment is not set')
        self.write(filename, self.mako_env.get_template(
            template).render(object=d), **kwargs)

    def write(self, filename, content,
              external_attr=2175008768, compress_type=None):
        info = zipfile.ZipInfo(filename)
        if 'ir.model.access.csv' in filename:
            content = b'id,name,model_id:id,group_id:id,perm_read,' \
                      b'perm_write,perm_create,perm_unlink\n'+content.strip()
        info.compress_type = compress_type or self.default_compress_type
        info.external_attr = external_attr or self.default_external_attr
        self.zip.writestr(info, content)

    def get_zip(self):
        self.zip.close()
        self.fileIO.flush()
        return self.fileIO


class ModuleZipFile(object):
    def __init__(self, zip_file, module):
        self.zip_file = zip_file
        self.module = module

    def register_template(self, filename, template, d, **kwargs):
        self.zip_file.register_template(posixpath.join(
            self.module.name, filename), template, d, **kwargs)

    def write(self, filename, content, **kwargs):
        self.zip_file.write(posixpath.join(
            self.module.name, filename), content, **kwargs)
