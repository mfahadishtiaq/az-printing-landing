/* AZ Printing & Signs — landing page behaviour.

   1. THE PRODUCT EXPLORER (2026-09-13). The markup ships every category panel
      visible, with the index as plain jump links, so a failed or blocked script
      still shows the whole catalogue (rule 31). This script upgrades it into
      tabs: one panel at a time, the ARIA tab pattern, arrow keys, and the URL
      hash kept in step so #business-cards opens that category, from the footer
      or from a link someone was sent.

   2. THE FORM HAS NO BACKEND YET and must not pretend to. Submitting composes a
      WhatsApp message from the fields and hands it to the customer to send.
      When the domain serves, wire a real endpoint and delete this part. */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var ex = document.querySelector('[data-explorer]');
  if (ex) {
    var index = ex.querySelector('.ex-index');
    var tabs = Array.prototype.slice.call(index.querySelectorAll('.ex-tab'));
    var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('href').slice(1)); });
    var desktop = window.matchMedia('(min-width: 1024px)');

    ex.classList.add('ex-ready'); // from here the hidden attribute owns visibility (see landing.css)
    index.setAttribute('role', 'tablist');
    index.setAttribute('aria-label', 'Product categories');
    var setOrientation = function () { index.setAttribute('aria-orientation', desktop.matches ? 'vertical' : 'horizontal'); };
    setOrientation();
    if (desktop.addEventListener) desktop.addEventListener('change', setOrientation);

    // Bring the top of the panels into view when a switch happens below it, so a
    // customer deep in a long panel is not left looking at the middle of the next.
    var scrollToPanels = function () {
      var head = document.querySelector('.head');
      var offset = (head ? head.offsetHeight : 0) + (desktop.matches ? 24 : index.offsetHeight + 8);
      var top = ex.querySelector('.ex-panels').getBoundingClientRect().top;
      if (top < offset || top > window.innerHeight * 0.6) {
        window.scrollTo({ top: window.pageYOffset + top - offset, behavior: reduce ? 'auto' : 'smooth' });
      }
    };

    var current = -1;
    var activate = function (i, opts) {
      opts = opts || {};
      tabs.forEach(function (t, j) {
        var on = j === i;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        panels[j].hidden = !on;
      });
      var p = panels[i];
      if (current !== -1 && current !== i) {
        p.classList.remove('is-in');
        void p.offsetWidth; // restart the entrance animation
        p.classList.add('is-in');
      }
      current = i;
      // keep the chosen chip in view inside the phone's swipe row (horizontal only)
      if (index.scrollWidth > index.clientWidth + 1) {
        var t = tabs[i];
        var left = t.offsetLeft - (index.clientWidth - t.offsetWidth) / 2;
        if (index.scrollTo) index.scrollTo({ left: left, behavior: reduce ? 'auto' : 'smooth' });
        else index.scrollLeft = left;
      }
      if (opts.focus) tabs[i].focus();
      if (opts.hash && window.history && history.replaceState) history.replaceState(null, '', '#' + p.id);
      if (opts.scroll) scrollToPanels();
    };

    tabs.forEach(function (t, i) {
      var p = panels[i];
      t.id = 'tab-' + p.id;
      t.setAttribute('role', 'tab');
      t.setAttribute('aria-controls', p.id);
      p.setAttribute('role', 'tabpanel');
      p.setAttribute('aria-labelledby', t.id);
      // NO tabindex on the panel. Every panel already holds focusable buttons,
      // so the ARIA pattern does not need it, and with it a link such as
      // /#signs focused the panel on arrival and drew a red focus ring round it.
      t.addEventListener('click', function (e) {
        e.preventDefault();
        activate(i, { hash: true, scroll: true });
      });
      t.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') n = (i + 1) % tabs.length;
        else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') n = (i - 1 + tabs.length) % tabs.length;
        else if (e.key === 'Home') n = 0;
        else if (e.key === 'End') n = tabs.length - 1;
        if (n !== null) { e.preventDefault(); activate(n, { focus: true, hash: true }); }
      });
    });

    var fromHash = function () {
      var id = decodeURIComponent(location.hash.slice(1));
      for (var j = 0; j < panels.length; j++) if (panels[j].id === id) return j;
      return -1;
    };

    var start = fromHash();
    activate(start === -1 ? 0 : start);
    // The browser jumped to the anchor while every panel was still showing, and
    // hiding the others moved it; settle on the panel top after layout.
    if (start !== -1) window.addEventListener('load', scrollToPanels);

    window.addEventListener('hashchange', function () {
      var j = fromHash();
      if (j !== -1) { activate(j); scrollToPanels(); }
    });
  }

  var f = document.getElementById('lp-form');
  if (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = function (id) { var el = document.getElementById(id); return el ? el.value.trim() : ''; };
      var lines = ['Hello, I would like a quote.'];
      if (v('lp-name')) lines.push('Name: ' + v('lp-name'));
      if (v('lp-phone')) lines.push('Phone: ' + v('lp-phone'));
      if (v('lp-job')) lines.push('Job: ' + v('lp-job'));
      window.open(f.dataset.fallback + '?text=' + encodeURIComponent(lines.join('\n')), '_blank', 'noopener');
    });
  }
})();
