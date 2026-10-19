# Website Product Enquiry

## Overview

**Website Product Enquiry** is an Odoo 18.0 module that replaces direct purchasing on the website with an enquiry workflow.

Visitors add products to an enquiry list, choose the quantities and send the request. The module turns every enquiry into a **lead / opportunity in Odoo CRM**, with the requested products and quantities stored on the record. Sales teams can follow up with the customer without any manual data entry.

No sales quotation is created automatically. The sales team can create one from the lead afterwards.

---

## Features

- Adds an **Add to Enquiry** button on website product pages for logged-in and public users.
- Enquiry list shows the selected products with their quantities.
- **Logged-in users:** a lead / opportunity is created for their own contact.
- **Public users:** an enquiry form collects name, email, phone number, company and location.
- **Contact matching:** an existing contact is found by email or phone number. A new contact is created only when no match exists.
- New **Products** tab on the CRM lead / opportunity listing the requested products and quantities.
- Reduces manual data entry and keeps the sales pipeline updated with website enquiries.

---

## How It Works

```text
Website product page
        |
        v
Add to Enquiry  -->  Enquiry list (products + quantities)
        |
        v
Submit enquiry
        |
        +-- Logged-in user --> Lead / opportunity for the user's contact
        |
        +-- Public user -----> Enquiry form
                                   |
                                   v
                       Match contact by email or phone
                          |                    |
                       found               not found
                          |                    |
                          |            Create new contact
                          v                    v
                     Lead / opportunity for that contact
                                   |
                                   v
                  CRM record > Products tab (products + quantities)
```

---

## Installation

1. Copy the module folder into your Odoo addons path.
2. Restart the Odoo server.
3. Go to **Apps**, click **Update Apps List**.
4. Search for **Website Product Enquiry** and click **Install**.

---

## Usage

1. Open the website and go to any product page.
2. Click **Add to Enquiry**.
3. Open the enquiry list to review the products and adjust the quantities.
4. Submit the enquiry.
   - **Logged-in user:** the lead / opportunity is created for the user's own contact.
   - **Public user:** fill in name, email, phone number, company and location. The module reuses a contact with the same email or phone number, otherwise it creates a new one, and then creates the lead / opportunity.
5. In **CRM**, open the record and check the **Products** tab for the requested products and quantities.

---

## Support

For support, contact: support@ninaadglobal.com

---

## Author

**Ninaad Global Pvt Ltd.**
https://www.ninaadglobal.com
