/* Epiphany House pages loader.
   Put this in a GHL custom code element:
     <div class="eh-page" data-page="home"></div>
     <script src="https://steveyjones.github.io/eh-pages/loader.js"></script>
   data-page is the page shown first: home, budget, report or plan.
   Links between pages open in place, so one GHL page with data-page="home" is the whole portal.
   Content is fetched fresh and decrypted in the browser; the password is asked once per browser session. */
(function () {
  var BASE = window.EH_PAGES_BASE || 'https://steveyjones.github.io/eh-pages/';
  var PAGES = {
    home:        { title: 'Trustee portal', file: 'home.enc' },
    budget:      { title: 'Budget', file: 'budget.enc', xlsx: 'budget-xlsx.enc' },
    report:      { title: 'Trustee report', file: 'report.enc' },
    plan:        { title: 'Workplan', file: 'plan.enc' }
  };
  var KEYNAME = 'eh-pages-pw';

  function b64(s) { var r = atob(s), u = new Uint8Array(r.length); for (var i = 0; i < r.length; i++) u[i] = r.charCodeAt(i); return u; }
  function ss(get, v) { try { if (get) return sessionStorage.getItem(KEYNAME); if (v === null) sessionStorage.removeItem(KEYNAME); else sessionStorage.setItem(KEYNAME, v); } catch (e) { return null; } }
  function fetchJson(file) {
    return fetch(BASE + file + '?t=' + Date.now(), { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error('fetch ' + r.status); return r.json();
    });
  }
  function decrypt(enc, pw) {
    return crypto.subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveKey']).then(function (base) {
      return crypto.subtle.deriveKey({ name: 'PBKDF2', salt: b64(enc.s), iterations: enc.n, hash: 'SHA-256' }, base, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
    }).then(function (key) { return crypto.subtle.decrypt({ name: 'AES-GCM', iv: b64(enc.i) }, key, b64(enc.c)); });
  }
  function fmtDate(u) { try { return new Date(u).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }); } catch (e) { return ''; } }
  var manifestP = null;
  function manifest() { if (!manifestP) manifestP = fetchJson('manifest.json').catch(function () { return {}; }); return manifestP; }

  var CSS = '.eh-gate{display:flex;justify-content:center;padding:48px 16px;font-family:Jost,Inter,Arial,sans-serif}' +
    '.eh-gate form{width:100%;max-width:360px;background:#fff;border:1px solid #e3e6ea;border-radius:14px;padding:28px 24px;box-shadow:0 10px 30px rgba(31,52,66,.12);box-sizing:border-box;color:#1f2328}' +
    '.eh-gate h2{margin:0 0 6px;font-family:Fraunces,"Source Serif 4",Georgia,serif;font-weight:400;font-size:1.5rem}' +
    '.eh-gate p{margin:0 0 16px;font-size:.875rem;color:#5f6670}' +
    '.eh-gate label{display:block;font-size:.8125rem;margin-bottom:6px;color:#5f6670}' +
    '.eh-gate input{width:100%;box-sizing:border-box;padding:10px 12px;font:inherit;border:1px solid #c5cad1;border-radius:8px;margin-bottom:12px}' +
    '.eh-gate button{width:100%;padding:11px;font:inherit;font-weight:600;color:#fff;background:#1f3442;border:0;border-radius:8px;cursor:pointer}' +
    '.eh-gate button:disabled{opacity:.7;cursor:wait}' +
    '.eh-gate .eh-msg{min-height:1.2em;margin-top:10px;font-size:.8125rem;color:#b42318}' +
    '.eh-frame{display:block;width:100%;border:0;min-height:400px}' +
    '.eh-bar{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:12px;padding:10px 16px;background:#1f3442;color:#f0efed;font:14px Jost,Inter,Arial,sans-serif}' +
    '.eh-bar button{all:unset;cursor:pointer;display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:999px;border:1px solid rgba(240,239,237,.3);font-size:13px}' +
    '.eh-bar button:hover{background:rgba(240,239,237,.1)} .eh-bar b{font-weight:500} .eh-bar span{margin-left:auto;font-size:12px;opacity:.7}' +
    '.eh-bar .eh-print{background:#f0efed;color:#1f3442;border-color:#f0efed;font-weight:500} .eh-bar .eh-print:hover{background:#fff}' +
    '.eh-upd{display:flex;justify-content:flex-end;align-items:center;gap:12px;font:12px Jost,Inter,Arial,sans-serif;color:#5f6670;padding:6px 8px}' +
    '.eh-upd .eh-print{display:inline-flex;align-items:center;gap:6px;font:500 13px Jost,Inter,Arial,sans-serif;color:#1f3442;background:#fff;border:1px solid #c5cad1;border-radius:999px;padding:5px 12px;cursor:pointer}' +
    '.eh-load{font:14px Jost,Inter,Arial,sans-serif;color:#5f6670;padding:24px}';

  function noIndex() {
    // keep the host page out of search engines
    if (document.querySelector('meta[name="robots"][data-eh]')) return;
    var m = document.createElement('meta'); m.name = 'robots'; m.content = 'noindex, nofollow, noarchive'; m.setAttribute('data-eh', '1');
    document.head.appendChild(m);
  }
  noIndex();

  function addCss() {
    if (document.getElementById('eh-pages-css')) return;
    var s = document.createElement('style'); s.id = 'eh-pages-css'; s.textContent = CSS; document.head.appendChild(s);
  }

  // stretch the element to the full window width, whatever column GHL puts it in
  function bleed(el) {
    // drop the GHL section, row and column padding above and below
    for (var n = el.parentElement; n && n !== document.body; n = n.parentElement) {
      if (/\bc-(section|row|column)\b/.test(n.className || '')) {
        n.style.setProperty('padding-top', '0', 'important'); n.style.setProperty('padding-bottom', '0', 'important');
        n.style.setProperty('margin-top', '0', 'important'); n.style.setProperty('margin-bottom', '0', 'important');
      }
      if (/\bc-section\b/.test(n.className || '')) break;
    }
    function fit() {
      el.style.marginLeft = '0px'; el.style.width = '';
      var w = document.documentElement.clientWidth, left = el.getBoundingClientRect().left;
      el.style.width = w + 'px'; el.style.marginLeft = (-left) + 'px'; el.style.maxWidth = 'none';
    }
    fit(); window.addEventListener('resize', fit); setTimeout(fit, 500); setTimeout(fit, 2000);
  }

  function mount(el) {
    if (el.getAttribute('data-eh-done')) return; el.setAttribute('data-eh-done', '1');
    if (el.getAttribute('data-full') !== 'off') bleed(el);
    var start = el.getAttribute('data-page');
    if (!PAGES[start]) { el.textContent = 'Unknown page.'; return; }
    addCss();
    var portal = start === 'home';
    var pw = null, current = null;

    function wanted() { var h = (location.hash || '').slice(1); return portal && PAGES[h] ? h : start; }

    function show(name, html, updated) {
      var cfg = PAGES[name];
      el.innerHTML = '';
      var f = document.createElement('iframe');
      function printIt() { try { var w = f.contentWindow; if (w.ehPrint) w.ehPrint(); else { w.focus(); w.print(); } } catch (e) { window.print(); } }
      var PRINT_ICON = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M6 14h12v7H6z"/></svg>';
      if (portal) {
        var bar = document.createElement('div'); bar.className = 'eh-bar';
        bar.innerHTML = (name !== 'home' ? '<button type="button" class="eh-back">← Trustee home</button>' : '') +
          '<b></b><span></span><button type="button" class="eh-print" title="Print in black and white">' + PRINT_ICON + 'Print</button>';
        bar.querySelector('b').textContent = cfg.title;
        bar.querySelector('span').textContent = updated && name !== 'home' ? 'Updated ' + fmtDate(updated) : '';
        var back = bar.querySelector('.eh-back'); if (back) back.addEventListener('click', function () { go('home'); });
        bar.querySelector('.eh-print').addEventListener('click', printIt);
        el.appendChild(bar);
      }
      f.className = 'eh-frame'; f.title = cfg.title; f.setAttribute('scrolling', 'no');
      el.appendChild(f);
      if (!portal) {
        var upd = document.createElement('div'); upd.className = 'eh-upd';
        upd.innerHTML = '<button type="button" class="eh-print">' + PRINT_ICON + 'Print</button><span></span>';
        upd.querySelector('span').textContent = 'Updated ' + fmtDate(updated);
        upd.querySelector('.eh-print').addEventListener('click', printIt);
        el.insertBefore(upd, f);
      }
      function size() { try { var d = f.contentDocument; if (d && d.documentElement) f.style.height = Math.max(d.documentElement.scrollHeight, d.body ? d.body.scrollHeight : 0) + 'px'; } catch (e) {} }
      f.addEventListener('load', function () {
        size();
        try {
          var d = f.contentDocument;
          d.documentElement.classList.add('eh-in-portal');
          if (window.ResizeObserver && d.body) new ResizeObserver(size).observe(d.body);
          setTimeout(size, 400); setTimeout(size, 1500);
          // links to other pages open in place; outside links open in a new tab
          d.addEventListener('click', function (e) {
            var a = e.target.closest && e.target.closest('[data-go]');
            if (a && PAGES[a.getAttribute('data-go')]) { e.preventDefault(); go(a.getAttribute('data-go')); }
          });
          Array.prototype.forEach.call(d.querySelectorAll('a[href^="http"]'), function (a) { if (!a.target) a.target = '_blank'; });
          // updated dates on the home page
          manifest().then(function (mf) {
            Array.prototype.forEach.call(d.querySelectorAll('[data-updated]'), function (s) { var u = mf[s.getAttribute('data-updated')]; if (u) s.textContent = fmtDate(u); });
          });
          var dl = d.getElementById('eh-dl');
          if (dl && cfg.xlsx) dl.addEventListener('click', function (e) {
            e.preventDefault(); var old = dl.textContent; dl.textContent = 'Preparing download…';
            fetchJson(cfg.xlsx).then(function (enc) {
              return decrypt(enc, pw).then(function (bytes) {
                var url = URL.createObjectURL(new Blob([bytes], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
                var a = document.createElement('a'); a.href = url; a.download = enc.name || 'EH budget.xlsx';
                document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(url); }, 3000);
              });
            }).catch(function (err) { console.error(err); }).then(function () { dl.textContent = old; });
          });
        } catch (e) { console.error(e); }
      });
      window.addEventListener('resize', size);
      f.srcdoc = html;
    }

    function load(name) {
      current = name;
      el.innerHTML = '<p class="eh-load">Loading…</p>';
      return fetchJson(PAGES[name].file).then(function (enc) {
        return decrypt(enc, pw).then(function (buf) {
          if (current !== name) return;
          show(name, new TextDecoder().decode(buf), enc.u);
          if (portal) { var top = el.getBoundingClientRect().top + window.pageYOffset; if (window.pageYOffset > top) window.scrollTo(0, Math.max(0, top - 10)); }
        });
      });
    }

    function go(name) {
      if (portal) {
        var h = name === 'home' ? '' : name;
        if ((location.hash || '').slice(1) !== h) { history.pushState(null, '', h ? '#' + h : location.pathname + location.search); }
      }
      load(name).catch(function (err) { el.innerHTML = '<p class="eh-load">Could not load this page. Refresh to try again.</p>'; console.error(err); });
    }

    if (portal) window.addEventListener('popstate', function () { if (pw) load(wanted()).catch(function () {}); });

    function attempt(p) {
      pw = p;
      return load(wanted()).then(function () { ss(false, p); });
    }
    function gate(msg) {
      el.innerHTML = '<div class="eh-gate"><form autocomplete="off"><h2></h2><p>For trustees and Co-Leads. Enter the password to view.</p>' +
        '<label>Password</label><input type="password" required><button type="submit">Open</button><div class="eh-msg" aria-live="polite"></div></form></div>';
      el.querySelector('h2').textContent = portal ? 'Epiphany House trustees' : PAGES[start].title;
      var form = el.querySelector('form'), input = el.querySelector('input'), btn = el.querySelector('button'), m = el.querySelector('.eh-msg');
      if (msg) m.textContent = msg;
      form.addEventListener('submit', function (e) {
        e.preventDefault(); btn.disabled = true; btn.textContent = 'Checking…'; m.textContent = '';
        attempt(input.value.trim()).catch(function (err) {
          gate(/fetch/.test(String(err && err.message)) ? 'Could not load the page. Check your connection and refresh.' : 'That password is not right. Try again.');
        });
      });
      input.focus();
    }
    var saved = ss(true);
    if (saved) attempt(saved).catch(function () { ss(false, null); pw = null; gate(); }); else gate();
  }

  function init() { Array.prototype.forEach.call(document.querySelectorAll('.eh-page'), mount); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  // GHL can render custom code late
  setTimeout(init, 1000); setTimeout(init, 3000);
  try { new MutationObserver(function () { init(); }).observe(document.documentElement, { childList: true, subtree: true }); } catch (e) {}
})();
