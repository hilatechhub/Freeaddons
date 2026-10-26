/** @odoo-module */
// Part of HILATECH SARL. See LICENSE file for full copyright and licensing details.
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import {
    hilatechStockState,
    hilatechIsRestricted,
    hilatechPendingOrders,
    hilatechQtyInOrders,
    hilatechExceeds,
    hilatechInsufficientMessage,
    hilatechOutOfStockMessage,
    hilatechOrderProblemsMessage,
} from "./stock_guard";

patch(PosStore.prototype, {
    async afterProcessServerData() {
        const result = await super.afterProcessServerData(...arguments);
        if (this.config.hilatech_restrict_stock) {
            // Pre-load the stock so that checks also work if the connection drops.
            const products = this.models["product.product"]
                .getAll()
                .filter((product) => product.product_tmpl_id?.is_storable);
            this.hilatechRefreshStock(products);
        }
        return result;
    },

    /**
     * Fetch the real available quantity of the given products from the server.
     * Returns false if the server could not be reached (cached values are kept).
     */
    async hilatechRefreshStock(products) {
        const ids = [...new Set(products.filter(Boolean).map((product) => product.id))];
        if (!ids.length) {
            return true;
        }
        try {
            const result = await this.data.call("pos.config", "hilatech_get_available_qty", [
                [this.config.id],
                ids,
            ]);
            for (const id of ids) {
                if (result && result[id] !== undefined) {
                    hilatechStockState.available.set(id, result[id]);
                } else {
                    hilatechStockState.available.delete(id);
                }
            }
            return true;
        } catch (error) {
            console.warn("[hilatech_restrick_salespos] Unable to refresh stock:", error);
            return false;
        }
    },

    hilatechShowStockAlert(message) {
        this.dialog.add(AlertDialog, message);
    },

    _hilatechResolve(value, model) {
        return typeof value === "number" ? this.models[model].get(value) : value;
    },

    async addLineToOrder(vals, order, opts = {}, configure = true) {
        if (
            !this.config.hilatech_restrict_stock ||
            opts.hilatech_skip_stock_check ||
            order?.preset_id?.is_return
        ) {
            return await super.addLineToOrder(...arguments);
        }

        const template = this._hilatechResolve(vals.product_tmpl_id, "product.template");
        let product = this._hilatechResolve(vals.product_id, "product.product");
        if (!product && template?.product_variant_ids?.length === 1) {
            product = template.product_variant_ids[0];
        }
        const toWeight = Boolean(template?.to_weight || product?.product_tmpl_id?.to_weight);
        const addedQty = typeof vals.qty === "number" ? vals.qty : 1;

        // 1. Check before adding, when the product is already known.
        if (product && hilatechIsRestricted(this.config, product) && addedQty > 0) {
            await this.hilatechRefreshStock([product]);
            const available = hilatechStockState.available.get(product.id);
            if (available !== undefined && available <= 0) {
                this.hilatechShowStockAlert(hilatechOutOfStockMessage(product));
                return;
            }
            if (!toWeight) {
                const required =
                    hilatechQtyInOrders(hilatechPendingOrders(this.models), product) + addedQty;
                if (hilatechExceeds(required, available)) {
                    this.hilatechShowStockAlert(
                        hilatechInsufficientMessage(product, available, required)
                    );
                    return;
                }
            }
        }

        // 2. Products whose variant or quantity is only known after the standard flow
        //    (variant configurator, weighed products): check after adding and revert.
        const needsPostCheck = !product || toWeight;
        const before = new Map();
        if (needsPostCheck) {
            for (const pendingOrder of hilatechPendingOrders(this.models)) {
                for (const line of pendingOrder.lines || []) {
                    if (line.qty > 0 && line.product_id) {
                        const id = line.product_id.id;
                        before.set(id, (before.get(id) || 0) + line.qty);
                    }
                }
            }
        }

        let line;
        hilatechStockState.bypass++;
        try {
            line = await super.addLineToOrder(...arguments);
        } finally {
            hilatechStockState.bypass--;
        }

        if (line && needsPostCheck && hilatechIsRestricted(this.config, line.product_id)) {
            const lineProduct = line.product_id;
            await this.hilatechRefreshStock([lineProduct]);
            const available = hilatechStockState.available.get(lineProduct.id);
            const total = hilatechQtyInOrders(hilatechPendingOrders(this.models), lineProduct);
            if (hilatechExceeds(total, available)) {
                const added = total - (before.get(lineProduct.id) || 0);
                this.hilatechShowStockAlert(
                    hilatechInsufficientMessage(lineProduct, available, total)
                );
                this._hilatechRevertLine(line, added);
                return;
            }
        }
        return line;
    },

    _hilatechRevertLine(line, addedQty) {
        const remaining = line.qty - addedQty;
        hilatechStockState.bypass++;
        try {
            if (remaining <= 1e-6) {
                line.order_id.removeOrderline(line);
            } else {
                line.setQuantity(remaining, true);
            }
        } finally {
            hilatechStockState.bypass--;
        }
    },

    /** Check the whole order against the real stock. Returns the list of problems. */
    async hilatechCheckOrderStock(order) {
        if (!this.config.hilatech_restrict_stock || !order || order.preset_id?.is_return) {
            return [];
        }
        const totals = new Map();
        for (const line of order.lines || []) {
            const product = line.product_id;
            if (line.qty > 0 && hilatechIsRestricted(this.config, product)) {
                const entry = totals.get(product.id) || { product, requested: 0 };
                entry.requested += line.qty;
                totals.set(product.id, entry);
            }
        }
        if (!totals.size) {
            return [];
        }
        await this.hilatechRefreshStock([...totals.values()].map((entry) => entry.product));
        const problems = [];
        for (const entry of totals.values()) {
            const available = hilatechStockState.available.get(entry.product.id);
            if (hilatechExceeds(entry.requested, available)) {
                problems.push({ ...entry, available });
            }
        }
        return problems;
    },

    async pay() {
        const problems = await this.hilatechCheckOrderStock(this.getOrder());
        if (problems.length) {
            this.hilatechShowStockAlert(hilatechOrderProblemsMessage(problems));
            return;
        }
        return await super.pay(...arguments);
    },
});
