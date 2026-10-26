# -*- coding: utf-8 -*-
# Part of HILATECH SARL. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_hilatech_restrict_stock = fields.Boolean(
        related='pos_config_id.hilatech_restrict_stock',
        readonly=False,
    )
