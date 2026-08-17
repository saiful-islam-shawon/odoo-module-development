/** @odoo-module **/

import { Component, onWillStart, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadJS, loadCSS } from "@web/core/assets";

export class MapLearning extends Component {
    static template = "map_learning.MapLearningTemplate";

    setup() {
        this.mapRef = useRef("mapContainer");
        this.map = null;
        this.userMarker = null;

        onWillStart(async () => {
            try {
                await loadCSS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css");
                await loadJS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js");
            } catch (err) {
                console.error("Leaflet Load Failed:", err);
            }
        });

        onMounted(() => {
            setTimeout(() => {
                this.renderLeafletMap();
            }, 300);
        });
    }

    renderLeafletMap() {
        const container = this.mapRef.el;
        if (!container || typeof L === "undefined") return;

        // ডিফোল্ট ম্যাপ (ঢাকা কেন্দ্রিক)
        this.map = L.map(container).setView([23.8103, 90.4125], 12);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(this.map);

        setTimeout(() => {
            this.map.invalidateSize();
        }, 200);
    }

    // লাইভ লোকেশন বের করার ফাংশন
    locateUser() {
        if (!("geolocation" in navigator)) {
            alert("আপনার ব্রাউজারে Geolocation সাপোর্ট করে না।");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;

                // ১. ম্যাপকে ইউজারের লাইভ পজিশনে ফোকাস করা (Zoom level: 16)
                this.map.setView([lat, lng], 16);

                // ২. আগের মার্কার থাকলে তা রিমুভ করে নতুন পিন বসানো
                if (this.userMarker) {
                    this.map.removeLayer(this.userMarker);
                }

                // ৩. নতুন লোকেশনে পিন ও পপআপ সেট করা
                this.userMarker = L.marker([lat, lng]).addTo(this.map);
                this.userMarker.bindPopup(`<b>আপনার বর্তমান অবস্থান</b><br/>Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`).openPopup();
            },
            (error) => {
                alert("লোকেশন পাওয়া যায়নি: " + error.message);
            },
            { enableHighAccuracy: true }
        );
    }
}

registry.category("actions").add("map_learning_action", MapLearning);




