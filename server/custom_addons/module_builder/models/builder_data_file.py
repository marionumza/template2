# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api, tools
from base64 import decodebytes
import os
import mimetypes


class ModuleBuilderDataFile(models.Model):
    _name = 'module.builder.data.file'
    _rec_name = 'path'

    module_id = fields.Many2one(
        'module.builder.main', 'Module', ondelete='cascade')
    extension = fields.Char(
        'Extension', compute='_compute_file_data', store=True)
    ctype = fields.Char(
        'Content Type', compute='_compute_file_data', store=True)
    path = fields.Char(
        string='Path',
        required=True, default='/static/description/')
    is_image = fields.Boolean(
        'Is Image', compute='_compute_file_data', store=True)
    filename = fields.Char(
        'Filename', compute='_compute_file_data', store=True)
    image_small = fields.Binary(
        'Image Thumb', compute='_compute_file_data', store=True)
    content = fields.Binary('Content')
    size = fields.Integer('Size', compute='_compute_file_data', store=True)
    icon = fields.Char('Icon File', store=True)

    @api.one
    @api.depends('content', 'path')
    def _compute_file_data(self):
        if self.content:
            self.size = len(decodebytes(self.content))
            self.filename = os.path.basename(self.path)
            self.extension = os.path.splitext(self.path)[1]
            self.ctype = mimetypes.guess_type(
                self.filename)[0] if mimetypes.guess_type(
                self.filename) else False
            self.is_image = self.ctype in [
                'image/png', 'image/jpeg', 'image/gif', 'image/bmp']
            self.image_small = tools.image_resize_image_small(
                self.content, size=(100, 100)) if self.is_image else False
        else:
            self.size = False
            self.filename = False
            self.extension = False
            self.ctype = False
            self.image_small = False
            self.is_image = False
