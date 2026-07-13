/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.TotalWork = publicWidget.Widget.extend({
    selector: ".total_work_section",

    start() {
        return this._super(...arguments).then(() => {
            this._setupCounterObserver();
        });
    },

    _setupCounterObserver() {
        const statNumbers = this.el.querySelectorAll(".stat-number");
        if (!statNumbers.length) {
            return;
        }

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    statNumbers.forEach((statEl) => {
                        this._animateCounter(statEl);
                    });
                    obs.disconnect();
                }
            });
        }, { threshold: 0.3 });

        observer.observe(this.el);
    },

    _animateCounter(statEl) {
        const target = parseInt(statEl.dataset.target, 10) || 0;
        const countEl = statEl.querySelector(".stat-count");
        if (!countEl) {
            return;
        }

        let current = 0;
        const interval = setInterval(() => {
            current++;
            countEl.textContent = current;

            if (current >= target) {
                clearInterval(interval);
            }
        }, 30); // 30ms per step, 180 er jonno ~5.4 sec lagbe
    },
});