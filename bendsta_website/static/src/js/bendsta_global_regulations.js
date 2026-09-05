/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";


publicWidget.registry.BendstaGlobalRegulations =
    publicWidget.Widget.extend({

        selector: ".s_bendsta_global_regulations",

        events: {
            "click .bendsta-global-country": "_onCountryClick",
        },


        start() {

            this.countryData = {

                uk: {
                    region: "Europe",
                    title: "United Kingdom (NHS & PHE / UKHSA)",
                    status: "Proactive THR Integration",

                    description:
                        "The UK Government launched the groundbreaking " +
                        "'Swap to Stop' scheme, providing 1 million adult " +
                        "smokers with free vape starter kits. Public Health " +
                        "England (now UKHSA) has consistently affirmed that " +
                        "vaping is at least 95% less harmful than smoking.",

                    safeguards:
                        "Strict 20mg/ml nicotine caps under TRPR, " +
                        "child-resistant caps, full toxicological " +
                        "notification to MHRA, and total ban on sales " +
                        "to minors.",

                    metric: "~11.9%",

                    metricText:
                        "Adult smoking rates have dropped to historic " +
                        "record lows across England and Wales.",
                },


                nz: {
                    region: "Oceania",
                    title: "New Zealand (Ministry of Health)",
                    status: "Smokefree 2025 Core Strategy",

                    description:
                        "New Zealand explicitly legislated vaping as a " +
                        "smoking cessation mechanism to reach its " +
                        "Smokefree 2025 target. Adult smokers are supported " +
                        "with regulated retail vape outlets while combustible " +
                        "tobacco supply is restricted.",

                    safeguards:
                        "Strict notification scheme for all devices, " +
                        "mandatory flavor restrictions in generic retail, " +
                        "with specialty vape shops reserved for adult " +
                        "cessation advice.",

                    metric: "6.8%",

                    metricText:
                        "Daily smoking among adult New Zealanders halved " +
                        "in under five years.",
                },


                se: {
                    region: "Europe",
                    title: "Sweden (The Scandinavian Model)",
                    status: "Smoke-Free Target Met (<5%)",

                    description:
                        "Sweden approved both Snus and modern nicotine " +
                        "pouches alongside regulated vaping. Consequently, " +
                        "Sweden reached very low smoking prevalence compared " +
                        "with many European countries.",

                    safeguards:
                        "Rigorous product standards, nicotine testing, " +
                        "consumer protections, and legal categorization " +
                        "distinct from combustible smoking.",

                    metric: "4.5%",

                    metricText:
                        "Sweden reports one of the lowest smoking " +
                        "prevalence rates in Europe.",
                },


                ca: {
                    region: "North America",
                    title: "Canada (Health Canada)",
                    status: "Federal Regulated Framework",

                    description:
                        "Canada regulates vaping under the Tobacco and " +
                        "Vaping Products Act, applying federal product, " +
                        "packaging, promotion, and youth-access controls.",

                    safeguards:
                        "Federal nicotine concentration requirements, " +
                        "child-resistant packaging standards, labeling, " +
                        "and restrictions on youth access.",

                    metric: "10.9%",

                    metricText:
                        "Canada maintains a regulated framework for adult " +
                        "access alongside tobacco-control measures.",
                },


                fr: {
                    region: "Europe",
                    title: "France",
                    status: "Regulated European Market",

                    description:
                        "France regulates electronic cigarettes within " +
                        "European and national tobacco-control rules while " +
                        "maintaining legal access for adults.",

                    safeguards:
                        "EU TPD compliant products, packaging requirements, " +
                        "advertising restrictions, and age controls.",

                    metric: "4M+",

                    metricText:
                        "Millions of French adults report using electronic " +
                        "cigarettes.",
                },


                my: {
                    region: "Asia",
                    title: "Malaysia",
                    status: "Legal Regulation & Taxation",

                    description:
                        "Malaysia has moved toward formal regulation and " +
                        "taxation of nicotine vaping products as part of " +
                        "its evolving tobacco-control framework.",

                    safeguards:
                        "Product requirements, excise controls, retail " +
                        "rules, and restrictions relating to youth access.",

                    metric: "Regulated",

                    metricText:
                        "The sector is increasingly incorporated into " +
                        "formal regulatory and fiscal systems.",
                },


                id: {
                    region: "Asia",
                    title: "Indonesia",
                    status: "Formal Excise Model",

                    description:
                        "Indonesia applies excise duties to vaping products " +
                        "and recognizes the sector within its legal and " +
                        "fiscal framework.",

                    safeguards:
                        "Excise stamps, regulatory requirements, product " +
                        "controls, and age-related restrictions.",

                    metric: "Excise",

                    metricText:
                        "Vaping products operate within a formal excise " +
                        "and regulatory structure.",
                },


                us: {
                    region: "North America",
                    title: "United States (FDA)",
                    status: "Premarket Authorization",

                    description:
                        "The U.S. Food and Drug Administration regulates " +
                        "electronic nicotine delivery systems and operates " +
                        "a premarket tobacco product review pathway.",

                    safeguards:
                        "Premarket review, manufacturing requirements, " +
                        "marketing restrictions, warning labels, and " +
                        "prohibition of sales to minors.",

                    metric: "FDA",

                    metricText:
                        "Products are subject to federal tobacco-product " +
                        "regulation and authorization requirements.",
                },


                eu: {
                    region: "European Union",
                    title: "European Union (Tobacco Products Directive)",
                    status: "Multi-Nation Regulatory Framework",

                    description:
                        "The EU Tobacco Products Directive establishes " +
                        "harmonized requirements for electronic cigarettes " +
                        "across member states.",

                    safeguards:
                        "Nicotine limits, container requirements, " +
                        "notifications, safety mechanisms, labeling, " +
                        "and consumer-information rules.",

                    metric: "27 Nations",

                    metricText:
                        "A common regulatory baseline applies across " +
                        "European Union member states.",
                },
            };

            return this._super(...arguments);
        },


        _onCountryClick(ev) {

            ev.preventDefault();

            const button = ev.currentTarget;
            const key = button.dataset.country;
            const data = this.countryData[key];

            if (!data) {
                return;
            }


            /*
             * Active country
             */

            this.el
                .querySelectorAll(".bendsta-global-country")
                .forEach((item) => {
                    item.classList.remove("is-active");
                });

            button.classList.add("is-active");


            /*
             * Update this snippet only
             */

            this._setText("region", data.region);
            this._setText("title", data.title);
            this._setText("status", data.status);
            this._setText("description", data.description);
            this._setText("safeguards", data.safeguards);
            this._setText("metric", data.metric);
            this._setText("metric-text", data.metricText);
        },


        _setText(role, value) {

            const element =
                this.el.querySelector(
                    `[data-role="${role}"]`
                );

            if (element) {
                element.textContent = value;
            }
        },
    });