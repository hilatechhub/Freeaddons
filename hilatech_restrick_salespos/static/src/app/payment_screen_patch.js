/** @odoo-module */
// Part of HILATECH SARL. See LICENSE file for full copyright and licensing details.
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { hilatechOrderProblemsMessage } from "./stock_guard";

patch(PaymentScreen.prototype, {
    // Last safety net: the stock may have changed since the order was started.
    async validateOrder(isForceValidate = false) {
        const problems = await this.pos.hilatechCheckOrderStock(this.currentOrder);
        if (problems.length) {
            this.pos.hilatechShowStockAlert(hilatechOrderProblemsMessage(problems));
            return;
        }
        return await super.validateOrder(...arguments);
    },
});
