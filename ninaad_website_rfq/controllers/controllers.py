from odoo.addons.portal.controllers import portal
from odoo import http, SUPERUSER_ID
from odoo.http import route, request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website.controllers.main import Website as WebsiteController
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.models.ir_http import sitemap_qs2dom
import logging
_logger = logging.getLogger(__name__)


class WebsiteSearch(WebsiteController):

    def _is_product_name_search(self):
        path = request.httprequest.path
        return (
            path == "/website/search"
            or path.startswith("/website/search/page/")
            or path.startswith("/website/search/products_only")
        )

    def _get_hybrid_search_options(self, **post):
        options = super()._get_hybrid_search_options(**post)
        if self._is_product_name_search():
            options.update({
                "displayDescription": False,
                "displayDetail": False,
                "displayExtraDetail": False,
                "displayExtraLink": False,
                "displayImage": False,
            })
        return options

    @route()
    def hybrid_list(self, page=1, search="", search_type="all", **kw):
        if search_type == "all" and self._is_product_name_search():
            search_type = "products_only"
        return super().hybrid_list(
            page=page,
            search=search,
            search_type=search_type,
            **kw,
        )


class WebsiteSale(WebsiteSale):

    # def sitemap_shop(env, rule, qs):
    #     website = env['website'].get_current_website()
    #     if website and website.ecommerce_access == 'logged_in' and not qs:
    #         # Make sure urls are not listed in sitemap when restriction is active
    #         # and no autocomplete query string is provided
    #         return

    #     if not qs or qs.lower() in '/shop':
    #         yield {'loc': '/shop'}

    #     Category = env['product.public.category']
    #     dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
    #     dom += website.website_domain()
    #     for cat in Category.search(dom):
    #         loc = '/shop/category/%s' % env['ir.http']._slug(cat)
    #         if not qs or qs.lower() in loc:
    #             yield {'loc': loc}

    def _get_cart_notification_information(self, order, line_ids):
        res = super()._get_cart_notification_information(order, line_ids)

        for line in res.get("lines", []):
            sale_line = order.order_line.filtered(lambda l: l.id == line["id"])[:1]
            if sale_line:
                line["show_price"] = bool(request.website.company_id.show_price)

        return res

    # ------------------------------------------------------------------
    # RFQ mode: never create a sale.order from an "add to cart" call.
    # The RFQ buttons use /shop/rfq/add directly; these two overrides
    # only catch any standard add-to-cart button that is still around
    # (snippets, default grid button, ...).
    # ------------------------------------------------------------------
    @route()
    def cart_update(self, **kw):
        if not request.website.company_id.allow_rfq:
            return super().cart_update(**kw)
        request.website.rfq_set(kw.get("product_id"), kw.get("add_qty") or 1)
        return request.redirect("/shop/rfq")

    @route()
    def cart_update_json(self, **kw):
        if not request.website.company_id.allow_rfq:
            return super().cart_update_json(**kw)
        website = request.website
        if kw.get("set_qty") not in (None, ""):
            website.rfq_set(kw.get("product_id"), kw.get("set_qty"), replace=True)
        else:
            website.rfq_set(kw.get("product_id"), kw.get("add_qty") or 1)
        return {
            "cart_quantity": website.get_rfq_quantity(),
            "notification_info": {},
            "warning": "",
        }

    @route()
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        **post,
    ):
        req = super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post,
        )
        request.httprequest.args.get('medium_id')
        return req


class WebsiteForm(WebsiteForm):

    @http.route(
        "/website/form/<string:model_name>",
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def website_form(
        self,
        model_name,
        **kwargs,
    ):
        req = super(WebsiteForm, self).website_form(
            model_name=model_name,
            **kwargs,
        )
        return req

    def _handle_website_form(self, model_name, **kwargs):
        req = super()._handle_website_form(model_name=model_name, **kwargs)
        return req



class NinaadRfqList(http.Controller):

    @http.route("/shop/rfq", type="http", auth="public", website=True, sitemap=False)
    def rfq_list(self, **kwargs):
        if not request.website.company_id.allow_rfq:
            return request.redirect("/shop/cart")
        return request.render(
            "ninaad_website_rfq.rfq_list_page",
            {"lines": request.website.rfq_get_lines()},
        )

    @http.route("/shop/rfq/add", type="json", auth="public", website=True)
    def rfq_add(self, product_id, qty=1, **kwargs):
        website = request.website
        ok = bool(website.company_id.allow_rfq) and website.rfq_set(product_id, qty)
        return {"success": ok, "cart_quantity": website.get_rfq_quantity()}

    @http.route("/shop/rfq/update", type="json", auth="public", website=True)
    def rfq_update(self, product_id, qty=0, **kwargs):
        """Set the quantity of a product; qty <= 0 removes it."""
        website = request.website
        ok = bool(website.company_id.allow_rfq) and website.rfq_set(
            product_id, qty, replace=True
        )
        return {"success": ok, "cart_quantity": website.get_rfq_quantity()}


class CustomeQute(CustomerPortal):
    @http.route(
        "/web/crm-quote-request",
        type="http",
        auth="public",
        website=True,
    )
    def shipping_request(self, **kwargs):
        leadObj = request.env["crm.lead"]
        PartnerObj = request.env["res.partner"]
        lead2opportunityObj = request.env["crm.lead2opportunity.partner"]
        name = kwargs.get("name") or ""
        email = kwargs.get("email") or ""
        phone = kwargs.get("phone") or ""
        location = kwargs.get("location") or ""
        company = kwargs.get("company") or ""
        description = kwargs.get("notes") or ""
        def _to_id(value):
            return int(value) if str(value or "").isdigit() else False

        campaign_id = _to_id(kwargs.get("campaign_id"))
        medium_id = _to_id(kwargs.get("medium_id"))
        source_id = _to_id(kwargs.get("source_id"))
        # Guests must not be assigned to the public user as salesperson.
        salesperson_id = False if request.env.user._is_public() else request.env.uid

        partner_id = False
        if not request.env.user._is_public():
            # Logged in (portal) user -> use his own partner record
            login_partner = request.env.user.partner_id
            partner_id = login_partner
            # Use partner's stored details, falling back to submitted
            # form values only if the partner field is empty
            name = login_partner.name or name
            email = login_partner.email or email
            phone = login_partner.phone or login_partner.mobile or phone
            location = login_partner.street or location
            company = (
                login_partner.parent_id.name
                if login_partner.parent_id
                else (login_partner.commercial_company_name or company)
            )
        else:
            partner_id = PartnerObj.with_user(SUPERUSER_ID).search(
                ["|", ("email", "=", email), ("phone", "=", phone)], limit=1
            )

        # ------------------------------------------------------------------

        # Products come from the session RFQ list - no sale.order involved.
        product_line = [
            (0, 0, {"product_id": line["product"].id, "qty": line["qty"]})
            for line in request.website.rfq_get_lines()
        ]

        lead_vals = {
            "type": "lead",
            "name": "Website Product Lead : " + name,
            "contact_name": name,
            "email_from": email,
            "phone": phone,
            "mobile": phone,
            "street": location,
            "partner_name": company,
            "description": description,
            "user_id": salesperson_id,
            "company_id": request.website.company_id.id,
            "campaign_id": campaign_id,
            "medium_id": medium_id,
            "source_id": source_id,
            "partner_id": partner_id.id if partner_id else False,
            "product_line": product_line,
        }
        # Genrate a Lead
        lead_id = leadObj.with_user(SUPERUSER_ID).create(lead_vals)
        if partner_id:
            opportunity_id = lead2opportunityObj.with_context(
                {
                    "default_lead_id": lead_id.id,
                    "active_model": "crm.lead",
                    "active_id": lead_id.id,
                    "active_ids": lead_id.ids,
                }
            ).create(
                {
                    "name": "convert",
                    "action": "exist",
                    "partner_id": partner_id.id,
                    "lead_id": lead_id.id,
                    "team_id": request.website.salesteam_id.id,
                    "user_id": salesperson_id,
                }
            )
            opportunity_id.sudo().with_context(website_lead=True).action_apply()
        else:
            opportunity_id = lead2opportunityObj.with_context(
                {
                    "default_lead_id": lead_id.id,
                    "active_model": "crm.lead",
                    "active_id": lead_id.id,
                    "active_ids": lead_id.ids,
                }
            ).create(
                {
                    "name": "convert",
                    "action": "create",
                    "lead_id": lead_id.id,
                    "team_id": request.website.salesteam_id.id,
                    "user_id": salesperson_id,
                }
            )
            opportunity_id.sudo().with_context(website_lead=True).action_apply()

        partner = opportunity_id.lead_id.partner_id
        if not request.env.user or request.env.user._is_public():
            if partner:
                partner_update_vals = {}

                if not partner.website_id:
                    partner_update_vals["website_id"] = request.website.id

                if not partner.company_id:
                    partner_update_vals["company_id"] = request.website.company_id.id

                if partner_update_vals:
                    partner.sudo().write(partner_update_vals)

        final_lead = opportunity_id.lead_id
        website = request.website

        if final_lead.email_from:
            try:
                template = request.env.ref("ninaad_website_rfq.email_template_rfq_request")
                company = website.company_id or final_lead.company_id

                email_values = {"auto_delete": False}

                # Sender: company email only, nothing hardcoded
                email_from = company.email_formatted
                if email_from:
                    email_values["email_from"] = email_from
                    # Mail server: the one whose From Filtering matches this sender
                    server, _from = request.env["ir.mail_server"].sudo()._find_mail_server(email_from)
                    if server:
                        email_values["mail_server_id"] = server.id

                mail_id = template.sudo().send_mail(
                    final_lead.id,
                    force_send=True,
                    email_values=email_values,
                )
                _logger.info(
                    "RFQ mail %s sent for lead %s, sender=%s",
                    mail_id, final_lead.id, email_from or "template/default",
                )
            except Exception:
                _logger.exception("RFQ confirmation mail failed for lead %s", final_lead.id)

        request.website.rfq_clear()
        return request.redirect("/contactus-thank-you")

