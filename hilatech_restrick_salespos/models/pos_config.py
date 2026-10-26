# -*- coding: utf-8 -*-
# Part of HILATECH SARL. See LICENSE file for full copyright and licensing details.
from collections import defaultdict

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    hilatech_restrict_stock = fields.Boolean(
        string="Block Out-of-Stock Sales",
        default=True,
        help="Prevent cashiers from adding storable products that are out of stock, "
             "or a quantity greater than the real quantity on hand in the stock "
             "location of this Point of Sale.",
    )

    def _hilatech_stock_location(self):
        self.ensure_one()
        return self.picking_type_id.default_location_src_id

    def hilatech_get_available_qty(self, product_ids):
        """Return the real quantity available for the POS, per product.

        Available = quantity on hand in the POS stock location (and its children)
                    - quantities already sold by paid POS orders of open sessions
                      whose stock moves are not done yet (e.g. "update stock at
                      session closing" mode).

        :param list product_ids: ids of product.product records
        :return: dict {product_id (str): available quantity (float)}
                 Only storable products are returned.
        """
        self.ensure_one()
        self.check_access('read')
        location = self._hilatech_stock_location()
        if not location or not product_ids:
            return {}

        Product = self.env['product.product'].sudo()
        products = Product.browse([int(pid) for pid in product_ids]).exists().filtered('is_storable')
        if not products:
            return {}

        on_hand = {
            product.id: product.qty_available
            for product in products.with_context(location=location.id)
        }

        # Quantities sold in open sessions but not yet removed from stock.
        pending = defaultdict(float)
        lines = self.env['pos.order.line'].sudo().search([
            ('product_id', 'in', products.ids),
            ('order_id.state', 'in', ('paid', 'done')),
            ('order_id.session_id.state', '!=', 'closed'),
            ('order_id.config_id.picking_type_id.default_location_src_id', 'child_of', location.id),
        ])
        for line in lines:
            if any(picking.state == 'done' for picking in line.order_id.picking_ids):
                continue
            pending[line.product_id.id] += line.qty

        return {
            str(pid): on_hand[pid] - pending.get(pid, 0.0)
            for pid in on_hand
        }
