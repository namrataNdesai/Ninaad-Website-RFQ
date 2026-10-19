# -*- coding: utf-8 -*-
import math

from odoo import models
from odoo.http import request

RFQ_SESSION_KEY = "rfq_products"
RFQ_MAX_QTY = 1000000


class Website(models.Model):
    _inherit = "website"

    # ------------------------------------------------------------------
    # Session based RFQ list. Nothing here touches sale.order, so adding
    # a product never creates a quotation.
    # ------------------------------------------------------------------

    def _rfq_raw_lines(self):
        lines = []
        for line in request.session.get(RFQ_SESSION_KEY, []):
            if isinstance(line, dict) and line.get("product_id"):
                lines.append({
                    "product_id": int(line["product_id"]),
                    "qty": float(line.get("qty") or 0),
                })
        return lines

    def rfq_get_lines(self):
        """[{"product": product.product, "qty": number}] for products that
        are still sellable/published (the public record rules apply)."""
        raw = self._rfq_raw_lines()
        if not raw:
            return []
        products = self.env["product.product"].search([
            ("id", "in", [line["product_id"] for line in raw]),
            ("sale_ok", "=", True),
        ])
        by_id = {product.id: product for product in products}
        result = []
        for line in raw:
            product = by_id.get(line["product_id"])
            if product:
                qty = line["qty"]
                result.append({
                    "product": product,
                    "qty": int(qty) if qty == int(qty) else qty,
                })
        return result

    def get_rfq_quantity(self):
        total = sum(line["qty"] for line in self._rfq_raw_lines())
        return int(total) if total == int(total) else total

    def rfq_set(self, product_id, qty, replace=False):
        """Add `qty` to (or, with replace=True, set to `qty`) a product of
        the RFQ list. qty <= 0 with replace=True removes the product.
        Returns True on success."""
        try:
            product_id = int(product_id)
            qty = float(qty)
        except (TypeError, ValueError):
            return False
        if product_id <= 0 or not math.isfinite(qty) or qty > RFQ_MAX_QTY:
            return False

        lines = self._rfq_raw_lines()
        existing = next((l for l in lines if l["product_id"] == product_id), None)

        if replace and qty <= 0:
            lines = [l for l in lines if l["product_id"] != product_id]
        else:
            if qty <= 0:
                return False
            if not existing and not self.env["product.product"].search_count([
                ("id", "=", product_id),
                ("sale_ok", "=", True),
            ]):
                return False
            if existing:
                existing["qty"] = qty if replace else min(existing["qty"] + qty, RFQ_MAX_QTY)
            else:
                lines.append({"product_id": product_id, "qty": qty})

        # Re-assign so the session is flagged as modified.
        request.session[RFQ_SESSION_KEY] = lines
        return True

    def rfq_clear(self):
        request.session.pop(RFQ_SESSION_KEY, None)
