from odoo import models, fields, api, exceptions

import io
import base64
import logging as logger

logger.basicConfig(level=logger.INFO)


class CustomItem(models.Model):
    _name = 'odoo_view_advanced.custom_item'
    _description = 'Model to manage custom items'

    name = fields.Char(string='Description')
    unit_price = fields.Char(string='Unit price')

    def remove_items(self, user):
        logger.info('Deleting items')
        return True


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_items(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Products',
            'view_mode': 'tree,form',
            'res_model': 'odoo_view_advanced.custom_item'
        }


class UploadFile(models.TransientModel):
    _name = 'odoo_view_advanced.upload_file'
    _description = 'Model to upload files'

    upload_file = fields.Binary(string='Upload file', required=True)
    file_name = fields.Char(string='Filename')

    def import_file(self):
        if self.file_name:
            if '.csv' not in self.file_name:
                raise exceptions.ValidationError('File must be a CSV')
            file = self.read_file_from_binary(self.upload_file)
            lines = file.split('\n')
            for line in lines:
                elements = line.split(';')
                if len(elements) > 1:
                    self.env['odoo_view_advanced.custom_item'].create({
                        'name': elements[0],
                        'unit_price': float(elements[1])
                    })
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload'
                    }

    def read_file_from_binary(self, file):
        try:
            with io.BytesIO(base64.b64decode(file)) as f:
                f.seek(0)
                return f.read().decode('UTF-8')
        except Exception as e:
            logger.error(f'Error to read file from binary: {e}')
            raise
