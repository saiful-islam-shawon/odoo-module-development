# -*- coding: utf-8 -*-

import json
import re

from odoo import http
from odoo.http import request


class BendstaBlogController(http.Controller):

    @http.route(
        "/bendsta/blog/posts",
        type="jsonrpc",
        auth="public",
        website=True,
    )
    def get_blog_posts(self, limit=12):
        # ==========================================
        # Limit
        # ==========================================

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 12

        limit = max(1, min(limit, 30))


        # ==========================================
        # Published Blog Posts
        # ==========================================

        posts = request.env["blog.post"].sudo().search(
            [
                ("website_published", "=", True),
            ],
            order="post_date desc, id desc",
            limit=limit,
        )


        result = []


        for post in posts:

            # ======================================
            # Cover Properties
            # ======================================

            cover_properties = {}

            if post.cover_properties:
                try:
                    cover_properties = json.loads(
                        post.cover_properties
                    )
                except (TypeError, ValueError, json.JSONDecodeError):
                    cover_properties = {}


            background_image = (
                cover_properties.get("background-image")
                or ""
            )


            # ======================================
            # Extract actual /web/image/... URL
            #
            # Example:
            #
            # url("/web/image/798-xxx/image.webp")
            #
            # becomes:
            #
            # /web/image/798-xxx/image.webp
            # ======================================

            cover_url = ""

            if background_image:

                match = re.search(
                    r"""url\(["']?(.*?)["']?\)""",
                    background_image,
                )

                if match:
                    cover_url = match.group(1)


            # ======================================
            # First Tag
            # ======================================

            tag = post.tag_ids[:1]


            # ======================================
            # Author
            # ======================================

            author = post.author_id


            # ======================================
            # Result
            # ======================================

            result.append({
                "id": post.id,

                "title": post.name or "",

                "url": post.website_url or "#",

                "date": (
                    post.post_date.strftime(
                        "%d %B %Y"
                    )
                    if post.post_date
                    else ""
                ),

                "description": (
                    post.subtitle
                    or post.website_meta_description
                    or ""
                ),

                "tag": (
                    tag.name
                    if tag
                    else ""
                ),

                "cover_image": cover_url,

                "author": {
                    "name": (
                        author.name
                        if author
                        else ""
                    ),

                    "image": (
                        f"/web/image/res.partner/"
                        f"{author.id}/avatar_128"
                        if author
                        else ""
                    ),
                },
            })


        return result