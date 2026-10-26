# -*- coding: utf-8 -*-
from odoo import fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # Renseignés par le POS (static/src/js/staff_capture.js) puis synchronisés avec
    # la commande. Même nom et même type que le champ des modules Hilatech
    # d'impression POS : les deux peuvent être installés ensemble.
    server_name = fields.Char(string='Serveur', index=True)
    cashier_name = fields.Char(string='Caissier', index=True)
