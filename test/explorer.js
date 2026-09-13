// Explorer gate (2026-09-13). Drives the category explorer with real input over
// CDP and asserts what verify() cannot see: one panel at a time, ARIA state,
// arrow keys, deep links, the phone chip row sticking, and the whole catalogue
// staying readable with scripting OFF (rule 31).
// Usage: node test/explorer.js [baseUrl]   (needs the az-landing server, 8804)
const { spawn } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path'), http = require('http');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const BASE = process.argv[2] || 'http://localhost:8804/';
const PORT = 9800 + Math.floor(Math.random() * 150);
const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'az-explorer-'));
const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + PORT, '--user-data-dir=' + PROFILE, '--no-first-run', '--disable-gpu', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const getJSON = u => new Promise((res, rej) => http.get(u, r => { let d = ''; r.on('data', c => d += c); r.on('end', () => { try { res(JSON.parse(d)); } catch (e) { rej(e); } }); }).on('error', rej));
let pass = 0, failed = 0;
const check = (name, ok, detail = '') => { if (ok) pass++; else failed++; console.log((ok ? '  ok   ' : '  FAIL ') + name + (ok || !detail ? '' : '  -> ' + detail)); };

(async () => {
  let ver; for (let i = 0; i < 80; i++) { try { ver = await getJSON(`http://127.0.0.1:${PORT}/json/version`); break; } catch (e) { await sleep(200); } }
  const ws = new WebSocket(ver.webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
  let id = 0; const pend = new Map(); const errors = [];
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { const { res, rej } = pend.get(m.id); pend.delete(m.id); m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result); } else if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text); };
  const send = (method, params = {}, s) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params, sessionId: s })); });

  async function open(url, { w, h, mobile, js = true, block = null }) {
    const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
    const { sessionId: S } = await send('Target.attachToTarget', { targetId, flatten: true });
    await send('Page.enable', {}, S); await send('Runtime.enable', {}, S);
    if (block) { await send('Network.enable', {}, S); await send('Network.setBlockedURLs', { urls: [block] }, S); }
    await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile }, S);
    if (!js) await send('Emulation.setScriptExecutionDisabled', { value: true }, S);
    await send('Page.navigate', { url }, S); await sleep(1800);
    const ev = async e => { const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true }, S); if (r.exceptionDetails) throw new Error(e.slice(0, 60) + ' :: ' + JSON.stringify(r.exceptionDetails.exception?.description || r.exceptionDetails.text)); return r.result.value; };
    // Scroll INSTANTLY, let layout settle, THEN measure. The page sets
    // scroll-behavior:smooth, so measuring in the same tick as scrollIntoView
    // reads the pre-scroll position and the click lands on whatever used to be
    // there (the first run of this gate failed five checks exactly that way).
    const click = async sel => {
      await ev(`document.querySelector(${JSON.stringify(sel)}).scrollIntoView({block:'center', inline:'center', behavior:'instant'})`); await sleep(350);
      const b = await ev(`(()=>{const r=document.querySelector(${JSON.stringify(sel)}).getBoundingClientRect(); return {x:r.left+r.width/2, y:r.top+r.height/2}})()`);
      for (const type of ['mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x: b.x, y: b.y, button: 'left', clickCount: 1 }, S); await sleep(500); };
    const key = async k => { const codes = { ArrowRight: 39, ArrowLeft: 37, ArrowDown: 40, ArrowUp: 38, End: 35, Home: 36 };
      for (const type of ['keyDown', 'keyUp']) await send('Input.dispatchKeyEvent', { type, key: k, code: k, windowsVirtualKeyCode: codes[k] }, S); await sleep(300); };
    const state = () => ev(`(()=>{const t=[...document.querySelectorAll('.ex-tab')], p=[...document.querySelectorAll('.ex-panel')];
      return {tabs:t.length, roles:t.every(x=>x.getAttribute('role')==='tab'), selected:t.filter(x=>x.getAttribute('aria-selected')==='true').map(x=>x.getAttribute('href').slice(1)),
        shown:p.filter(x=>getComputedStyle(x).display!=='none').map(x=>x.id), hash:location.hash, focus:document.activeElement&&document.activeElement.getAttribute('href'),
        tabindex:t.map(x=>x.tabIndex), controls:t.every(x=>document.getElementById(x.getAttribute('aria-controls')))}})()`);
    return { S, ev, click, key, state, close: () => send('Target.closeTarget', { targetId }) };
  }

  console.log('phone 375, scripting on');
  let p = await open(BASE, { w: 375, h: 812, mobile: true });
  let s = await p.state();
  check('12 tabs, all role=tab, each controls a real panel', s.tabs === 12 && s.roles && s.controls, JSON.stringify(s));
  check('exactly one panel shows on load, and it is the first', s.shown.length === 1 && s.shown[0] === 'business-cards', s.shown.join(','));
  check('selected tab agrees with the shown panel', s.selected.length === 1 && s.selected[0] === s.shown[0]);
  check('roving tabindex: one 0, the rest -1', s.tabindex.filter(x => x === 0).length === 1 && s.tabindex.filter(x => x === -1).length === 11);
  await p.click('.ex-tab[href="#signs"]');
  s = await p.state();
  check('tap Signs shows only the Signs panel', s.shown.length === 1 && s.shown[0] === 'signs', s.shown.join(','));
  check('tap updates the URL hash', s.hash === '#signs', s.hash);
  const chip = await p.ev(`(()=>{const i=document.querySelector('.ex-index'); const t=document.querySelector('.ex-tab[href="#signs"]').getBoundingClientRect(); return {pos:getComputedStyle(i).position, inRow: t.left>=-1 && t.right<=innerWidth+1}})()`);
  check('phone chip row is sticky', chip.pos === 'sticky', chip.pos);
  check('the chosen chip is scrolled into the visible row', chip.inRow);
  await p.ev(`window.scrollTo(0, document.getElementById('signs').getBoundingClientRect().top + scrollY + 500)`); await sleep(400);
  const stuck = await p.ev(`(()=>{const i=document.querySelector('.ex-index').getBoundingClientRect(); const h=document.querySelector('.head').getBoundingClientRect(); return Math.abs(i.top - h.bottom) <= 2})()`);
  check('chip row sits directly under the header while reading a panel', stuck);
  await p.close();

  console.log('desktop 1280, scripting on');
  p = await open(BASE, { w: 1280, h: 900, mobile: false });
  await p.ev(`document.querySelector('.ex-tab').focus()`);
  await p.key('ArrowDown'); s = await p.state();
  check('ArrowDown moves selection and focus to the next category', s.selected[0] === 'marketing-materials' && s.focus === '#marketing-materials', JSON.stringify(s.selected) + ' focus ' + s.focus);
  await p.key('End'); s = await p.state();
  check('End jumps to the last category', s.selected[0] === 'canvas-photo-prints' && s.shown[0] === 'canvas-photo-prints');
  await p.key('ArrowDown'); s = await p.state();
  check('ArrowDown on the last wraps to the first', s.selected[0] === 'business-cards');
  const orient = await p.ev(`document.querySelector('.ex-index').getAttribute('aria-orientation')`);
  check('desktop index reports vertical orientation', orient === 'vertical', orient);
  await p.click('.foot-col a[href="#apparel"]'); s = await p.state();
  check('a footer link opens its category', s.shown.length === 1 && s.shown[0] === 'apparel', s.shown.join(','));
  // The trip from the footer is a long smooth scroll: poll for the END state a
  // visitor sees, rather than sampling one instant mid-flight.
  const inView = await p.ev(`new Promise(res=>{const t0=Date.now(); (function poll(){const r=document.querySelector('.ex-panels').getBoundingClientRect(); if(r.top>=0 && r.top<innerHeight*0.7) return res({ok:true, top:Math.round(r.top), ms:Date.now()-t0}); if(Date.now()-t0>2500) return res({ok:false, top:Math.round(r.top), y:Math.round(scrollY)}); setTimeout(poll,100);})();})`);
  check('...and scrolls the panel into view', inView.ok, JSON.stringify(inView));
  await p.close();

  console.log('deep link #vinyl-graphics');
  p = await open(BASE + '#vinyl-graphics', { w: 375, h: 812, mobile: true });
  await sleep(800); s = await p.state();
  check('a deep link opens that category on load', s.shown.length === 1 && s.shown[0] === 'vinyl-graphics', s.shown.join(','));
  await p.close();

  console.log('phone 375, scripting OFF');
  p = await open(BASE, { w: 375, h: 812, mobile: true, js: false });
  const nojs = await p.ev(`(()=>({shown:[...document.querySelectorAll('.ex-panel')].filter(x=>getComputedStyle(x).display!=='none').length, hidden:[...document.querySelectorAll('.ex-panel[hidden]')].length, jsClass:document.documentElement.classList.contains('js')}))()`).catch(e => ({ err: String(e) }));
  check('with scripting off, all 12 panels are readable', nojs.shown === 12 && nojs.hidden === 0 && !nojs.jsClass, JSON.stringify(nojs));
  await p.close();

  console.log('phone 375, head script runs but the explorer script is BLOCKED');
  p = await open(BASE, { w: 375, h: 812, mobile: true, block: '*landing.js*' });
  const early = await p.ev(`[...document.querySelectorAll('.ex-panel')].filter(x=>getComputedStyle(x).display!=='none').length`);
  check('before the failsafe, only the first panel paints (no twelve-panel flash)', early === 1, 'shown ' + early);
  await sleep(4200);
  const late = await p.ev(`(()=>({shown:[...document.querySelectorAll('.ex-panel')].filter(x=>getComputedStyle(x).display!=='none').length, failsafe:document.documentElement.classList.contains('js-failsafe'), gap:getComputedStyle(document.querySelector('.ex-panels')).rowGap}))()`);
  check('after 4s the failsafe reveals all 12 panels, spaced apart', late.shown === 12 && late.failsafe && late.gap === '56px', JSON.stringify(late));
  await p.close();

  check('no script exceptions anywhere', errors.length === 0, errors.join(' | '));
  console.log(`\n${pass} passed, ${failed} failed`);
  ws.close(); chrome.kill(); try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) {}
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); chrome.kill(); process.exit(1); });
