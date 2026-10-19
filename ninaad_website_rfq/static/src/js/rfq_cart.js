/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

/**
 * RFQ list (session based). "Add to RFQ List" buttons and the RFQ list
 * page talk to /shop/rfq/* - website_sale's cart routes are never
 * called, so no sale.order (quotation) is created.
 */
publicWidget.registry.NinaadRfqCart = publicWidget.Widget.extend({
    selector: "#wrapwrap",
    events: {
        "click .o_ninaad_rfq_add": "_onAdd",
        "change .o_ninaad_rfq_qty": "_onQtyChange",
        "click .o_ninaad_rfq_remove": "_onRemove",
    },

    _updateBadge(quantity) {
        document.querySelectorAll(".my_cart_quantity").forEach((el) => {
            el.textContent = quantity;
            el.classList.toggle("d-none", !quantity);
        });
    },

    async _onAdd(ev) {
        ev.preventDefault();
        const button = ev.currentTarget;
        if (button.classList.contains("disabled") || button.dataset.busy) {
            return;
        }
        // Grid: product id is on the button. Product page: it lives in the
        // hidden input the variant selector keeps up to date.
        const root = button.closest(".js_product") || button.closest("form") || document;
        const idInput = root.querySelector("input[name='product_id'], input.product_id");
        const qtyInput = root.querySelector("input[name='add_qty'], input.quantity");
        const productId = parseInt(button.dataset.productId || (idInput && idInput.value), 10);
        const qty = parseFloat(qtyInput && qtyInput.value) || 1;
        if (!productId) {
            return;
        }

        button.dataset.busy = "1";
        const original = button.innerHTML;
        try {
            const result = await rpc("/shop/rfq/add", { product_id: productId, qty });
            if (result.success) {
                this._updateBadge(result.cart_quantity);
                button.innerHTML = `<i class="fa fa-check me-2"></i>${_t("Added to RFQ List")}`;
                setTimeout(() => {
                    button.innerHTML = original;
                    delete button.dataset.busy;
                }, 1500);
                return;
            }
        } catch (error) {
            console.error("RFQ add failed", error);
        }
        button.innerHTML = original;
        delete button.dataset.busy;
    },

    async _updateLine(productId, qty) {
        await rpc("/shop/rfq/update", { product_id: productId, qty });
        window.location.reload();
    },

    _onQtyChange(ev) {
        const input = ev.currentTarget;
        return this._updateLine(
            parseInt(input.dataset.productId, 10),
            parseFloat(input.value) || 0
        );
    },

    _onRemove(ev) {
        ev.preventDefault();
        return this._updateLine(parseInt(ev.currentTarget.dataset.productId, 10), 0);
    },
});
