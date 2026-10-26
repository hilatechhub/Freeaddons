/** @odoo-module */
// Part of HILATECH SARL. See LICENSE file for full copyright and licensing details.
import { patch } from "@web/core/utils/patch";
import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(OrderSummary.prototype, {
    // Quantity typed in the "Set the new quantity" popup.
    async updateQuantityNumber(newQuantity) {
        if (newQuantity !== null && newQuantity !== undefined) {
            let line = this.currentOrder.getSelectedOrderline();
            if (line?.combo_parent_id) {
                line = line.combo_parent_id;
            }
            const blocked = line?.hilatechCheckNewQuantity?.(newQuantity);
            if (blocked) {
                this.dialog.add(AlertDialog, blocked);
                return false;
            }
        }
        return await super.updateQuantityNumber(...arguments);
    },
});
