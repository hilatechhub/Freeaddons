# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Client(s) utilisés pour les ventes en livraison : leurs factures payées
    # alimentent la carte "Livraisons" du tableau de bord Factures & dette client.
    hl_delivery_customer = fields.Boolean(
        string='Client livraison',
        help="Cochez pour les clients utilisés pour les ventes en livraison : "
             "leurs factures payées sont comptées dans le tableau de bord.")
