import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .. import db_logo


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Stored in the data directory (there is no database yet on the selector page)
    hl_db_selector_logo = fields.Binary('Database Selector Logo')

    @api.model
    def get_values(self):
        res = super().get_values()
        raw = db_logo.read_logo()
        res['hl_db_selector_logo'] = base64.b64encode(raw) if raw else False
        return res

    def set_values(self):
        super().set_values()
        for settings in self:
            data = settings.hl_db_selector_logo
            if data and not db_logo.is_valid_image(base64.b64decode(data)):
                raise UserError(_('The database selector logo must be a PNG, JPEG, GIF, WebP or SVG image.'))
            db_logo.write_logo(data)
