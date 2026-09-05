/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";


publicWidget.registry.BendstaBlogCarousel =
    publicWidget.Widget.extend({

    selector: ".c_bendsta_blog_cards",

    events: {
        "click .bendsta_blog_next": "_onNext",
        "click .bendsta_blog_prev": "_onPrevious",
        "click .bendsta_blog_dot": "_onDotClick",
        "mouseenter .bendsta_blog_slider": "_onMouseEnter",
        "mouseleave .bendsta_blog_slider": "_onMouseLeave",
    },


    // =========================================================
    // Start
    // =========================================================

    async start() {
        await this._super(...arguments);

        this.currentPage = 0;

        this.autoSlideDelay = 5000;

        this.autoSlideTimer = null;
        this.resizeTimer = null;


        this.viewport = this.el.querySelector(
            ".bendsta_blog_viewport"
        );

        this.track = this.el.querySelector(
            ".bendsta_blog_track"
        );

        this.dotsContainer = this.el.querySelector(
            ".bendsta_blog_dots"
        );


        this.cards = [];


        this._boundResize =
            this._onResize.bind(this);

        this._boundVisibility =
            this._onVisibilityChange.bind(this);


        if (!this.viewport || !this.track) {
            return;
        }


        // Load dynamic Blog posts
        await this._loadPosts();


        window.addEventListener(
            "resize",
            this._boundResize
        );


        document.addEventListener(
            "visibilitychange",
            this._boundVisibility
        );


        /*
         * Website Edit Mode-এ auto slide বন্ধ।
         */
        if (!this.editableMode) {
            this._startAutoSlide();
        }
    },


    // =========================================================
    // Load Posts
    // =========================================================

    async _loadPosts() {
        try {

            const limit =
                Number(
                    this.el.dataset.postLimit
                ) || 12;


            const posts =
                await rpc(
                    "/bendsta/blog/posts",
                    {
                        limit: limit,
                    }
                );


            this._renderPosts(
                Array.isArray(posts)
                    ? posts
                    : []
            );

        } catch (error) {

            console.error(
                "Bendsta Blog: unable to load posts",
                error
            );


            this.track.innerHTML = `
                <div class="bendsta_blog_message">
                    Unable to load blog posts.
                </div>
            `;
        }
    },


    // =========================================================
    // Escape HTML
    // =========================================================

    _escape(value) {

        const element =
            document.createElement("div");


        element.textContent =
            value || "";


        return element.innerHTML;
    },


    // =========================================================
    // Safe Internal URL
    // =========================================================

    _safeUrl(value) {

        if (
            typeof value === "string" &&
            value.startsWith("/")
        ) {
            return value;
        }


        return "#";
    },


    // =========================================================
    // Card Template
    // =========================================================

    _cardTemplate(post) {

        const title =
            this._escape(
                post.title
            );


        const date =
            this._escape(
                post.date
            );


        const description =
            this._escape(
                post.description
            );


        const tag =
            this._escape(
                post.tag
            );


        const authorName =
            this._escape(
                post.author?.name
            );


        const url =
            this._safeUrl(
                post.url
            );


        const coverUrl =
            this._safeUrl(
                post.cover_image
            );


        const authorImage =
            this._safeUrl(
                post.author?.image
            );


        // =============================================
        // Tag
        // =============================================

        const tagHtml =
            tag
                ? `
                    <span class="bendsta_blog_tag">
                        ${tag}
                    </span>
                `
                : "";


        // =============================================
        // Cover
        // =============================================

        const coverHtml =
            coverUrl !== "#"
                ? `
                    <img
                        src="${coverUrl}"
                        alt="${title}"
                        class="bendsta_blog_image"
                        loading="lazy"
                    />
                `
                : `
                    <div
                        class="
                            bendsta_blog_image
                            bendsta_blog_no_image
                        ">
                    </div>
                `;


        // =============================================
        // Author
        // =============================================

        const authorHtml =
            authorName
                ? `
                    <div class="bendsta_blog_author">

                        ${
                            authorImage !== "#"
                                ? `
                                    <img
                                        src="${authorImage}"
                                        alt="${authorName}"
                                        class="bendsta_blog_avatar"
                                        loading="lazy"
                                    />
                                `
                                : `
                                    <span
                                        class="
                                            bendsta_blog_avatar
                                            bendsta_blog_avatar_placeholder
                                        ">
                                        <i class="fa fa-user"></i>
                                    </span>
                                `
                        }

                        <span class="bendsta_blog_author_name">
                            ${authorName}
                        </span>

                    </div>
                `
                : `
                    <div class="bendsta_blog_author"></div>
                `;


        // =============================================
        // Complete Card
        // =============================================

        return `
            <article class="bendsta_blog_card">


                <a href="${url}"
                   class="bendsta_blog_cover">

                    ${coverHtml}

                    ${tagHtml}

                </a>


                <div class="bendsta_blog_content">


                    <div class="bendsta_blog_date">

                        <i class="fa fa-calendar"></i>

                        <span>
                            ${date}
                        </span>

                    </div>


                    <a href="${url}"
                       class="bendsta_blog_title">

                        ${title}

                    </a>


                    <p class="bendsta_blog_description">

                        ${description}

                    </p>


                    <div class="bendsta_blog_footer">


                        ${authorHtml}


                        <a href="${url}"
                           class="bendsta_blog_read_more">

                            <span>
                                Read More
                            </span>

                            <i class="fa fa-arrow-right"></i>

                        </a>


                    </div>


                </div>


            </article>
        `;
    },


    // =========================================================
    // Render Posts
    // =========================================================

    _renderPosts(posts) {

        if (!posts.length) {

            this.track.innerHTML = `
                <div class="bendsta_blog_message">
                    No published blog posts found.
                </div>
            `;


            this.cards = [];


            this._buildDots();

            this._toggleArrows(
                false
            );


            return;
        }


        this.track.innerHTML =
            posts
                .map(
                    (post) =>
                        this._cardTemplate(post)
                )
                .join("");


        this.cards =
            Array.from(
                this.track.querySelectorAll(
                    ".bendsta_blog_card"
                )
            );


        this.currentPage = 0;


        this._buildDots();

        this._updateSlider(
            false
        );


        this._toggleArrows(
            this._pageCount() > 1
        );
    },


    // =========================================================
    // Responsive
    // =========================================================

    _itemsPerPage() {

        const width =
            this.viewport.clientWidth;


        if (width < 768) {
            return 1;
        }


        if (width < 992) {
            return 2;
        }


        return 3;
    },


    // =========================================================
    // Page Count
    // =========================================================

    _pageCount() {

        if (!this.cards.length) {
            return 0;
        }


        return Math.ceil(
            this.cards.length /
            this._itemsPerPage()
        );
    },


    // =========================================================
    // Page Offset
    // =========================================================

    _pageOffset() {

        const items =
            this._itemsPerPage();


        /*
         * Actual card position ব্যবহার করছি।
         *
         * এতে CSS gap-ও automatically
         * calculation-এ চলে আসে।
         */
        if (
            this.cards.length >
            items
        ) {

            return (
                this.cards[items].offsetLeft -
                this.cards[0].offsetLeft
            );
        }


        return this.viewport.clientWidth;
    },


    // =========================================================
    // Maximum Offset
    // =========================================================

    _maxOffset() {

        return Math.max(
            0,

            this.track.scrollWidth -
            this.viewport.clientWidth
        );
    },


    // =========================================================
    // Update Slider
    // =========================================================

    _updateSlider(
        animate = true
    ) {

        const pages =
            this._pageCount();


        if (!pages) {
            return;
        }


        if (
            this.currentPage >=
            pages
        ) {
            this.currentPage = 0;
        }


        if (
            this.currentPage < 0
        ) {
            this.currentPage =
                pages - 1;
        }


        let offset =
            this._pageOffset() *
            this.currentPage;


        /*
         * Last page overflow আটকাবে।
         */
        offset =
            Math.min(
                offset,
                this._maxOffset()
            );


        this.track.style.transition =
            animate
                ? "transform 0.5s ease"
                : "none";


        this.track.style.transform =
            `translate3d(-${offset}px, 0, 0)`;


        this._updateDots();
    },


    // =========================================================
    // Build Dots
    // =========================================================

    _buildDots() {

        if (!this.dotsContainer) {
            return;
        }


        this.dotsContainer.innerHTML =
            "";


        const pages =
            this._pageCount();


        if (pages <= 1) {

            this.dotsContainer.style.display =
                "none";

            return;
        }


        this.dotsContainer.style.display =
            "flex";


        for (
            let page = 0;
            page < pages;
            page++
        ) {

            const dot =
                document.createElement(
                    "button"
                );


            dot.type =
                "button";


            dot.className =
                "bendsta_blog_dot";


            dot.dataset.page =
                String(page);


            dot.setAttribute(
                "aria-label",
                `Go to slide ${page + 1}`
            );


            if (
                page ===
                this.currentPage
            ) {

                dot.classList.add(
                    "active"
                );
            }


            this.dotsContainer.appendChild(
                dot
            );
        }
    },


    // =========================================================
    // Update Dots
    // =========================================================

    _updateDots() {

        this.el
            .querySelectorAll(
                ".bendsta_blog_dot"
            )
            .forEach(
                (dot, index) => {

                    dot.classList.toggle(
                        "active",

                        index ===
                            this.currentPage
                    );

                }
            );
    },


    // =========================================================
    // Toggle Arrows
    // =========================================================

    _toggleArrows(show) {

        this.el
            .querySelectorAll(
                ".bendsta_blog_arrow"
            )
            .forEach((arrow) => {

                arrow.style.display =
                    show
                        ? "flex"
                        : "none";

            });
    },


    // =========================================================
    // Next
    // =========================================================

    _onNext(event) {

        event.preventDefault();


        const pages =
            this._pageCount();


        if (pages <= 1) {
            return;
        }


        this.currentPage =
            (
                this.currentPage +
                1
            ) %
            pages;


        this._updateSlider(
            true
        );


        if (!this.editableMode) {
            this._restartAutoSlide();
        }
    },


    // =========================================================
    // Previous
    // =========================================================

    _onPrevious(event) {

        event.preventDefault();


        const pages =
            this._pageCount();


        if (pages <= 1) {
            return;
        }


        this.currentPage =
            (
                this.currentPage -
                1 +
                pages
            ) %
            pages;


        this._updateSlider(
            true
        );


        if (!this.editableMode) {
            this._restartAutoSlide();
        }
    },


    // =========================================================
    // Dot
    // =========================================================

    _onDotClick(event) {

        event.preventDefault();


        const page =
            Number(
                event.currentTarget.dataset.page
            );


        if (
            !Number.isInteger(page) ||
            page < 0 ||
            page >= this._pageCount()
        ) {
            return;
        }


        this.currentPage =
            page;


        this._updateSlider(
            true
        );


        if (!this.editableMode) {
            this._restartAutoSlide();
        }
    },


    // =========================================================
    // Auto Slide
    // =========================================================

    _startAutoSlide() {

        this._stopAutoSlide();


        if (
            this.editableMode ||
            this._pageCount() <= 1
        ) {
            return;
        }


        this.autoSlideTimer =
            setInterval(
                () => {

                    if (document.hidden) {
                        return;
                    }


                    const pages =
                        this._pageCount();


                    if (pages <= 1) {
                        return;
                    }


                    this.currentPage =
                        (
                            this.currentPage +
                            1
                        ) %
                        pages;


                    this._updateSlider(
                        true
                    );

                },

                this.autoSlideDelay
            );
    },


    // =========================================================
    // Stop Auto Slide
    // =========================================================

    _stopAutoSlide() {

        if (!this.autoSlideTimer) {
            return;
        }


        clearInterval(
            this.autoSlideTimer
        );


        this.autoSlideTimer =
            null;
    },


    // =========================================================
    // Restart Auto Slide
    // =========================================================

    _restartAutoSlide() {

        this._stopAutoSlide();

        this._startAutoSlide();
    },


    // =========================================================
    // Hover
    // =========================================================

    _onMouseEnter() {

        if (!this.editableMode) {
            this._stopAutoSlide();
        }
    },


    _onMouseLeave() {

        if (!this.editableMode) {
            this._startAutoSlide();
        }
    },


    // =========================================================
    // Visibility
    // =========================================================

    _onVisibilityChange() {

        if (this.editableMode) {
            return;
        }


        if (document.hidden) {

            this._stopAutoSlide();

        } else {

            this._startAutoSlide();

        }
    },


    // =========================================================
    // Resize
    // =========================================================

    _onResize() {

        clearTimeout(
            this.resizeTimer
        );


        this.resizeTimer =
            setTimeout(
                () => {

                    this.currentPage = 0;


                    this._buildDots();


                    this._updateSlider(
                        false
                    );


                    this._toggleArrows(
                        this._pageCount() > 1
                    );


                    if (
                        !this.editableMode
                    ) {
                        this._restartAutoSlide();
                    }

                },

                150
            );
    },


    // =========================================================
    // Destroy
    // =========================================================

    destroy() {

        this._stopAutoSlide();


        clearTimeout(
            this.resizeTimer
        );


        if (this._boundResize) {

            window.removeEventListener(
                "resize",
                this._boundResize
            );

        }


        if (this._boundVisibility) {

            document.removeEventListener(
                "visibilitychange",
                this._boundVisibility
            );

        }


        return this._super(
            ...arguments
        );
    },
});