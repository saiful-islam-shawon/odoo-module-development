/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.HeroTypewriterEffect = publicWidget.Widget.extend({
    selector: ".hero_section",

    start() {
        this._super(...arguments);

        this.timers = [];

        const elements = this.el.querySelectorAll(".typewrite");

        elements.forEach((element) => {
            const toRotate = element.getAttribute("data-type");
            const period = element.getAttribute("data-period");

            if (toRotate) {
                const texts = JSON.parse(toRotate);
                this._startTypewriter(element, texts, period);
            }
        });

        return Promise.resolve();
    },

    _startTypewriter(element, texts, period) {
        let loopNum = 0;
        let txt = "";
        let isDeleting = false;
        const typingPeriod = parseInt(period, 10) || 2000;

        const tick = () => {
            const i = loopNum % texts.length;
            const fullTxt = texts[i];

            if (isDeleting) {
                txt = fullTxt.substring(0, txt.length - 1);
            } else {
                txt = fullTxt.substring(0, txt.length + 1);
            }

            element.innerHTML = `<span class="new_text">${txt}</span>`;

            let delta = 200 - Math.random() * 100;

            if (isDeleting) {
                delta = delta / 2;
            }

            if (!isDeleting && txt === fullTxt) {
                delta = typingPeriod;
                isDeleting = true;
            } else if (isDeleting && txt === "") {
                isDeleting = false;
                loopNum++;
                delta = 500;
            }

            const timer = setTimeout(tick, delta);
            this.timers.push(timer);
        };

        tick();
    },

    destroy() {
        if (this.timers) {
            this.timers.forEach((timer) => clearTimeout(timer));
        }

        this._super(...arguments);
    },
});