/** @odoo-module */
// Part of HILATECH SARL. See LICENSE file for full copyright and licensing details.
import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import {
    hilatechStockState,
    hilatechIsRestricted,
    hilatechPendingOrders,
    hilatechQtyInOrders,
    hilatechExceeds,
    hilatechInsufficientMessage,
} from "./stock_guard";

patch(PosOrderline.prototype, {
    /**
     * Returns false when the new quantity is allowed, otherwise a {title, body}
     * message (the format expected by the POS numpad to display a popup).
     */
    hilatechCheckNewQuantity(quantity) {
        if (hilatechStockState.bypass > 0) {
            return false;
        }
        const order = this.order_id;
        if (
            !order ||
            !hilatechIsRestricted(order.config_id || order.config, this.product_id) ||
            order.preset_id?.is_return ||
            this.refunded_orderline_id ||
            this.combo_parent_id
        ) {
            return false;
        }
        const newQty =
            typeof quantity === "number" ? quantity : parseFloat("" + (quantity ? quantity : 0));
        if (!(newQty > 0) || newQty <= this.qty) {
            return false; // decreasing or removing is always allowed
        }
        const available = hilatechStockState.available.get(this.product_id.id);
        const required =
            hilatechQtyInOrders(hilatechPendingOrders(this.models), this.product_id, this) + newQty;
        if (hilatechExceeds(required, available)) {
            return hilatechInsufficientMessage(this.product_id, available, required);
        }
        return false;
    },

    setQuantity(quantity, keep_price) {
        const blocked = this.hilatechCheckNewQuantity(quantity);
        if (blocked) {
            return blocked;
        }
        return super.setQuantity(...arguments);
    },
});
