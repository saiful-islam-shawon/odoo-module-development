/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

async function callJsonRoute(route, params) {
    const response = await fetch(route, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: params,
            id: Date.now(),
        }),
    });

    const data = await response.json();

    if (data.error) {
        throw new Error(data.error.data ? data.error.data.message : "RPC Error");
    }

    return data.result;
}

publicWidget.registry.SaleOrderCustomer = publicWidget.Widget.extend({
    selector: "#sale_order_form",

    events: {
        "change #so_customer_select": "_onCustomerChange",
    },

    async start() {
        await this._super(...arguments);

        this.invoiceSelect = this.el.querySelector("#so_invoice_address");
        this.deliverySelect = this.el.querySelector("#so_delivery_address");
    },

    async _onCustomerChange(event) {
        const partnerId = event.currentTarget.value;

        if (!partnerId) {
            this._resetAddressSelect(this.invoiceSelect);
            this._resetAddressSelect(this.deliverySelect);
            return;
        }

        try {
            const result = await callJsonRoute("/sale_order/partner_addresses", {
                partner_id: partnerId,
            });

            this._populateAddressSelect(this.invoiceSelect, result.invoice, result.default_invoice);
            this._populateAddressSelect(this.deliverySelect, result.delivery, result.default_delivery);
        } catch (error) {
            console.error("Failed to load addresses:", error);
        }
    },

    _resetAddressSelect(selectEl) {
        selectEl.replaceChildren();

        const option = document.createElement("option");
        option.textContent = "Select customer first";
        selectEl.appendChild(option);
        selectEl.disabled = true;
    },

    _populateAddressSelect(selectEl, options, defaultId) {
        selectEl.replaceChildren();
        selectEl.disabled = false;

        options.forEach((option) => {
            const opt = document.createElement("option");
            opt.value = option.id;
            opt.textContent = option.name;
            selectEl.appendChild(opt);
        });

        if (defaultId) {
            selectEl.value = String(defaultId);
        }
    },
});