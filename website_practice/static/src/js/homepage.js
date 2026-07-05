// mouse parallax effect for body

const wrap = document.getElementById('wrap');
const image = document.querySelector('.parallax-image');

wrap.addEventListener('mousemove', (e) => {
    const x = (e.clientX / window.innerWidth - 0.5) * 200;
    const y = (e.clientY / window.innerHeight - 0.5) * 200;

    image.style.transform = `translate(${x}px, ${y}px)`;
});


// type write animation

(function () {

    var TxtType = function (el, toRotate, period) {
        this.toRotate = toRotate;
        this.el = el;
        this.loopNum = 0;
        this.period = parseInt(period, 10) || 2000;
        this.txt = '';
        this.isDeleting = false;
        this.tick();
    };

    TxtType.prototype.tick = function () {
        var i = this.loopNum % this.toRotate.length;
        var fullTxt = this.toRotate[i];

        this.txt = this.isDeleting
            ? fullTxt.substring(0, this.txt.length - 1)
            : fullTxt.substring(0, this.txt.length + 1);

        this.el.innerHTML = '<span class="wrap">' + this.txt + '</span>';

        var that = this;
        var delta = 200 - Math.random() * 100;
        if (this.isDeleting) delta /= 2;

        if (!this.isDeleting && this.txt === fullTxt) {
            delta = this.period;
            this.isDeleting = true;
        } else if (this.isDeleting && this.txt === '') {
            this.isDeleting = false;
            this.loopNum++;
            delta = 500;
        }

        setTimeout(function () { that.tick(); }, delta);
    };

    function init() {
        var elements = document.getElementsByClassName('typewrite');
        for (var i = 0; i < elements.length; i++) {
            var toRotate = elements[i].getAttribute('data-type');
            var period = elements[i].getAttribute('data-period');
            if (toRotate) {
                new TxtType(elements[i], JSON.parse(toRotate), period);
            }
        }

        var css = document.createElement('style');
        css.innerHTML = '.typewrite > .wrap { border-right: 0.08em solid #fff }';
        document.head.appendChild(css);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();




// success animation

console.log("hello shawon")
var els = document.querySelectorAll(".right_to_left_animation");

if (!els.length) return;

var observer = new IntersectionObserver(
    function (entries, obs) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add("aux-animated");
                obs.unobserve(entry.target);
            }
        });
    },
    {
        threshold: 0.2,
    }
);

els.forEach(function (el) {
    observer.observe(el);
});
