from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    show_price = fields.Boolean(
        default=False,
        string="Publish Price",
        help="Only relevant when 'Published on Website' is enabled.",
    )

    allow_rfq = fields.Boolean(
        default=True,
        string="Generate RFQ",
        help="Only relevant when 'Can be Purchased' is enabled.",
    )