/** @odoo-module **/

/**
 * hilatech_pos_waiter_cashier_stats — enregistre le serveur et le caissier
 * de chaque commande POS (champs pos.order server_name / cashier_name).
 *
 * - Serveur : la personne connectée au POS au premier envoi en préparation
 *   (bouton Envoyer / Commander du restaurant). À défaut, celle qui encaisse.
 * - Caissier : la personne connectée au POS à la validation du paiement.
 *
 * Les valeurs sont posées sur la commande avant sa synchronisation avec le
 * serveur (finalizeValidation appelle syncAllOrders).
 */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";

function currentStaffName(pos, order) {
    return pos.getCashier()?.name || order?.employee_id?.name || order?.user_id?.name || false;
}

patch(PosStore.prototype, {
    async sendOrderInPreparationUpdateLastChange(order, opts = {}) {
        if (order && !order.server_name) {
            order.server_name = currentStaffName(this, order);
        }
        return super.sendOrderInPreparationUpdateLastChange(order, opts);
    },
});

patch(OrderPaymentValidation.prototype, {
    async finalizeValidation() {
        const order = this.order;
        if (order) {
            const name = currentStaffName(this.pos, order);
            if (!order.server_name) {
                order.server_name = name;
            }
            order.cashier_name = name;
        }
        return super.finalizeValidation(...arguments);
    },
});
