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
  /* ---------- "What we do" layouts + the LOCALHOST-ONLY switch ----------
     Fahad picked two layouts (2026-10-06) and flips between them while he
     decides. The switch never renders on the real domain; there the first
     layout in build.py's CATALOG_LAYOUTS shows. ?layout=<name> works anywhere
     (captures). */
  var cat = document.querySelector('.catalog[data-layouts]');
  if (cat) {
    var views = [].slice.call(cat.querySelectorAll('.cat-view'));
    var names = views.map(function (v) { return v.getAttribute('data-view'); });
    var local = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
    var LABEL = { shelves: 'Shelves', bento: 'Bento', circles: 'Circles' };
    var sw = null;

    var fitShelves = function () {
      cat.querySelectorAll('.shelf').forEach(function (sh) {
        var row = sh.querySelector('.shelf-row'), ar = sh.querySelector('.shelf-arrows');
        if (!row || !ar) return;
        var max = row.scrollWidth - row.clientWidth;
        if (max > 4) ar.removeAttribute('data-fits'); else ar.setAttribute('data-fits', '');
        ar.querySelector('[data-dir="-1"]').disabled = row.scrollLeft < 4;
        ar.querySelector('[data-dir="1"]').disabled = row.scrollLeft > max - 4;
      });
    };
    var setView = function (n, remember) {
      if (names.indexOf(n) < 0) return;
      views.forEach(function (v) { v.hidden = v.getAttribute('data-view') !== n; });
      if (sw) sw.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-view') === n ? 'true' : 'false'); });
      if (remember) { try { localStorage.setItem('az-catalog-layout', n); } catch (e) {} }
      fitShelves();
      if (window.ScrollTrigger) window.ScrollTrigger.refresh();
    };

    cat.querySelectorAll('.shelf').forEach(function (sh) {
      var row = sh.querySelector('.shelf-row');
      sh.querySelectorAll('.shelf-arrows button').forEach(function (b) {
        b.addEventListener('click', function () {
          row.scrollBy({ left: +b.getAttribute('data-dir') * row.clientWidth * 0.8, behavior: 'smooth' });
        });
      });
      row.addEventListener('scroll', fitShelves, { passive: true });
    });
    window.addEventListener('resize', fitShelves);

    if (local && names.length > 1) {
      sw = document.createElement('div');
      sw.className = 'layout-switch';
      sw.setAttribute('role', 'group');
      sw.setAttribute('aria-label', 'What we do layout (only on localhost)');
      sw.innerHTML = '<span>What we do</span>' + names.map(function (n) {
        return '<button type="button" data-view="' + n + '">' + (LABEL[n] || n) + '</button>';
      }).join('');
      sw.addEventListener('click', function (e) {
        var b = e.target.closest('button');
        if (b) setView(b.getAttribute('data-view'), true);
      });
      document.body.appendChild(sw);
    }
    var q = /[?&]layout=([a-z]+)/.exec(location.search), saved = null;
    try { saved = localStorage.getItem('az-catalog-layout'); } catch (e) {}
    setView(q ? q[1] : (local && saved && names.indexOf(saved) > -1 ? saved : names[0]), false);
  }

  /* ?vf=<n> holds nav item n in its variable-font hover state for captures */
  var vfPin = /[?&]vf=(\d+)/.exec(location.search);
  var vfEl = vfPin && document.querySelectorAll('.menu > a, .menu > .menu-dd')[+vfPin[1]];
  if (vfEl) vfEl.classList.add('vf-on');

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
