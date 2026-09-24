from odoo.http import request, route
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
)
from odoo.tools import html2plaintext
from werkzeug.exceptions import Forbidden, NotFound


class FakirCustomerPortal(CustomerPortal):

    # =========================================================
    # PORTAL HOME
    # =========================================================

    def _prepare_home_portal_values(self, counters):

        values = super()._prepare_home_portal_values(counters)

        user = request.env.user

        has_crm_access = (
            user.has_group(
                "fakir_portal_management.group_crm_website_access"
            )
            or user.has_group("base.group_system")
        )

        values["has_crm_portal_access"] = has_crm_access

        if has_crm_access:

            values["crm_opportunity_count"] = (
                request.env["crm.lead"]
                .sudo()
                .search_count([
                    ("type", "=", "opportunity"),
                ])
            )

        else:

            values["crm_opportunity_count"] = 0

        return values


    # =========================================================
    # CHECK CRM PORTAL ACCESS
    # =========================================================

    def _check_crm_portal_access(self):

        user = request.env.user

        has_crm_access = (
            user.has_group(
                "fakir_portal_management.group_crm_website_access"
            )
            or user.has_group("base.group_system")
        )

        if not has_crm_access:
            raise Forbidden()


    # =========================================================
    # OPPORTUNITY LIST
    # =========================================================

    @route(
        [
            "/my/crm/opportunities",
            "/my/crm/opportunities/page/<int:page>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_crm_opportunities(
        self,
        page=1,
        sortby=None,
        **kw,
    ):

        self._check_crm_portal_access()

        Opportunity = request.env["crm.lead"]

        sortings = {

            "date": {
                "label": "Newest",
                "order": "create_date desc",
            },

            "name": {
                "label": "Opportunity",
                "order": "name",
            },

            "revenue": {
                "label": "Expected Revenue",
                "order": "expected_revenue desc",
            },
        }

        if not sortby or sortby not in sortings:
            sortby = "date"

        order = sortings[sortby]["order"]

        domain = [
            ("type", "=", "opportunity"),
        ]

        opportunity_count = (
            Opportunity
            .sudo()
            .search_count(domain)
        )

        pager_values = portal_pager(
            url="/my/crm/opportunities",
            url_args={
                "sortby": sortby,
            },
            total=opportunity_count,
            page=page,
            step=self._items_per_page,
        )

        opportunities = (
            Opportunity
            .sudo()
            .search(
                domain,
                order=order,
                limit=self._items_per_page,
                offset=pager_values["offset"],
            )
        )

        values = {

            "opportunities": opportunities,

            "page_name": "crm_opportunity",

            "pager": pager_values,

            "sortby": sortby,

            "sortings": sortings,

            "default_url": "/my/crm/opportunities",
        }

        return request.render(
            "fakir_portal_management.portal_my_crm_opportunities",
            values,
        )


    # =========================================================
    # GET OPPORTUNITY
    # =========================================================

    def _get_crm_opportunity(self, opportunity_id):

        opportunity = (
            request.env["crm.lead"]
            .sudo()
            .browse(opportunity_id)
        )

        if (
            not opportunity.exists()
            or opportunity.type != "opportunity"
        ):
            raise NotFound()

        return opportunity


    # =========================================================
    # OPPORTUNITY DETAIL / EDIT
    # =========================================================

    @route(
        ["/my/crm/opportunities/<int:opportunity_id>"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def portal_crm_opportunity_detail(
        self,
        opportunity_id,
        **kw,
    ):

        self._check_crm_portal_access()

        opportunity = self._get_crm_opportunity(
            opportunity_id
        )

        success = False


        # =====================================================
        # QUICK STAGE CHANGE
        # =====================================================

        if (
            request.httprequest.method == "GET"
            and kw.get("stage_id")
        ):

            opportunity.sudo().write({
                "stage_id": int(
                    kw["stage_id"]
                ),
            })

            return request.redirect(
                "/my/crm/opportunities/%s"
                % opportunity.id
            )


        # =====================================================
        # UPDATE OPPORTUNITY
        # =====================================================

        if request.httprequest.method == "POST":

            expected_revenue = (
                kw.get("expected_revenue")
                or 0.0
            )

            try:

                expected_revenue = float(
                    expected_revenue
                )

            except (TypeError, ValueError):

                expected_revenue = (
                    opportunity.expected_revenue
                )


            tag_ids = (
                request.httprequest.form
                .getlist("tag_ids")
            )


            def _int_or_false(value):

                try:
                    return int(value)

                except (TypeError, ValueError):
                    return False


            vals = {

                # ==============================
                # BASIC / NOTES
                # ==============================

                "name": (
                    kw.get("name")
                    or opportunity.name
                ),

                "contact_name": kw.get(
                    "contact_name"
                ),

                "email_from": kw.get(
                    "email_from"
                ),

                "phone": kw.get(
                    "phone"
                ),

                "expected_revenue": (
                    expected_revenue
                ),

                "date_deadline": (
                    kw.get("date_deadline")
                    or False
                ),

                "description": kw.get(
                    "description"
                ),

                "tag_ids": [
                    (
                        6,
                        0,
                        [
                            int(tag)
                            for tag in tag_ids
                        ],
                    )
                ],


                # ==============================
                # COMPANY INFORMATION
                # ==============================

                "partner_name": kw.get(
                    "partner_name"
                ),

                "street": kw.get(
                    "street"
                ),

                "street2": kw.get(
                    "street2"
                ),

                "city": kw.get(
                    "city"
                ),

                "zip": kw.get(
                    "zip"
                ),

                "state_id": _int_or_false(
                    kw.get("state_id")
                ),

                "country_id": _int_or_false(
                    kw.get("country_id")
                ),


                # ==============================
                # CONTACT INFORMATION
                # ==============================

                "function": kw.get(
                    "function"
                ),

                "website": kw.get(
                    "website"
                ),


                # ==============================
                # MARKETING
                # ==============================

                "campaign_id": _int_or_false(
                    kw.get("campaign_id")
                ),

                "medium_id": _int_or_false(
                    kw.get("medium_id")
                ),

                "source_id": _int_or_false(
                    kw.get("source_id")
                ),

                "referred": kw.get(
                    "referred"
                ),


                # ==============================
                # OWNERSHIP
                # ==============================

                "team_id": _int_or_false(
                    kw.get("team_id")
                ),
            }


            opportunity.sudo().write(vals)

            success = True


        # =====================================================
        # TEMPLATE VALUES
        # =====================================================

        values = {

            "opportunity": opportunity,

            "description_plain": html2plaintext(
                opportunity.description or ""
            ),


            # ==============================
            # CRM DATA
            # ==============================

            "stages": (
                request.env["crm.stage"]
                .sudo()
                .search(
                    [],
                    order="sequence",
                )
            ),

            "all_tags": (
                request.env["crm.tag"]
                .sudo()
                .search(
                    [],
                    order="name",
                )
            ),

            "crm_countries": (
                request.env["res.country"]
                .sudo()
                .search(
                    [],
                    order="name",
                )
            ),

            "crm_states": (
                request.env["res.country.state"]
                .sudo()
                .search(
                    [],
                    order="name",
                )
            ),

            "crm_campaigns": (
                request.env["utm.campaign"]
                .sudo()
                .search(
                    [],
                    order="name",
                )
            ),

            "crm_mediums": (
                request.env["utm.medium"]
                .sudo()
                .search(
                    [],
                    order="name",
                )
            ),

            "crm_sources": (
                request.env["utm.source"]
                .sudo()
                .search(
                    [],
                    order="name",
                )
            ),

            "crm_teams": (
                request.env["crm.team"]
                .sudo()
                .search(
                    [],
                    order="name",
                )
            ),


            # ==============================
            # CHATTER MESSAGES
            # ==============================

            "messages": (
                opportunity.message_ids
            ),


            # ==============================
            # ACTIVITIES
            # ==============================

            "activities": (
                opportunity.activity_ids
            ),

            "activity_types": (
                request.env[
                    "mail.activity.type"
                ]
                .sudo()
                .search(
                    [],
                    order="sequence, id",
                )
            ),

            "activity_users": (
                request.env[
                    "res.users"
                ]
                .sudo()
                .search(
                    [
                        ("active", "=", True),
                        ("share", "=", False),
                    ],
                    order="name",
                )
            ),


            # ==============================
            # OTHER
            # ==============================

            "success": success,

            "page_name": (
                "crm_opportunity_detail"
            ),
        }


        return request.render(
            "fakir_portal_management."
            "portal_my_crm_opportunity_detail",
            values,
        )


    # =========================================================
    # CHATTER - POST MESSAGE
    # =========================================================

    @route(
        [
            "/my/crm/opportunities/"
            "<int:opportunity_id>/post_message"
        ],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_crm_opportunity_post_message(
        self,
        opportunity_id,
        **kw,
    ):

        self._check_crm_portal_access()

        opportunity = (
            self._get_crm_opportunity(
                opportunity_id
            )
        )

        message_body = (
            kw.get("message_body")
            or ""
        ).strip()


        if message_body:

            opportunity.sudo().message_post(

                body=message_body,

                message_type="comment",

                subtype_xmlid="mail.mt_comment",
            )


        return request.redirect(
            "/my/crm/opportunities/%s"
            % opportunity.id
        )


    # =========================================================
    # ACTIVITY - SCHEDULE ACTIVITY
    # =========================================================

    @route(
        [
            "/my/crm/opportunities/"
            "<int:opportunity_id>/schedule_activity"
        ],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_crm_opportunity_schedule_activity(
        self,
        opportunity_id,
        **kw,
    ):

        # -----------------------------------------
        # Check CRM portal permission
        # -----------------------------------------

        self._check_crm_portal_access()


        # -----------------------------------------
        # Get Opportunity
        # -----------------------------------------

        opportunity = (
            self._get_crm_opportunity(
                opportunity_id
            )
        )


        # -----------------------------------------
        # Get form data
        # -----------------------------------------

        activity_type_id = kw.get(
            "activity_type_id"
        )

        summary = (
            kw.get("summary")
            or ""
        ).strip()

        note = (
            kw.get("note")
            or ""
        ).strip()

        date_deadline = kw.get(
            "date_deadline"
        )

        user_id = kw.get(
            "user_id"
        )


        # -----------------------------------------
        # Convert Activity Type ID
        # -----------------------------------------

        try:

            activity_type_id = int(
                activity_type_id
            )

        except (TypeError, ValueError):

            activity_type_id = False


        # -----------------------------------------
        # Convert User ID
        # -----------------------------------------

        try:

            user_id = int(
                user_id
            )

        except (TypeError, ValueError):

            user_id = False


        # -----------------------------------------
        # Required validation
        # -----------------------------------------

        if (
            not activity_type_id
            or not date_deadline
        ):

            return request.redirect(
                "/my/crm/opportunities/%s"
                % opportunity.id
            )


        # -----------------------------------------
        # Default Assigned User
        # -----------------------------------------

        if not user_id:

            if opportunity.user_id:

                user_id = (
                    opportunity.user_id.id
                )

            else:

                user_id = (
                    request.env.user.id
                )


        # -----------------------------------------
        # Get CRM Lead Model
        # -----------------------------------------

        crm_lead_model = (
            request.env["ir.model"]
            .sudo()
            ._get("crm.lead")
        )


        # -----------------------------------------
        # Create Activity
        # -----------------------------------------

        request.env[
            "mail.activity"
        ].sudo().create({

            "activity_type_id": (
                activity_type_id
            ),

            "summary": (
                summary or False
            ),

            "note": (
                note or False
            ),

            "date_deadline": (
                date_deadline
            ),

            "user_id": (
                user_id
            ),

            "res_model_id": (
                crm_lead_model.id
            ),

            "res_id": (
                opportunity.id
            ),
        })


        # -----------------------------------------
        # Back to Opportunity
        # -----------------------------------------

        return request.redirect(
            "/my/crm/opportunities/%s"
            % opportunity.id
        )