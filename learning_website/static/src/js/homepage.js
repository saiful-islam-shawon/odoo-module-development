/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.HomeParallaxEffect = publicWidget.Widget.extend({
    selector: "#wrap",

    start() {
        this._super(...arguments);

        console.log("Home parallax widget loaded");

        this.image = this.el.querySelector(".parallax-image");

        if (!this.image) {
            console.log("Parallax image not found");
            return Promise.resolve();
        }

        this._onMouseMove = (e) => {
            const rect = this.el.getBoundingClientRect();

            const x = ((e.clientX - rect.left) / rect.width - 0.5) * 200;
            const y = ((e.clientY - rect.top) / rect.height - 0.5) * 200;

            this.image.style.transform = `translate3d(${x}px, ${y}px, 0)`;
        };

        this._onMouseLeave = () => {
            this.image.style.transform = "translate3d(0, 0, 0)";
        };

        this.el.addEventListener("mousemove", this._onMouseMove);
        this.el.addEventListener("mouseleave", this._onMouseLeave);

        return Promise.resolve();
    },

    destroy() {
        if (this._onMouseMove) {
            this.el.removeEventListener("mousemove", this._onMouseMove);
        }

        if (this._onMouseLeave) {
            this.el.removeEventListener("mouseleave", this._onMouseLeave);
        }

        this._super(...arguments);
    },
});