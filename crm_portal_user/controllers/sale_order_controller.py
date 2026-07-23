from odoo import http, fields
from odoo.http import request


class SaleOrder(http.Controller):

    @http.route("/sale_order", type="http", auth="user", website=True)
    def sale_order(self, **kwargs):
        company_id = request.env.company.id

        products = request.env["product.product"].sudo().search(
            [("sale_ok", "=", True)], order="name"
        )

        product_tax_map = {
            product.id: sum(
                t.amount for t in product.taxes_id if t.amount_type == "percent"
            )
            for product in products
        }

        values = {
            "active_menu": "sale_order",
            "products": products,
            "product_tax_map": product_tax_map,
            "customers": request.env["res.partner"].sudo().search([], order="name"),
            "pricelists": request.env["product.pricelist"].sudo().search(
                ["|", ("company_id", "=", False), ("company_id", "=", company_id)],
                order="name",
            ),
            "payment_terms": request.env["account.payment.term"].sudo().search(
                ["|", ("company_id", "=", False), ("company_id", "=", company_id)],
                order="name",
            ),
        }
        return request.render("crm_portal_user.sale_order_template", values)

    @http.route("/sale_order/partner_addresses", type="json", auth="user", website=True)
    def partner_addresses(self, partner_id=None, **kwargs):
        if not partner_id:
            return {"invoice": [], "delivery": [], "default_invoice": False, "default_delivery": False}

        partner = request.env["res.partner"].sudo().browse(int(partner_id))
        default_addr = partner.address_get(["invoice", "delivery"])

        invoice_children = partner.child_ids.filtered(lambda c: c.type == "invoice")
        delivery_children = partner.child_ids.filtered(lambda c: c.type == "delivery")

        invoice_list = [{"id": partner.id, "name": partner.name}] + [
            {"id": a.id, "name": a.display_name} for a in invoice_children
        ]
        delivery_list = [{"id": partner.id, "name": partner.name}] + [
            {"id": a.id, "name": a.display_name} for a in delivery_children
        ]

        return {
            "invoice": invoice_list,
            "delivery": delivery_list,
            "default_invoice": default_addr.get("invoice"),
            "default_delivery": default_addr.get("delivery"),
        }

    @http.route("/sale_order/submit", type="http", auth="user", website=True, methods=["POST"], csrf=True)
    def submit_sale_order(self, **kwargs):
        product_ids = request.httprequest.form.getlist("product_id[]")
        quantities = request.httprequest.form.getlist("quantity[]")

        order_lines = []
        for product_id, qty in zip(product_ids, quantities):
            if product_id and qty and float(qty) > 0:
                order_lines.append((0, 0, {
                    "product_id": int(product_id),
                    "product_uom_qty": float(qty),
                }))

        if not order_lines:
            return request.redirect("/sale_order?error=no_lines")

        partner_id = kwargs.get("partner_id")
        if not partner_id:
            return request.redirect("/sale_order?error=no_customer")

        # datetime-local gives "2026-07-31T12:05" -> normalize -> convert to real datetime object
        date_order = kwargs.get("date_order")
        if date_order:
            date_order = date_order.replace("T", " ")
            if len(date_order) == 16:
                date_order += ":00"
            date_order = fields.Datetime.to_datetime(date_order)

        order_vals = {
            "partner_id": int(partner_id),
            "partner_invoice_id": int(kwargs["partner_invoice_id"]) if kwargs.get("partner_invoice_id") else int(partner_id),
            "partner_shipping_id": int(kwargs["partner_shipping_id"]) if kwargs.get("partner_shipping_id") else int(partner_id),
            "validity_date": kwargs.get("validity_date") or False,
            "date_order": date_order or fields.Datetime.now(),
            "pricelist_id": int(kwargs["pricelist_id"]) if kwargs.get("pricelist_id") else False,
            "payment_term_id": int(kwargs["payment_term_id"]) if kwargs.get("payment_term_id") else False,
            "note": kwargs.get("note"),
            "order_line": order_lines,
        }

        request.env["sale.order"].sudo().create(order_vals)

        return request.redirect("/sale_order?success=1")