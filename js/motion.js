/* AZ Printing & Signs, the motion layer (2026-10-05).

   Three things, in order of weight:
   1. Lenis smooth scroll, lerp .1, sharing GSAP's clock (the house standard:
      ZEF's stepper). Without it a trackpad delivers scroll in steps and every
      reveal steps with it.
   2. The hero set piece: each product in the collage is its own cut-out
      (rendered from the client's PSD), so they rise in one after another,
      drift with the pointer by depth, and slide up at different rates as the
      hero scrolls away. One loud moment, at the top, nowhere else.
   3. Reveals below the fold, ONE ITEM AT A TIME: each item fires on its own
      visibility, through a queue with a minimum gap, so a row reads as a
      sequence and never as one event (Fahad's ruling, 2026-09-03).

   Off switches: prefers-reduced-motion, `?motion=off`, or GSAP failing to
   load. Each leaves the page in its final, fully visible state. */
(function () {
  var html = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    || /[?&]motion=off\b/.test(location.search);
  var head = document.querySelector('.head');

  function headerState(y) {
    if (head) head.classList.toggle('is-scrolled', y > 8);
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
  lenis.on('scroll', function (e) { ScrollTrigger.update(); headerState(e.scroll); });
  gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
  gsap.ticker.lagSmoothing(0);
  headerState(window.scrollY);

  /* 2. the hero */
  var items = gsap.utils.toArray('.hero-item');
  var words = gsap.utils.toArray('.hero h1 .w');
  var list = gsap.utils.toArray('.hero-list li');
  html.classList.remove('pre');
  var tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
  tl.from(words, { y: 40, opacity: 0, duration: 0.8, stagger: 0.06 }, 0)
    .from(list, { y: 18, opacity: 0, duration: 0.6, stagger: 0.08 }, 0.4)
    .from(items, { y: 70, scale: 0.94, opacity: 0, duration: 1, stagger: 0.09 }, 0.15)
    .from('.hero-quality', { opacity: 0, duration: 0.6 }, 1.2)
    .add(afterEntrance);

  function afterEntrance() {
    // idle drift on the picture itself, never on the positioned box
    items.forEach(function (el, i) {
      var img = el.querySelector('img');
      gsap.to(img, { y: 4 + (i % 3) * 2, duration: 3.4 + (i % 4) * 0.5, yoyo: true, repeat: -1, ease: 'sine.inOut' });
    });
    // scroll: the collage slides up faster than the page, by depth
    items.forEach(function (el) {
      var depth = parseFloat(el.getAttribute('data-depth')) || 0.5;
      gsap.to(el, {
        y: -90 * depth, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
      });
    });
    // pointer: a small parallax on the inner wrapper, fine pointers only
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      var movers = items.map(function (el) {
        var depth = parseFloat(el.getAttribute('data-depth')) || 0.5;
        var wrap = el.querySelector('.hero-float');
        return { x: gsap.quickTo(wrap, 'x', { duration: 0.9, ease: 'power2.out' }),
                 y: gsap.quickTo(wrap, 'y', { duration: 0.9, ease: 'power2.out' }), depth: depth };
      });
      var hero = document.querySelector('.hero');
      hero.addEventListener('pointermove', function (e) {
        var r = hero.getBoundingClientRect();
        var dx = (e.clientX - r.left) / r.width - 0.5;
        var dy = (e.clientY - r.top) / r.height - 0.5;
        movers.forEach(function (m) { m.x(dx * 28 * m.depth); m.y(dy * 18 * m.depth); });
      });
      hero.addEventListener('pointerleave', function () {
        movers.forEach(function (m) { m.x(0); m.y(0); });
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
