/** @odoo-module */
// Part of HILATECH SARL. See LICENSE file for full copyright and licensing details.
import { _t } from "@web/core/l10n/translation";

const EPSILON = 1e-6;

/**
 * Shared state of the stock restriction (one POS per browser tab).
 * - available: Map(productId -> real available quantity, as returned by the server)
 * - bypass: counter; when > 0 quantity checks are skipped (used while Odoo merges
 *   lines internally, after our own check already validated the operation).
 */
export const hilatechStockState = {
    available: new Map(),
    bypass: 0,
};

export function hilatechIsRestricted(config, product) {
    return Boolean(config?.hilatech_restrict_stock && product?.product_tmpl_id?.is_storable);
}

/** Orders of this POS whose quantities are not yet known by the server. */
export function hilatechPendingOrders(models) {
    return models["pos.order"]
        .getAll()
        .filter((order) => order.state !== "cancel" && !(order.finalized && order.isSynced));
}

/** Total positive quantity of `product` in the given orders, ignoring `excludeLine`. */
export function hilatechQtyInOrders(orders, product, excludeLine = null) {
    let total = 0;
    for (const order of orders) {
        for (const line of order.lines || []) {
            if (line === excludeLine || line.product_id?.id !== product.id) {
                continue;
            }
            if (line.qty > 0) {
                total += line.qty;
            }
        }
    }
    return total;
}

export function hilatechExceeds(required, available) {
    return available !== undefined && required > available + EPSILON;
}

function withReplenishmentHint(body) {
    return body + "\n\n" + _t("Please contact the stock manager for replenishment.");
}

function fmt(qty) {
    return String(Math.round((qty || 0) * 1000) / 1000);
}

export function hilatechOutOfStockMessage(product) {
    return {
        title: _t("Product out of stock"),
        body: withReplenishmentHint(
            _t(
                'The product "%s" is out of stock. It cannot be added to the order.',
                product.display_name
            )
        ),
    };
}

export function hilatechInsufficientMessage(product, available, requested) {
    if (available <= EPSILON) {
        return hilatechOutOfStockMessage(product);
    }
    const uom = product.uom_id?.name || product.product_tmpl_id?.uom_id?.name || "";
    return {
        title: _t("Insufficient stock"),
        body: withReplenishmentHint(
            _t(
                'Only %s %s of "%s" available in stock.\nRequested quantity: %s %s.',
                fmt(available),
                uom,
                product.display_name,
                fmt(requested),
                uom
            )
        ),
    };
}

export function hilatechOrderProblemsMessage(problems) {
    return {
        title: _t("Insufficient stock"),
        body: withReplenishmentHint(_t(
            "The order cannot be paid because some products do not have enough stock:\n%s",
            problems
                .map((p) =>
                    _t(
                        '- "%s": requested %s, available %s',
                        p.product.display_name,
                        fmt(p.requested),
                        fmt(Math.max(p.available, 0))
                    )
                )
                .join("\n")
        )),
    };
}
