/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.SaleOrderLines = publicWidget.Widget.extend({
    selector: "#sale_order_form",

    events: {
        "click #so_add_line": "_onAddLine",
        "click .so_remove_line": "_onRemoveLine",
        "change .so_product_select": "_onProductChange",
        "input .so_qty_input": "_onQtyChange",
    },

    async start() {
        await this._super(...arguments);
        this.linesContainer = this.el.querySelector("#so_order_lines_container");
        this.grandTotalEl = this.el.querySelector("#so_grand_total");
        this.untaxedTotalEl = this.el.querySelector("#so_untaxed_total");
        this.taxTotalEl = this.el.querySelector("#so_tax_total");
    },

    _onAddLine(event) {
        event.preventDefault();

        const rows = this.linesContainer.querySelectorAll(".so_order_line_row");
        const newRow = rows[0].cloneNode(true);

        newRow.querySelector(".so_product_select").selectedIndex = 0;
        newRow.querySelector(".so_qty_input").value = 1;
        newRow.querySelector(".so_unit_price_display").value = "0.00";
        newRow.querySelector(".so_tax_display").value = "0%";
        newRow.querySelector(".so_amount_display").value = "0.00";
        newRow.dataset.taxRate = 0;

        this.linesContainer.appendChild(newRow);
        this._toggleRemoveButtons();
    },

    _onRemoveLine(event) {
        event.preventDefault();

        const row = event.currentTarget.closest(".so_order_line_row");
        row.remove();

        this._toggleRemoveButtons();
        this._recalculateTotal();
    },

    _onProductChange(event) {
        const row = event.currentTarget.closest(".so_order_line_row");
        const selectedOption = event.currentTarget.selectedOptions[0];
        const price = parseFloat(selectedOption.dataset.price || 0);
        const taxRate = parseFloat(selectedOption.dataset.tax || 0);

        row.querySelector(".so_unit_price_display").value = price.toFixed(2);
        row.querySelector(".so_tax_display").value = taxRate ? `${taxRate}%` : "0%";
        row.dataset.taxRate = taxRate;

        this._updateRowAmount(row);
    },

    _onQtyChange(event) {
        const row = event.currentTarget.closest(".so_order_line_row");
        this._updateRowAmount(row);
    },

    _updateRowAmount(row) {
        const price = parseFloat(row.querySelector(".so_unit_price_display").value || 0);
        const qty = parseFloat(row.querySelector(".so_qty_input").value || 0);
        const amount = price * qty;

        row.querySelector(".so_amount_display").value = amount.toFixed(2);
        this._recalculateTotal();
    },

    _recalculateTotal() {
        const rows = this.linesContainer.querySelectorAll(".so_order_line_row");

        let untaxedTotal = 0;
        let taxTotal = 0;

        rows.forEach((row) => {
            const amount = parseFloat(row.querySelector(".so_amount_display").value || 0);
            const taxRate = parseFloat(row.dataset.taxRate || 0);
            const taxAmount = amount * (taxRate / 100);

            untaxedTotal += amount;
            taxTotal += taxAmount;
        });

        this.untaxedTotalEl.textContent = untaxedTotal.toFixed(2);
        this.taxTotalEl.textContent = taxTotal.toFixed(2);
        this.grandTotalEl.textContent = (untaxedTotal + taxTotal).toFixed(2);
    },

    _toggleRemoveButtons() {
        const rows = this.linesContainer.querySelectorAll(".so_order_line_row");
        const removeButtons = this.linesContainer.querySelectorAll(".so_remove_line");

        removeButtons.forEach((btn) => {
            btn.disabled = rows.length <= 1;
        });
    },
});