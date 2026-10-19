# -*- coding: utf-8 -*-
{
    "name": "Website Product Enquiry",
    "summary": "Replace Add to Cart with an enquiry list on website products and create CRM leads with the selected products and quantities.",
    "version": "18.0.1.0.0",
    "category": "Website",
    "description": """
        Website Product Enquiry
        =======================
        Replaces direct website purchasing with an enquiry workflow that feeds CRM.

        * Adds an Enquiry List button on website product pages (login and public users).
        * The enquiry list shows the selected products with quantities.
        * Logged-in users: a lead/opportunity is created for their own contact.
        * Public users: submit a form (name, email, phone, company, location).
        An existing contact is matched by email or phone; otherwise a new contact is created.
        * The lead/opportunity stores the requested products and quantities in a new
        "Products" tab on the CRM form.
        * No sales quotation is created automatically. The sales team can create one
        from the lead afterwards.
            """,
    "author": 'Ninaad Global Pvt Ltd.',
    "website": 'https://www.ninaadglobal.com',
    "support": 'support@ninaadglobal.com',
    "depends": [
        "base",
        "crm",
        "website_sale",
        "payment_stripe",
        "payment_demo",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "views/template.xml",
        "views/crm_view.xml",
        "views/res_company_view.xml"
    ],
    "assets": {
        'web.assets_frontend': [
            'ninaad_website_rfq/static/src/scss/style.scss',
            'ninaad_website_rfq/static/src/js/rfq_cart.js',
        ],
    },
    "images": ["static/description/screen_image.png"],
    "license": 'Other proprietary',
    "installable": True,
    "application": False,
    "auto_install": False,
}
