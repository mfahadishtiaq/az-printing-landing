/* AZ Printing & Signs, the motion layer (2026-10-05).

   Three things, in order of weight:
   1. Lenis smooth scroll, lerp .1, sharing GSAP's clock (the house standard:
      ZEF's stepper). Without it a trackpad delivers scroll in steps and every
      reveal steps with it.
   2. The hero set piece: each product in the collage is its own cut-out
      (rendered from the client's PSD), so they rise in one after another and
      then stay still; the background ribbon drifts instead (CSS). One loud
      moment, at the top, nowhere else.
   3. Reveals below the fold, ONE ITEM AT A TIME: each item fires on its own
      visibility, through a queue with a minimum gap, so a row reads as a
      sequence and never as one event (Fahad's ruling, 2026-09-03).

   Off switches: prefers-reduced-motion, `?motion=off`, or GSAP failing to
   load. Each leaves the page in its final, fully visible state. */
(function () {
  var html = document.documentElement;
  var editing = /[?&]edit=1\b/.test(location.search);
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    || /[?&]motion=off\b/.test(location.search) || editing;
  if (editing) {
    var es = document.createElement('script');
    es.src = document.querySelector('script[src$="motion.js"]').src.replace('motion.js', 'edit.js');
    document.body.appendChild(es);
  }
  var head = document.querySelector('.head');

  function headerState(y) {
    if (head) head.classList.toggle('is-scrolled', y > 8);
  }

  /* ?demo=<name> pins one item in its hover state, so a headless capture can
     show what a hover looks like (the pane cannot hover and keep it) */
  var demo = /[?&]demo=([a-z0-9-]+)/.exec(location.search);
  if (demo) {
    var target = document.querySelector('.hero-item[data-name="' + demo[1] + '"]');
    if (target) { target.classList.add('is-hover'); target.closest('.hero').classList.add('has-hover'); }
  }

  /* ?swirl=<seconds> freezes the background ribbon at that moment of its
     loop (negative animation-delay, paused), so a capture can show a phase */
  var sw = /[?&]swirl=([0-9.]+)/.exec(location.search);
  if (sw) {
    document.querySelectorAll('.hero-swirl').forEach(function (el) {
      el.style.animationDelay = '-' + sw[1] + 's';
      el.style.animationPlayState = 'paused';
    });
  }

  if (reduce || !window.gsap || !window.Lenis) {
    html.classList.remove('pre');
    html.classList.add('motion-done');
    window.addEventListener('scroll', function () { headerState(window.scrollY); }, { passive: true });
    headerState(window.scrollY);
    return;
  }

  html.classList.add('motion');
  gsap.registerPlugin(ScrollTrigger);

  /* 1. smooth scroll, one clock */
  var lenis = new Lenis({ lerp: 0.1, smoothWheel: true, anchors: true });
  window.__lenis = lenis;  // js/site.js stops it while the phone menu is open
  lenis.on('scroll', function (e) { ScrollTrigger.update(); headerState(e.scroll); });
  gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
  gsap.ticker.lagSmoothing(0);
  headerState(window.scrollY);

  /* 2. the hero */
  var items = gsap.utils.toArray('.hero-item');
  var words = gsap.utils.toArray('.hero h1 .w');
  var list = gsap.utils.toArray('.hero-list li, .hero-ctas');  // the two buttons enter as ONE block, never offset
  var eyebrow = document.querySelector('.hero-eyebrow');
  html.classList.remove('pre');
  var hasHero = !!document.querySelector('.hero');
  var tl = gsap.timeline({ defaults: { ease: 'power3.out' }, paused: !hasHero });
  if (hasHero) {
  if (eyebrow) tl.from(eyebrow, { y: 14, opacity: 0, duration: 0.6 }, 0);
  tl.from(words, { y: 40, opacity: 0, duration: 0.8, stagger: 0.06 }, 0.1)
    .from(list, { y: 18, opacity: 0, duration: 0.6, stagger: 0.08 }, 0.4)
    .from(items, { y: 70, scale: 0.94, opacity: 0, duration: 1, stagger: 0.09 }, 0.15)
    .from('.hero-quality', { opacity: 0, duration: 0.6 }, 1.2)
    .add(afterEntrance);
  }  // product pages have no hero: nothing to enter, no GSAP target warnings

  function afterEntrance() {
    // The products stay STILL after they arrive (Fahad, 2026-10-05 night): no
    // idle drift, no pointer parallax, no scroll parallax. The background
    // ribbon carries the motion (CSS keyframes on .hero-swirl). What remains
    // on the products is their hover response. The cursor light stays.
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      var hero = document.querySelector('.hero');
      hero.classList.add('has-light');
      hero.addEventListener('pointermove', function (e) {
        var r = hero.getBoundingClientRect();
        hero.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(2) + '%');
        hero.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(2) + '%');
      });
      items.forEach(function (el) {
        var lift = el.querySelector('.hero-lift');
        el.addEventListener('pointermove', function (e) {
          var r = el.getBoundingClientRect();
          var px = (e.clientX - r.left) / r.width - 0.5;
          var py = (e.clientY - r.top) / r.height - 0.5;
          lift.style.setProperty('--ry', (px * 14).toFixed(2) + 'deg');
          lift.style.setProperty('--rx', (-py * 14).toFixed(2) + 'deg');
        });
        el.addEventListener('pointerleave', function () {
          lift.style.setProperty('--ry', '0deg');
          lift.style.setProperty('--rx', '0deg');
        });
      });
    }
  }

  /* gentle accents tied to scroll (transform only, small travel) */
  var photo = document.querySelector('.welcome-photo img');
  if (photo) {
    gsap.fromTo(photo, { yPercent: -6 }, {
      yPercent: 6, ease: 'none',
      scrollTrigger: { trigger: '.welcome-photo', start: 'top bottom', end: 'bottom top', scrub: true }
    });
  }
  var sloganLines = gsap.utils.toArray('.slogan .line');
  sloganLines.forEach(function (line, i) {
    gsap.fromTo(line, { xPercent: i ? 2.5 : -2.5 }, {
      xPercent: i ? -2.5 : 2.5, ease: 'none',
      scrollTrigger: { trigger: '.slogan', start: 'top bottom', end: 'bottom top', scrub: true }
    });
  });

  /* 3. reveals, one by one */
  var GAP = 260, last = 0;
  function schedule(el) {
    var now = performance.now();
    var at = Math.max(now, last + GAP);
    last = at;
    setTimeout(function () { el.classList.add('is-in'); }, at - now);
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { io.unobserve(e.target); schedule(e.target); }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -18% 0px' });
  document.querySelectorAll('[data-reveal]').forEach(function (el) { io.observe(el); });

  /* the form's thank-you line, when FormSubmit sends the visitor back */
  if (location.search.indexOf('sent=1') > -1) {
    var s = document.getElementById('form-sent');
    if (s) { s.classList.add('show'); lenis.scrollTo(s, { offset: -120 }); }
  }
})();
