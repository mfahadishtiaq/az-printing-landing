/* AZ Printing & Signs — Build 1 behaviour (2026-08-27).
   Rules honoured: content never depends on JS for visibility (rule 31 —
   .reveal states exist only under .js and a timed failsafe reveals all);
   reduced motion collapses everything in CSS. */
(function () {
  var nav = document.querySelector('.main-nav');
  var toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    });
  }

  /* Family menus. Hover is CSS; this handles tap, and now also click and the
     keyboard, because the trigger is a BUTTON that navigates nowhere
     (Fahad 2026-09-09). The old handler had to preventDefault on the first tap
     and let a second tap follow the link; with nothing to follow, a tap is
     simply a toggle, and Enter/Space get the same behaviour for free.
     1023 tracks the CSS nav breakpoints — if they move, move this with them, or
     a mouse user in the gap gets burger CSS with desktop logic. */
  document.querySelectorAll('.has-dropdown > button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var li = btn.parentElement;
      var open = li.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) {
        /* Only one family open at a time, or the burger becomes a wall of
           every menu at once. */
        document.querySelectorAll('.has-dropdown.open').forEach(function (o) {
          if (o !== li) {
            o.classList.remove('open');
            var b = o.querySelector('button');
            if (b) b.setAttribute('aria-expanded', 'false');
          }
        });
      }
    });
  });
  /* Escape closes an open family and returns focus to its own trigger. With a
     button trigger this is the only way back out by keyboard. */
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = document.querySelector('.has-dropdown.open');
    if (!open) return;
    open.classList.remove('open');
    var b = open.querySelector('button');
    if (b) { b.setAttribute('aria-expanded', 'false'); b.focus(); }
  });

  // Reveal on scroll: margin 0 (reveal on first pixel — desktop-tuned margins
  // hide phone content), plus a timed failsafe so an un-fired observer can
  // never leave a blank page.
  var sections = document.querySelectorAll('main > section');
  sections.forEach(function (s) { s.classList.add('reveal'); });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('revealed'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px', threshold: 0 });
    sections.forEach(function (s) { io.observe(s); });
  }
  setTimeout(function () {
    sections.forEach(function (s) { s.classList.add('revealed'); });
  }, 1800);
})();


/* Site search (2026-08-27): reads /search-index.json (emitted by generate.py
   from the same tables that build the nav). Rule 104: this input exists
   because it actually finds things. */
(function () {
  var input = document.getElementById('site-search');
  var panel = document.getElementById('search-results');
  if (!input || !panel) return;
  var idx = null, loading = null;

  function load() {
    if (idx) return Promise.resolve(idx);
    if (!loading) {
      loading = fetch('/search-index.json')
        .then(function (r) { return r.json(); })
        .then(function (d) { idx = d; return d; });
    }
    return loading;
  }

  function hide() { panel.hidden = true; panel.innerHTML = ''; }

  function render(q) {
    var query = q.toLowerCase();
    var scored = [];
    idx.forEach(function (row) {
      var t = row.t.toLowerCase();
      var score = t.indexOf(query) === 0 ? 0 : t.indexOf(query) > -1 ? 1 : row.k.indexOf(query) > -1 ? 2 : -1;
      if (score >= 0) scored.push([score, row]);
    });
    scored.sort(function (a, b) { return a[0] - b[0]; });
    var top = scored.slice(0, 8);
    if (!top.length) {
      panel.innerHTML = '<p class="no-hit">Nothing matched. Call 905-796-1515 and ask; the list is what is common, not what is possible.</p>';
    } else {
      panel.innerHTML = top.map(function (s) {
        return '<a href="' + s[1].u + '">' + s[1].t + '</a>';
      }).join('');
    }
    panel.hidden = false;
  }

  // Clear button (2026-08-28, ported behaviour from the supplied HeroUI
  // SearchField). Lives inside THIS module on purpose: it shares hide() and
  // the input reference, and a separate IIFE would duplicate both.
  var clearBtn = document.querySelector('.search-clear');
  function syncClear() { if (clearBtn) clearBtn.hidden = !input.value; }
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      input.value = '';
      syncClear();
      hide();
      input.focus();
    });
  }
  input.addEventListener('input', syncClear);
  syncClear();

  input.addEventListener('focus', load);
  input.addEventListener('input', function () {
    var q = input.value.trim();
    if (q.length < 2) { hide(); return; }
    load().then(function () { render(q); });
  });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { hide(); input.blur(); }
    if (e.key === 'Enter') {
      var first = panel.querySelector('a');
      if (first) location.href = first.getAttribute('href');
    }
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.search')) hide();
  });
})();

/* Quote list (NAV v3, Fahad 2026-08-28): the honest cart on a quote-first
   site. localStorage only; the tier-1 badge counts items; /quote/ renders
   the list and folds it into the form's hidden field.

   EXTENDED 2026-09-08 for the product configurator (Fahad: click a product,
   choose what you want, add it to the cart like Etsy). An item may now carry
   OPTIONS the customer typed — quantity, size, finish, notes.

   ***THAT BROKE THE OLD SAFETY ARGUMENT AND THE RENDER HAD TO CHANGE.*** The
   previous version built the list with innerHTML and string concatenation,
   which was safe ONLY because every value was site-authored by the generator.
   Customer text through innerHTML is an injection hole, so the render below is
   DOM construction with textContent throughout. Do not "tidy" it back into a
   template string: the values are no longer ours. */
(function () {
  var KEY = 'az-quote';
  function read() {
    try {
      var l = JSON.parse(localStorage.getItem(KEY)) || [];
      // items stored before options existed have no .o
      return l.map(function (i) { return { t: i.t, u: i.u, o: i.o || [] }; });
    } catch (e) { return []; }
  }
  function badge(list) {
    var b = document.querySelector('.q-badge');
    if (!b) return;
    b.textContent = String(list.length);
    b.hidden = list.length === 0;
  }
  function write(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {}
    badge(list);
  }
  /* The added-state label is per button: the window says "In your cart" while
     the .type-block pages on the other five categories still say "On your
     list". One shared handler, two labels, no second code path. */
  function mark(btn) { btn.textContent = btn.dataset.addedLabel || 'On your list'; btn.disabled = true; }
  function summary(item) {
    return item.o.map(function (o) { return o.k + ': ' + o.v; }).join('; ');
  }
  /* FAVOURITES (Fahad 2026-09-09: a heart at the end of the window, beside the
     add-to-cart button). Kept in their OWN store rather than as a flag on quote
     items, because the two lists mean different things: the cart is what you
     are asking us to price, the heart is what you are thinking about. A saved
     thing must not travel into a quote request the customer did not make. */
  var FAV = 'az-favs';
  function readFavs() {
    try {
      var l = JSON.parse(localStorage.getItem(FAV) || '[]');
      if (!Array.isArray(l)) return [];
      return l.map(function (i) { return { t: i.t, u: i.u }; });
    } catch (e) { return []; }
  }
  function writeFavs(l) { try { localStorage.setItem(FAV, JSON.stringify(l)); } catch (e) {} }
  function isFav(t) { return readFavs().some(function (i) { return i.t === t; }); }
  function toggleFav(t, u) {
    var l = readFavs();
    var at = l.findIndex(function (i) { return i.t === t; });
    if (at > -1) l.splice(at, 1); else l.push({ t: t, u: u });
    writeFavs(l);
    return at === -1;
  }

  var list = read();
  badge(list);
  document.querySelectorAll('.add-quote').forEach(function (btn) {
    if (list.some(function (i) { return i.t === btn.dataset.item; })) mark(btn);
  });

  /* CONFIGURATOR WINDOW (2026-09-09). One <dialog> per page, filled on open
     from the card that was clicked, so the copy lives once (in generate.py's
     types list) and card, window and quote list cannot drift apart.
     showModal() is what gives us the focus trap, ESC-to-close, the inert
     background and the backdrop. Everything below is only the filling. */
  var modal = document.getElementById('prod-modal');
  if (modal && typeof modal.showModal === 'function') {
    var mFace = modal.querySelector('.pm-face');
    var mName = modal.querySelector('.pm-name');
    var mDesc = modal.querySelector('.pm-desc');
    var mSize = modal.querySelector('.pm-size');
    var mQty = modal.querySelector('.pm-qty');
    var mAdd = modal.querySelector('.pm-add');
    var mFav = modal.querySelector('.pm-fav');
    /* Captured from the markup ONCE, not hardcoded here. The reset on every
       open used to restate the label as a literal, so renaming the button in
       generate.py changed it for exactly one paint and then the reset put the
       old word back on the first product opened. */
    var ADD_LABEL = mAdd.textContent;
    var opener = null;

    function paintFav(name) {
      if (!mFav) return;
      var on = isFav(name);
      mFav.setAttribute('aria-pressed', String(on));
      mFav.setAttribute('aria-label', on ? 'Remove from favourites' : 'Save to favourites');
    }
    if (mFav) mFav.addEventListener('click', function () {
      toggleFav(mAdd.dataset.item, mAdd.dataset.url);
      paintFav(mAdd.dataset.item);
    });

    /* Options are built as elements with textContent, never as markup. These
       strings are site-authored, but the same window also carries text the
       CUSTOMER types, and having one safe habit in here beats two rules. */
    function fill(sel, values, unit, axis) {
      sel.textContent = '';
      var ph = document.createElement('option');
      ph.value = '';
      ph.textContent = unit ? 'Choose a quantity' : 'Choose a ' + (axis || 'size').toLowerCase();
      sel.appendChild(ph);
      values.forEach(function (v) {
        if (!v) return;
        var o = document.createElement('option');
        o.value = v;                       // the value IS the answer
        o.textContent = v;
        sel.appendChild(o);
      });
      /* THE OTHER OPTION CARRIES value="" ON PURPOSE. The quote collector skips
         empty values, so "Other" can never be recorded as if it were an answer,
         and the free-text field it reveals carries the SAME data-cfg key — so
         exactly one Size (or Quantity) ever reaches the list, whichever way the
         customer answered. It is told apart from the placeholder by data-other. */
      var other = document.createElement('option');
      other.value = '';
      other.dataset.other = '1';
      other.textContent = unit ? 'Another quantity (tell us)'
        : 'Other ' + (axis || 'size').toLowerCase() + ' (tell us)';
      sel.appendChild(other);
    }

    /* THE FIRST FIELD'S AXIS IS PER PRODUCT. Most products ask for a Size, but a
       mug asks for a Capacity and a shirt run asks for the spread of garment
       sizes, so the label, the placeholder text and the KEY the answer is filed
       under all come from the card. A product with no standard list at all
       (pens, keychains, awards) declares itself free text and gets an input
       instead of a menu — inventing a menu of promo items AZ has never said it
       stocks is the one thing this whole register exists to stop. */
    var sizeLabel = mSize.closest('.cfg-f');
    var sizeOther = modal.querySelector('.pm-other[data-for="size"]');
    function setAxis(axis, freetext, hint) {
      axis = axis || 'Size';
      sizeLabel.querySelector('span').textContent = axis;
      mSize.dataset.cfg = axis;
      var inp = sizeOther.querySelector('input');
      inp.dataset.cfg = axis;
      if (freetext) {
        sizeLabel.hidden = true;                 // no menu to show
        sizeOther.querySelector('span').textContent = axis;
        inp.placeholder = hint || 'Tell us what you need';
        sizeOther.hidden = false;
      } else {
        sizeLabel.hidden = false;
        sizeOther.querySelector('span').textContent = 'Your ' + axis.toLowerCase();
        inp.placeholder = 'Tell us what you need';
        sizeOther.hidden = true;
      }
    }
    function otherField(which) {
      return modal.querySelector('.pm-other[data-for="' + which + '"]');
    }
    function syncOther(sel, which) {
      var opt = sel.options[sel.selectedIndex];
      var box = otherField(which);
      if (!box) return;
      var on = !!(opt && opt.dataset.other);
      box.hidden = !on;
      if (!on) box.querySelector('input').value = '';
      else box.querySelector('input').focus();
    }
    mSize.addEventListener('change', function () { syncOther(mSize, 'size'); });
    mQty.addEventListener('change', function () { syncOther(mQty, 'qty'); });

    document.addEventListener('click', function (e) {
      /* The picture is a second way in (Fahad 2026-09-09). It is not its own
         button: the data lives on the card's toggle either way, so a click on
         the face is resolved to that same toggle rather than duplicated. */
      var t = e.target.closest('.prod-toggle');
      if (!t) {
        var face = e.target.closest('.prod-face');
        if (face) t = face.closest('.prod').querySelector('.prod-toggle');
      }
      if (!t) return;
      opener = t;
      mName.textContent = t.dataset.name || '';
      mDesc.textContent = t.dataset.desc || '';
      mFace.textContent = '';
      if (t.dataset.img) {
        var im = document.createElement('img');
        im.src = t.dataset.img;
        im.alt = (t.dataset.name || '') + ', sample image';
        mFace.appendChild(im);
      } else {
        /* No photo yet: the same house panel the card draws, not a grey hole. */
        var panel = document.createElement('span');
        panel.className = 'prod-panel ' + (t.dataset.panel || 'pp-a');
        mFace.appendChild(panel);
      }
      var freetext = t.dataset.freetext === '1';
      fill(mSize, (t.dataset.sizes || '').split('|'), false, t.dataset.axis);
      fill(mQty, (t.dataset.qty || '').split('|'), true);
      modal.querySelectorAll('.pm-other').forEach(function (b) {
        b.hidden = true; b.querySelector('input').value = '';
      });
      setAxis(t.dataset.axis, freetext, t.dataset.hint);
      modal.querySelectorAll('[data-cfg]').forEach(function (f) {
        if (f.tagName !== 'SELECT') f.value = '';
      });
      /* THE ADD BUTTON IS SHARED BY EVERY PRODUCT, so its state must be rebuilt
         on each open. Without this, adding one product left it disabled and
         reading "On your list" for all the others. */
      mAdd.dataset.item = t.dataset.name || '';
      mAdd.dataset.url = t.dataset.url || '';
      mAdd.disabled = false;
      mAdd.textContent = ADD_LABEL;
      if (read().some(function (i) { return i.t === mAdd.dataset.item; })) mark(mAdd);
      paintFav(mAdd.dataset.item);
      modal.showModal();
      /* autofocus sits on the size select, which a free-text product HIDES, so
         the dialog fell back to its first focusable and opened with the close
         button ringed. Put focus on whichever first field is actually shown. */
      var first = freetext ? sizeOther.querySelector('input') : mSize;
      if (first) try { first.focus(); } catch (e) {}
    });

    modal.addEventListener('click', function (e) {
      /* Backdrop click closes. A click on the backdrop targets the dialog
         itself, because the backdrop is not an element you can hit. */
      if (e.target === modal || e.target.closest('[data-pm-close]')) modal.close();
    });
    /* Focus goes back to the card that opened the window. showModal() does not
       do this for a dialog closed programmatically. */
    modal.addEventListener('close', function () {
      if (opener && document.contains(opener)) opener.focus();
      opener = null;
    });
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.add-quote');
    if (!btn || btn.disabled) return;
    var opts = [];
    var cfgId = btn.dataset.cfgFor;
    if (cfgId) {
      var cfg = document.getElementById(cfgId);
      if (cfg) {
        cfg.querySelectorAll('[data-cfg]').forEach(function (f) {
          var v = (f.value || '').trim().slice(0, 120);   // capped, stored as text
          if (v) opts.push({ k: f.dataset.cfg, v: v });
        });
      }
    }
    var l = read();
    if (!l.some(function (i) { return i.t === btn.dataset.item; })) {
      l.push({ t: btn.dataset.item, u: btn.dataset.url, o: opts });
      write(l);
    }
    mark(btn);
    /* Added from the window: show the button change, then hand the page back.
       Closing instantly reads as nothing having happened; leaving it open makes
       the customer hunt for the close button after every product. */
    var dlg = btn.closest('dialog');
    if (dlg && dlg.open) setTimeout(function () { dlg.close(); }, 550);
  });

  // /quote/ page: render the list, wire removes, fill the hidden field
  var wrap = document.getElementById('quote-items');
  if (wrap) {
    var field = document.getElementById('quote-items-field');
    var render = function () {
      var l = read();
      if (field) {
        field.value = l.map(function (i) {
          var s = summary(i);
          return i.t + (s ? ' (' + s + ')' : '');
        }).join(' | ');
      }
      wrap.textContent = '';
      if (!l.length) {
        var p = document.createElement('p');
        p.className = 'quote-empty';
        p.textContent = 'Your list is empty so far. Open any family in the red bar and tap Add to cart on the things you need.';
        wrap.appendChild(p);
        return;
      }
      l.forEach(function (i, n) {
        var row = document.createElement('div');
        row.className = 'quote-row';
        var a = document.createElement('a');
        a.href = i.u;                      // site-authored, still ours
        a.textContent = i.t;               // site-authored
        row.appendChild(a);
        var s = summary(i);
        if (s) {
          var spec = document.createElement('span');
          spec.className = 'quote-spec';
          spec.textContent = s;            // CUSTOMER TEXT — textContent, never innerHTML
          row.appendChild(spec);
        }
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'q-remove';
        b.dataset.n = String(n);
        b.setAttribute('aria-label', 'Remove ' + i.t + ' from the list');
        b.textContent = 'Remove';
        row.appendChild(b);
        wrap.appendChild(row);
      });
    };
    /* SAVED FOR LATER. Same DOM-construction discipline as the cart above: these
       rows carry product names the generator wrote, but the two renderers sit
       side by side and one safe habit beats two rules. Saved items carry NO
       options, because the heart is tapped before the customer has chosen any;
       moving one across puts the bare product on the list, which is the same
       thing the .type-block pages already do. */
    var savedWrap = document.getElementById('saved-items');
    var savedSec = document.getElementById('saved-sec');
    var renderSaved = function () {
      if (!savedWrap) return;
      var f = readFavs();
      if (savedSec) savedSec.hidden = f.length === 0;
      savedWrap.textContent = '';
      f.forEach(function (i, n) {
        var row = document.createElement('div');
        row.className = 'quote-row';
        var a = document.createElement('a');
        a.href = i.u;
        a.textContent = i.t;
        row.appendChild(a);
        var add = document.createElement('button');
        add.type = 'button';
        add.className = 'q-move';
        add.dataset.n = String(n);
        add.setAttribute('aria-label', 'Add ' + i.t + ' to your cart');
        add.textContent = 'Add to cart';
        row.appendChild(add);
        var rm = document.createElement('button');
        rm.type = 'button';
        rm.className = 'q-unfav';
        rm.dataset.n = String(n);
        rm.setAttribute('aria-label', 'Remove ' + i.t + ' from favourites');
        rm.textContent = 'Remove';
        row.appendChild(rm);
        savedWrap.appendChild(row);
      });
    };
    if (savedWrap) {
      savedWrap.addEventListener('click', function (e) {
        var mv = e.target.closest('.q-move');
        var un = e.target.closest('.q-unfav');
        if (!mv && !un) return;
        var f = readFavs();
        var i = f[Number((mv || un).dataset.n)];
        if (!i) return;
        if (mv) {
          var l = read();
          if (!l.some(function (x) { return x.t === i.t; })) { l.push({ t: i.t, u: i.u, o: [] }); write(l); }
        }
        f.splice(Number((mv || un).dataset.n), 1);
        writeFavs(f);
        renderSaved();
        render();
      });
      renderSaved();
    }

    wrap.addEventListener('click', function (e) {
      var b = e.target.closest('.q-remove');
      if (!b) return;
      var l = read();
      l.splice(Number(b.dataset.n), 1);
      write(l);
      render();
    });
    render();
  }
})();

/* Same-day rush row: the arrow buttons page the scroller by one card.
   Touch and trackpad scroll the row natively; buttons only exist under .js
   (CSS-gated) so nothing depends on this. Plain scrollLeft assignment on
   purpose: its behavior resolves from the scroller's CSS scroll-behavior
   (smooth for users, auto under reduced motion, injectable to auto for QA).
   scrollBy({behavior:'smooth'}) was a silent no-op on this snap container
   in headless Chrome; keep the assignment. */
(function () {
  // PLURAL ON PURPOSE (2026-08-28). Home now carries TWO carousels, featured
  // products and same-day. The previous querySelector was singular and correct
  // when there was one; with two, every .rush-btn on the page would have been
  // wired to whichever scroller was found first, and since featured sits above
  // same-day in the DOM that would have silently killed the same-day arrows.
  var scrollers = document.querySelectorAll('.rush-scroller');
  if (!scrollers.length) return;
  scrollers.forEach(function (sc) {
    // buttons belong to the same SECTION as their scroller, not to the document
    var scope = sc.closest('section') || document;
    scope.querySelectorAll('.rush-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        // same-day holds .rush-card, featured holds .feat: measure whatever
        // card this scroller actually contains rather than assuming a class
        var card = sc.firstElementChild;
        var step = (card ? card.getBoundingClientRect().width : 280) + 16;
        sc.scrollLeft += step * Number(b.dataset.dir);
      });
    });
  });
})();

/* MEGA-PANEL PLACEMENT (2026-08-28, Fahad: "Apparel and Promo is opening
   towards the left, same with Copy, Photo").
   The CSS clamp `li:nth-child(n+5) .dropdown{right:0}` right-anchors the last
   families so they cannot run off the viewport. It works, but it makes panels
   1-4 open rightward from their label and 5-7 open leftward, which reads as
   inconsistent rather than considered. That rule is now the NO-JS FALLBACK
   only (rule 31: without JS those panels must still be reachable).
   With JS, every panel is aligned under its own label and then shifted left
   by its ACTUAL overflow, never by its index. Two consequences worth knowing:
   nobody has to reason about nth-child positions when a nav item is added or
   reordered, which has bitten this build twice; and panel width is no longer
   coupled to that clamp.
   Measured on open rather than up front, because a display:none panel measures
   zero. CSS :hover applies before the mouseenter listener runs, so the box is
   already laid out by the time this reads it. */
(function () {
  var GUTTER = 16;
  var desktop = function () { return window.matchMedia('(min-width: 1024px)').matches; };

  function place(li) {
    var d = li.querySelector('.dropdown');
    if (!d) return;
    if (!desktop()) { d.style.left = ''; return; }   // burger: panel is in flow
    d.style.left = '0px';
    var r = d.getBoundingClientRect();
    if (!r.width) return;                            // not laid out yet, leave CSS alone
    var vw = document.documentElement.clientWidth;
    var shift = 0;
    var over = r.right - (vw - GUTTER);
    if (over > 0) shift = -over;
    // and never push it off the LEFT while fixing the right, which is the
    // failure mode the index-based clamp had on the middle families.
    if (r.left + shift < GUTTER) shift = GUTTER - r.left;
    d.style.left = Math.round(shift) + 'px';
  }

  var items = document.querySelectorAll('.main-nav li.has-dropdown');
  items.forEach(function (li) {
    li.addEventListener('mouseenter', function () { place(li); });
    li.addEventListener('focusin', function () { place(li); });
  });

  // Widths change what fits, so any stale inline offset must go.
  var t;
  window.addEventListener('resize', function () {
    clearTimeout(t);
    t = setTimeout(function () {
      items.forEach(function (li) { li.querySelector('.dropdown').style.left = ''; });
    }, 150);
  });
})();

/* F11 FORM HARNESS (2026-08-28, ported from ZEF at Fahad's instruction: "Make
   the last contact us form like the contact us form on ZEF"). This closes a
   NAMED SKIP that has stood in the handoff since this build started.

   What it replaces: a plain POST that navigated the visitor away to
   FormSubmit's own page, with no per-field errors and NO FAILURE PATH. If the
   POST failed, the visitor landed on an error page and everything they typed
   was gone.

   Three states, and the middle one is why the port was worth doing:
     pending  the button is disabled and says so, so a slow network cannot be
              double-submitted into two leads
     sent     the confirmation appears ONLY after FormSubmit acknowledges
     failed   the typed details STAY on screen, the notice says the send did
              not go through, and it hands back the counter's phone number

   A form that answers "thank you" to a dropped POST tells a lie in a quiet
   voice. The confirmation here is a consequence of a resolved promise, never
   of a click. */
(function () {
  document.querySelectorAll('form[data-validate]').forEach(function (form) {
    var fields = form.querySelectorAll('.field input[required], .field textarea[required]');

    /* novalidate is set HERE, not in the markup. With JS these custom errors are
       the designed path and the browser's own bubbles would fire first and fight
       them. Without JS the browser's checking is the ONLY checking there is, and
       putting novalidate in the markup would take it away from the one visitor
       who has nothing else. */
    form.noValidate = true;

    function validate(input) {
      var field = input.closest('.field');
      var ok = input.checkValidity() && input.value.trim() !== '';
      field.classList.toggle('invalid', !ok);
      input.setAttribute('aria-invalid', ok ? 'false' : 'true');
      return ok;
    }

    fields.forEach(function (input) {
      // Blur, never keystroke: nobody should be told their half-typed name is
      // wrong. Once a field IS marked invalid, clear it as soon as it becomes
      // valid rather than making them tab away again to see it resolve.
      input.addEventListener('blur', function () { validate(input); });
      input.addEventListener('input', function () {
        if (input.closest('.field').classList.contains('invalid')) validate(input);
      });
    });

    var btn = form.querySelector('.send');
    var notice = form.querySelector('.formerr');
    var wrap = form.closest('.quote-wrap');
    var busy = false;

    /* The email is only as readable as its field names, and the owner is the one
       reading it. The VISIBLE LABEL is the field's name in the email, so the two
       cannot drift. data-label covers the hidden quote-list field, which has no
       visible label but must still arrive named. */
    function labelFor(el) {
      if (el.getAttribute('data-label')) return el.getAttribute('data-label');
      var lab = el.id && form.querySelector('label[for="' + el.id + '"]');
      if (!lab) return el.name || 'Field';
      var copy = lab.cloneNode(true);
      var req = copy.querySelector('.req');
      if (req) req.parentNode.removeChild(req);
      return copy.textContent.replace(/\s+/g, ' ').trim();
    }

    function fail() {
      busy = false;
      if (btn) {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.textContent = btn.getAttribute('data-label') || 'Request my free quote';
      }
      if (!notice) return;
      notice.textContent = form.getAttribute('data-failtext') || '';
      notice.setAttribute('tabindex', '-1');
      notice.focus();
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (busy) return;

      var firstBad = null;
      fields.forEach(function (input) { if (!validate(input) && !firstBad) firstBad = input; });
      if (firstBad) { firstBad.focus(); return; }

      var endpoint = form.getAttribute('data-endpoint');
      // No endpoint means the build shipped broken. Say so rather than showing a
      // confirmation, which is the exact failure this register was opened for.
      if (!endpoint || typeof fetch !== 'function') { fail(); return; }

      var payload = {};
      form.querySelectorAll('input, select, textarea').forEach(function (el) {
        if (!el.name || el.name.charAt(0) === '_') return;   // FormSubmit's own
        var val = (el.value || '').trim();
        if (val) payload[labelFor(el)] = val;
      });
      // Three pages share this form, so the lead has to say which one it came
      // from or the counter cannot tell a quote-list request from a home enquiry.
      payload['Sent from'] = document.title;
      payload._subject = form.getAttribute('data-subject') || document.title;
      payload._template = 'box';
      payload._captcha = 'false';
      payload._honey = (form.querySelector('[name="_honey"]') || {}).value || '';

      busy = true;
      if (notice) notice.textContent = '';
      if (btn) {
        btn.setAttribute('data-label', btn.textContent);
        btn.disabled = true;
        btn.setAttribute('aria-busy', 'true');
        btn.textContent = 'Sending';
      }

      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (data) {
          /* FormSubmit answers a FRESH DOMAIN with an activation challenge
             rather than a delivery, and that is the FIRST thing that will happen
             at launch, not an edge case. It arrives as a 200 with success false,
             so treating any 200 as sent would report a delivered lead that is
             actually sitting behind an unconfirmed activation email. */
          var ok = data && (data.success === true || data.success === 'true');
          if (!ok) { fail(); return; }
          busy = false;
          if (wrap) wrap.classList.add('done');
          var sent = wrap && wrap.querySelector('.sent');
          if (sent) { sent.hidden = false; sent.setAttribute('tabindex', '-1'); sent.focus(); }
        })
        .catch(fail);
    });
  });
})();
