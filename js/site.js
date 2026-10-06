/* AZ Printing & Signs, site interactions (2026-10-05): the Products mega
   menu, the phone menu sheet, the catalogue tabs and the 3D card tilt.
   Independent of motion.js; everything works with motion off, only the tilt
   is skipped under reduced motion or on touch. */
(function () {
  var html = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  function lenis(cmd) { if (window.__lenis && window.__lenis[cmd]) window.__lenis[cmd](); }

  /* ---------- mega menu ---------- */
  var ddBtn = document.querySelector('.menu-dd');
  var mega = document.getElementById('mega');
  var head = document.getElementById('site-nav');
  var closeT = null;
  function openMega() {
    if (!mega) return;
    clearTimeout(closeT);
    mega.hidden = false;
    requestAnimationFrame(function () { mega.classList.add('open'); });
    ddBtn.setAttribute('aria-expanded', 'true');
    head.classList.add('mega-open');
  }
  function closeMega(now) {
    if (!mega || mega.hidden) return;
    clearTimeout(closeT);
    var go = function () {
      mega.classList.remove('open');
      ddBtn.setAttribute('aria-expanded', 'false');
      head.classList.remove('mega-open');
      setTimeout(function () { if (!mega.classList.contains('open')) mega.hidden = true; }, 220);
    };
    if (now) go(); else closeT = setTimeout(go, 160);
  }
  if (ddBtn && mega) {
    ddBtn.addEventListener('click', function () {
      if (ddBtn.getAttribute('aria-expanded') === 'true') closeMega(true); else openMega();
    });
    if (finePointer) {
      ddBtn.addEventListener('mouseenter', openMega);
      head.addEventListener('mouseleave', function () { closeMega(false); });
      mega.addEventListener('mouseenter', function () { clearTimeout(closeT); });
      document.querySelectorAll('.menu > a, .head-cta, .brand').forEach(function (el) {
        el.addEventListener('mouseenter', function () { closeMega(false); });
      });
    }
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeMega(true); ddBtn.focus(); } });
    document.addEventListener('click', function (e) { if (!head.contains(e.target)) closeMega(true); });
    mega.addEventListener('click', function (e) { if (e.target.closest('a')) closeMega(true); });
  }

  /* ?menu=1 opens the mega menu at load so a capture can show it */
  if (/[?&]menu=1\b/.test(location.search) && mega) { mega.hidden = false; mega.classList.add('open'); ddBtn.setAttribute('aria-expanded', 'true'); head.classList.add('mega-open'); }

  /* ---------- phone sheet ---------- */
  var burger = document.querySelector('.burger');
  var sheet = document.getElementById('sheet');
  function setSheet(open) {
    if (!sheet) return;
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    if (open) { sheet.hidden = false; requestAnimationFrame(function () { sheet.classList.add('open'); }); html.classList.add('sheet-open'); lenis('stop'); }
    else { sheet.classList.remove('open'); html.classList.remove('sheet-open'); lenis('start'); setTimeout(function () { if (!sheet.classList.contains('open')) sheet.hidden = true; }, 300); }
  }
  if (burger && sheet) {
    burger.addEventListener('click', function () { setSheet(burger.getAttribute('aria-expanded') !== 'true'); });
    sheet.addEventListener('click', function (e) { if (e.target.closest('a')) setSheet(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setSheet(false); });
  }

  /* ---------- catalogue tabs ---------- */
  var tabs = document.querySelectorAll('.tabs .tab');
  var cards = document.querySelectorAll('.c3d');
  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      var f = t.getAttribute('data-filter');
      tabs.forEach(function (x) { x.setAttribute('aria-selected', x === t ? 'true' : 'false'); });
      var i = 0;
      cards.forEach(function (c) {
        var show = f === 'all' || c.getAttribute('data-group') === f;
        if (show) {
          c.hidden = false;
          c.classList.add('is-in');
          c.style.setProperty('--d', (i++ * 45) + 'ms');
          c.classList.remove('c3d-enter'); void c.offsetWidth; c.classList.add('c3d-enter');
        } else {
          c.hidden = true;
        }
      });
    });
  });

  /* ?tilt=<n> pins card n mid-tilt so a capture can show the 3D state */
  var pin = /[?&]tilt=(\d+)/.exec(location.search);
  if (pin && cards[+pin[1]]) {
    var pc = cards[+pin[1]], pi = pc.querySelector('.c3d-in');
    pc.classList.add('tilting');
    pi.style.setProperty('--ry', '11deg'); pi.style.setProperty('--rx', '-7deg');
    pi.style.setProperty('--gx', '80%'); pi.style.setProperty('--gy', '15%');
  }

  /* ?door=<n> / ?ind=<n> pin a door or an industry tile open so a capture
     can show the widened state (the pane and headless cannot hover) */
  [['door', '.door'], ['ind', '.ind-tile']].forEach(function (k) {
    var m = new RegExp('[?&]' + k[0] + '=(\\d+)').exec(location.search);
    var el = m && document.querySelectorAll(k[1])[+m[1]];
    if (el) el.classList.add('is-open');
  });

  /* ---------- 3D tilt + glare ---------- */
  if (finePointer && !reduce) {
    cards.forEach(function (c) {
      var inner = c.querySelector('.c3d-in');
      var raf = 0, px = 0, py = 0;
      function paint() {
        raf = 0;
        inner.style.setProperty('--ry', (px * 14).toFixed(2) + 'deg');
        inner.style.setProperty('--rx', (-py * 12).toFixed(2) + 'deg');
        inner.style.setProperty('--gx', ((px + 0.5) * 100).toFixed(1) + '%');
        inner.style.setProperty('--gy', ((py + 0.5) * 100).toFixed(1) + '%');
      }
      c.addEventListener('pointermove', function (e) {
        var r = c.getBoundingClientRect();
        px = (e.clientX - r.left) / r.width - 0.5;
        py = (e.clientY - r.top) / r.height - 0.5;
        if (!raf) raf = requestAnimationFrame(paint);
      });
      c.addEventListener('pointerenter', function () { c.classList.add('tilting'); });
      c.addEventListener('pointerleave', function () {
        c.classList.remove('tilting');
        inner.style.setProperty('--ry', '0deg'); inner.style.setProperty('--rx', '0deg');
      });
    });
  }
})();
