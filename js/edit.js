/* Hero edit mode (2026-10-05): open the home page with ?edit=1.

   Click a product, the headline block or "Premium quality" to select it.
   Drag to move. Pull a corner handle to resize from the opposite corner,
   like Photoshop's free transform. Arrow keys nudge 1px (Shift: 10px),
   [ and ] scale by 2%, , and . send back / bring forward, Cmd/Ctrl-Z undoes,
   Esc deselects. "Download" saves hero-layout.json; put it beside build.py
   and run `python3 build.py` and the live page uses the layout.

   Everything is stored as percentages of the 1920x1083 stage, the same
   numbers build.py writes, so the file round-trips exactly. */
(function () {
  var html = document.documentElement;
  var stage = document.querySelector('.hero-stage');
  var hero = document.querySelector('.hero');
  if (!stage || !hero) return;
  if (window.innerWidth < 900) {
    alert('Edit mode works at desktop width (900px and up). Widen the window and reload.');
  }
  html.classList.add('editing');

  /* ---------- the editable things ---------- */
  var items = Array.prototype.slice.call(stage.querySelectorAll('.hero-item'));
  var textBlock = hero.querySelector('.hero-text');
  var quality = hero.querySelector('.hero-quality');
  var h1 = hero.querySelector('h1');
  var list = hero.querySelector('.hero-list');

  function num(v) { return parseFloat(v) || 0; }
  function stageRect() { return stage.getBoundingClientRect(); }

  // Each editable is {el, kind, get(), set(box), name}. Boxes are in stage %.
  function itemEd(el) {
    var img = el.querySelector('img');
    var aspect = num(img.getAttribute('height')) / num(img.getAttribute('width'));
    return {
      el: el, kind: 'item', name: el.getAttribute('data-name'), aspect: aspect,
      get: function () {
        var s = el.style;
        var w = num(s.getPropertyValue('--w'));
        return { x: num(s.getPropertyValue('--x')), y: num(s.getPropertyValue('--y')), w: w,
                 h: w * aspect * (stageRect().width / stageRect().height) };
      },
      set: function (b) {
        el.style.setProperty('--x', b.x.toFixed(3) + '%');
        el.style.setProperty('--y', b.y.toFixed(3) + '%');
        el.style.setProperty('--w', b.w.toFixed(3) + '%');
      }
    };
  }
  function cssPct(el, prop, fallback) {
    var v = el.style.getPropertyValue(prop);
    return v ? num(v) : fallback;
  }
  function textEd() {
    // left/top/width in % of the hero; font sizes in vw
    function fontVw(node) { return num(getComputedStyle(node).fontSize) / window.innerWidth * 100; }
    return {
      el: textBlock, kind: 'text', name: 'headline',
      get: function () {
        var r = textBlock.getBoundingClientRect(), s = stageRect();
        return { x: (r.left - s.left) / s.width * 100, y: (r.top - s.top) / s.height * 100,
                 w: r.width / s.width * 100, h: r.height / s.height * 100,
                 h1: fontVw(h1), list: fontVw(list) };
      },
      set: function (b, scale) {
        textBlock.style.setProperty('--tx', b.x.toFixed(3) + '%');
        textBlock.style.setProperty('--ty', b.y.toFixed(3) + '%');
        textBlock.style.setProperty('--tw', b.w.toFixed(3) + '%');
        if (scale) {
          textBlock.style.setProperty('--h1', (b.h1 * scale).toFixed(3) + 'vw');
          textBlock.style.setProperty('--lsz', (b.list * scale).toFixed(3) + 'vw');
        }
      }
    };
  }
  function qualityEd() {
    return {
      el: quality, kind: 'quality', name: 'premium-quality',
      get: function () {
        var r = quality.getBoundingClientRect(), s = stageRect();
        return { x: (r.left - s.left) / s.width * 100, y: (r.top - s.top) / s.height * 100,
                 w: r.width / s.width * 100, h: r.height / s.height * 100,
                 size: num(getComputedStyle(quality).fontSize) / window.innerWidth * 100 };
      },
      set: function (b, scale) {
        var s = stageRect();
        var right = 100 - (b.x + b.w), bottom = 100 - (b.y + b.h);
        quality.style.setProperty('--qr', right.toFixed(3) + '%');
        quality.style.setProperty('--qb', bottom.toFixed(3) + '%');
        if (scale) quality.style.setProperty('--qs', (b.size * scale).toFixed(3) + 'vw');
      }
    };
  }
  var editables = items.map(itemEd).concat([textEd(), qualityEd()]);
  editables.forEach(function (e) { e.el.classList.add('ed'); e.el.setAttribute('tabindex', '0'); });

  /* ---------- selection, handles, HUD ---------- */
  var selected = null;
  var box = document.createElement('div');
  box.className = 'ed-box';
  box.innerHTML = '<i data-h="nw"></i><i data-h="ne"></i><i data-h="sw"></i><i data-h="se"></i><b class="ed-name"></b>';
  hero.appendChild(box);

  var panel = document.createElement('div');
  panel.className = 'ed-panel';
  panel.innerHTML =
    '<div class="ed-bar">' +
    '<span class="ed-grip" title="Drag to move this bar">&#8942;</span>' +
    '<strong class="ed-selname">Nothing selected</strong>' +
    '<label>X <input type="number" step="0.1" data-f="x">%</label>' +
    '<label>Y <input type="number" step="0.1" data-f="y">%</label>' +
    '<label>W <input type="number" step="0.1" data-f="w">%</label>' +
    '<span class="ed-sp"></span>' +
    '<button data-a="undo">Undo</button><button data-a="reset">Reset</button>' +
    '<button data-a="copy">Copy</button><button data-a="download" class="ed-main">Download hero-layout.json</button>' +
    '<button data-a="help" title="Keys">?</button><button data-a="hide" title="Hide (H)">&times;</button>' +
    '</div>' +
    '<div class="ed-more" hidden>' +
    '<p>Click to select. Drag to move. Pull a corner to resize. Arrows nudge (Shift: 10px). [ ] scale 2%. , . send back / bring forward. Cmd-Z undo. Esc deselect. H hides this bar; drag the grip to move it.</p>' +
    '<textarea class="ed-out" rows="5" readonly placeholder="The layout JSON appears here when you copy."></textarea>' +
    '<p>Drop the file beside build.py and run <code>python3 build.py</code>; the live page then uses this layout.</p>' +
    '</div>';
  document.body.appendChild(panel);
  var pill = document.createElement('button');
  pill.className = 'ed-pill'; pill.textContent = 'Edit bar (H)'; pill.hidden = true;
  document.body.appendChild(pill);
  function toggleBar() { panel.hidden = !panel.hidden; pill.hidden = !panel.hidden; }
  pill.addEventListener('click', toggleBar);
  // the bar is draggable by its grip
  (function () {
    var grip = panel.querySelector('.ed-grip'), start = null;
    grip.addEventListener('pointerdown', function (e) {
      var r = panel.getBoundingClientRect();
      start = { x: e.clientX - r.left, y: e.clientY - r.top };
      panel.style.left = r.left + 'px'; panel.style.top = r.top + 'px'; panel.style.right = 'auto'; panel.style.bottom = 'auto';
      e.preventDefault();
      function mv(ev) { panel.style.left = (ev.clientX - start.x) + 'px'; panel.style.top = (ev.clientY - start.y) + 'px'; }
      document.addEventListener('pointermove', mv);
      document.addEventListener('pointerup', function () { document.removeEventListener('pointermove', mv); }, { once: true });
    });
  })();
  var fields = {};
  panel.querySelectorAll('input[data-f]').forEach(function (i) { fields[i.getAttribute('data-f')] = i; });

  function placeBox() {
    if (!selected) { box.style.display = 'none'; panel.querySelector('.ed-selname').textContent = 'Nothing selected'; return; }
    var r = selected.el.getBoundingClientRect(), h = hero.getBoundingClientRect();
    box.style.display = 'block';
    box.style.left = (r.left - h.left) + 'px';
    box.style.top = (r.top - h.top) + 'px';
    box.style.width = r.width + 'px';
    box.style.height = r.height + 'px';
    box.querySelector('.ed-name').textContent = selected.name;
    var b = selected.get();
    fields.x.value = b.x.toFixed(1); fields.y.value = b.y.toFixed(1); fields.w.value = b.w.toFixed(1);
    panel.querySelector('.ed-selname').textContent = selected.name;
  }
  function select(e) {
    editables.forEach(function (x) { x.el.classList.remove('ed-on'); });
    selected = e;
    if (e) e.el.classList.add('ed-on');
    placeBox();
  }

  /* ---------- history ---------- */
  var history = [];
  function snapshot() { return JSON.stringify(layout()); }
  function push() { history.push(snapshot()); if (history.length > 100) history.shift(); }
  function undo() {
    var s = history.pop();
    if (!s) return;
    apply(JSON.parse(s));
    placeBox();
  }

  /* ---------- the layout as data ---------- */
  function layout() {
    var out = { stage: [1920, 1083], order: [], layers: {}, text: {}, quality: {} };
    Array.prototype.slice.call(stage.querySelectorAll('.hero-item')).forEach(function (el) {
      var n = el.getAttribute('data-name'), s = el.style;
      out.order.push(n);
      out.layers[n] = { x: +num(s.getPropertyValue('--x')).toFixed(3), y: +num(s.getPropertyValue('--y')).toFixed(3), w: +num(s.getPropertyValue('--w')).toFixed(3) };
    });
    ['--tx', '--ty', '--tw', '--h1', '--lsz'].forEach(function (p) {
      var v = textBlock.style.getPropertyValue(p); if (v) out.text[p.slice(2)] = v;
    });
    ['--qr', '--qb', '--qs'].forEach(function (p) {
      var v = quality.style.getPropertyValue(p); if (v) out.quality[p.slice(2)] = v;
    });
    return out;
  }
  function apply(l) {
    l.order.forEach(function (n) {
      var el = stage.querySelector('.hero-item[data-name="' + n + '"]');
      if (!el) return;
      stage.appendChild(el);
      var b = l.layers[n];
      el.style.setProperty('--x', b.x + '%'); el.style.setProperty('--y', b.y + '%'); el.style.setProperty('--w', b.w + '%');
    });
    ['tx', 'ty', 'tw', 'h1', 'lsz'].forEach(function (k) {
      if (l.text[k]) textBlock.style.setProperty('--' + k, l.text[k]); else textBlock.style.removeProperty('--' + k);
    });
    ['qr', 'qb', 'qs'].forEach(function (k) {
      if (l.quality[k]) quality.style.setProperty('--' + k, l.quality[k]); else quality.style.removeProperty('--' + k);
    });
  }
  var built = snapshot();

  /* ---------- pointer: move and resize ---------- */
  var drag = null;
  function onDown(e) {
    var handle = e.target.closest('[data-h]');
    var target = handle ? selected : editables.filter(function (x) { return x.el.contains(e.target); })[0];
    if (!target) { if (!panel.contains(e.target) && !box.contains(e.target)) select(null); return; }
    e.preventDefault();
    if (target !== selected) select(target);
    push();
    var b = selected.get();
    drag = { mode: handle ? handle.getAttribute('data-h') : 'move', start: { x: e.clientX, y: e.clientY }, box: b };
    document.addEventListener('pointermove', onMove);
    document.addEventListener('pointerup', onUp, { once: true });
  }
  function onMove(e) {
    if (!drag) return;
    var s = stageRect();
    var dx = (e.clientX - drag.start.x) / s.width * 100;
    var dy = (e.clientY - drag.start.y) / s.height * 100;
    var b = drag.box, n = { x: b.x, y: b.y, w: b.w, h: b.h };
    if (drag.mode === 'move') {
      n.x = b.x + dx; n.y = b.y + dy;
      selected.set(n);
    } else {
      // resize from the opposite corner; width follows the pointer, height
      // keeps the item's own proportion (text scales its type with it)
      var right = b.x + b.w, bottom = b.y + b.h;
      var w;
      if (drag.mode === 'se' || drag.mode === 'ne') w = b.w + dx; else w = b.w - dx;
      w = Math.max(2, w);
      var scale = w / b.w;
      n.w = w; n.h = b.h * scale;
      n.x = (drag.mode === 'se' || drag.mode === 'ne') ? b.x : right - w;
      n.y = (drag.mode === 'se' || drag.mode === 'sw') ? b.y : bottom - n.h;
      if (selected.kind === 'text') { n.h1 = b.h1; n.list = b.list; selected.set(n, scale); }
      else if (selected.kind === 'quality') { n.size = b.size; selected.set(n, scale); }
      else selected.set(n);
    }
    placeBox();
  }
  function onUp() { drag = null; document.removeEventListener('pointermove', onMove); }
  hero.addEventListener('pointerdown', onDown);
  box.addEventListener('pointerdown', onDown);
  hero.addEventListener('click', function (e) { if (e.target.closest('.hero-item')) e.preventDefault(); }, true);

  /* ---------- keyboard ---------- */
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); undo(); return; }
    if (e.key === 'Escape') { select(null); return; }
    if (e.key === 'h' || e.key === 'H') { toggleBar(); return; }
    if (!selected) return;
    var s = stageRect(), step = e.shiftKey ? 10 : 1;
    var b = selected.get(), changed = true;
    if (e.key === 'ArrowLeft') b.x -= step / s.width * 100;
    else if (e.key === 'ArrowRight') b.x += step / s.width * 100;
    else if (e.key === 'ArrowUp') b.y -= step / s.height * 100;
    else if (e.key === 'ArrowDown') b.y += step / s.height * 100;
    else if (e.key === '[' || e.key === ']') {
      var sc = e.key === ']' ? 1.02 : 0.98;
      var cx = b.x + b.w / 2, cy = b.y + b.h / 2;
      b.w *= sc; b.h *= sc; b.x = cx - b.w / 2; b.y = cy - b.h / 2;
      push(); selected.set(b, sc); placeBox(); return;
    }
    else if ((e.key === ',' || e.key === '.') && selected.kind === 'item') {
      push();
      var el = selected.el;
      if (e.key === '.' && el.nextElementSibling) el.parentNode.insertBefore(el.nextElementSibling, el);
      if (e.key === ',' && el.previousElementSibling) el.parentNode.insertBefore(el, el.previousElementSibling);
      placeBox(); return;
    }
    else changed = false;
    if (changed) { e.preventDefault(); push(); selected.set(b); placeBox(); }
  });
  Object.keys(fields).forEach(function (k) {
    fields[k].addEventListener('change', function () {
      if (!selected) return;
      push();
      var b = selected.get(); b[k] = num(fields[k].value);
      if (k === 'w') { var sc = b.w / selected.get().w; b.h = selected.get().h * sc; selected.set(b, sc); }
      else selected.set(b);
      placeBox();
    });
  });

  /* ---------- actions ---------- */
  var out = panel.querySelector('.ed-out');
  panel.addEventListener('click', function (e) {
    var a = e.target.getAttribute && e.target.getAttribute('data-a');
    if (!a) return;
    if (a === 'undo') undo();
    if (a === 'hide') toggleBar();
    if (a === 'help') { var m = panel.querySelector('.ed-more'); m.hidden = !m.hidden; }
    if (a === 'reset') { push(); apply(JSON.parse(built)); placeBox(); }
    if (a === 'copy' || a === 'download') {
      var json = JSON.stringify(layout(), null, 1);
      out.value = json; panel.querySelector('.ed-more').hidden = false;
      if (a === 'copy' && navigator.clipboard) navigator.clipboard.writeText(json).catch(function () { out.select(); });
      if (a === 'download') {
        var blob = new Blob([json], { type: 'application/json' });
        var link = document.createElement('a');
        link.href = URL.createObjectURL(blob); link.download = 'hero-layout.json';
        document.body.appendChild(link); link.click(); link.remove();
      }
    }
  });
  window.addEventListener('resize', placeBox);
  window.addEventListener('scroll', placeBox, { passive: true });
})();
