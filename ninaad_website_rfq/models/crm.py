# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    product_line = fields.One2many(
        "crm.product.line",
        "lead_id",
        string="CRM Lead",
    )

    def _prepare_opportunity_quotation_context(self):
        context = super()._prepare_opportunity_quotation_context()
        self.ensure_one()
        order_lines = []

        for line in self.product_line:
            order_lines.append((
                0,
                0,
                {
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.qty,
                }
            ))
        context["default_order_line"] = order_lines

        return context

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        self.ensure_one()

        values = super()._prepare_customer_values(
            partner_name,
            is_company=is_company,
            parent_id=parent_id,
        )

        if self.company_id:
            values["company_id"] = self.company_id.id

        return values


class CrmProductLine(models.Model):
    _name = "crm.product.line"

    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )
    lead_id = fields.Many2one(
        "crm.lead",
        string="Lead",
    )
    qty = fields.Float("Quantity")


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = "crm.lead2opportunity.partner"

    def _convert_and_allocate(self, leads, user_ids, team_id=False):
        self.ensure_one()
        print("144 - - -- - ", self._context)
        print("_convert_and_allocate  - - --", leads, user_ids)
        for lead in leads:
            if lead.active and self.action != "nothing":
                self._convert_handle_partner(
                    lead,
                    self.action,
                    self.partner_id.id or lead.partner_id.id,
                )

            lead.convert_opportunity(
                lead.partner_id,
                user_ids=False,
                team_id=False,
            )

        leads_to_allocate = leads
        if not self.force_assignment:
            leads_to_allocate = leads_to_allocate.filtered(
                lambda lead: not lead.user_id
            )
        website_lead = self._context.get("website_lead", False)
        print("website_lead", website_lead)
        if user_ids and not website_lead and leads:
            leads_to_allocate._handle_salesmen_assignment(
                user_ids,
                team_id=team_id,
            )
