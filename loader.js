/* Epiphany House pages loader.
   Put this in a GHL custom code element:
     <div class="eh-page" data-page="budget"></div>
     <script src="https://steveyjones.github.io/eh-pages/loader.js"></script>
   data-page is budget, report or plan. Content is fetched fresh and decrypted in the browser. */
(function () {
  var BASE = window.EH_PAGES_BASE || 'https://steveyjones.github.io/eh-pages/';
  var PAGES = {
    budget: { title: 'Epiphany House Budget', file: 'budget.enc', xlsx: 'budget-xlsx.enc' },
    report: { title: 'EH Trustee Report', file: 'report.enc' },
    plan:   { title: 'EH Workplan', file: 'plan.enc' }
  };
  var KEYNAME = 'eh-pages-pw';

  function b64(s) { var r = atob(s), u = new Uint8Array(r.length); for (var i = 0; i < r.length; i++) u[i] = r.charCodeAt(i); return u; }
  function ss(get, v) { try { if (get) return sessionStorage.getItem(KEYNAME); if (v === null) sessionStorage.removeItem(KEYNAME); else sessionStorage.setItem(KEYNAME, v); } catch (e) { return null; } }
  function fetchEnc(file) {
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

  var CSS = '.eh-gate{display:flex;justify-content:center;padding:48px 16px;font-family:Inter,Arial,sans-serif}' +
    '.eh-gate form{width:100%;max-width:360px;background:#fff;border:1px solid #e3e6ea;border-radius:12px;padding:28px 24px;box-shadow:0 8px 28px rgba(31,58,77,.12);box-sizing:border-box;color:#1f2328}' +
    '.eh-gate h2{margin:0 0 6px;font-family:"Source Serif 4",Georgia,serif;font-weight:400;font-size:1.5rem}' +
    '.eh-gate p{margin:0 0 16px;font-size:.875rem;color:#5f6670}' +
    '.eh-gate label{display:block;font-size:.8125rem;margin-bottom:6px;color:#5f6670}' +
    '.eh-gate input{width:100%;box-sizing:border-box;padding:10px 12px;font:inherit;border:1px solid #c5cad1;border-radius:8px;margin-bottom:12px}' +
    '.eh-gate button{width:100%;padding:11px;font:inherit;font-weight:600;color:#fff;background:#1F3A4D;border:0;border-radius:8px;cursor:pointer}' +
    '.eh-gate button:disabled{opacity:.7;cursor:wait}' +
    '.eh-gate .eh-msg{min-height:1.2em;margin-top:10px;font-size:.8125rem;color:#b42318}' +
    '.eh-frame{display:block;width:100%;border:0;min-height:400px}' +
    '.eh-upd{font:12px Inter,Arial,sans-serif;color:#5f6670;text-align:right;padding:4px 8px}';

  function addCss() {
    if (document.getElementById('eh-pages-css')) return;
    var s = document.createElement('style'); s.id = 'eh-pages-css'; s.textContent = CSS; document.head.appendChild(s);
  }

  function show(el, cfg, html, pw, updated) {
    el.innerHTML = '';
    var f = document.createElement('iframe');
    f.className = 'eh-frame'; f.title = cfg.title; f.setAttribute('scrolling', 'no');
    el.appendChild(f);
    var upd = document.createElement('div'); upd.className = 'eh-upd'; upd.textContent = 'Updated ' + fmtDate(updated);
    el.appendChild(upd);
    function size() { try { var d = f.contentDocument; if (d && d.documentElement) f.style.height = Math.max(d.documentElement.scrollHeight, d.body ? d.body.scrollHeight : 0) + 'px'; } catch (e) {} }
    f.addEventListener('load', function () {
      size();
      try {
        var d = f.contentDocument;
        if (window.ResizeObserver && d.body) new ResizeObserver(size).observe(d.body);
        setTimeout(size, 400); setTimeout(size, 1500);
        // links open outside the frame
        Array.prototype.forEach.call(d.querySelectorAll('a[href^="http"]'), function (a) { if (!a.target) a.target = '_blank'; });
        var dl = d.getElementById('eh-dl');
        if (dl && cfg.xlsx) dl.addEventListener('click', function (e) {
          e.preventDefault(); var old = dl.textContent; dl.textContent = 'Preparing download…';
          fetchEnc(cfg.xlsx).then(function (enc) {
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

  function mount(el) {
    if (el.getAttribute('data-eh-done')) return; el.setAttribute('data-eh-done', '1');
    var cfg = PAGES[el.getAttribute('data-page')];
    if (!cfg) { el.textContent = 'Unknown page.'; return; }
    addCss();
    var encP = fetchEnc(cfg.file);
    function attempt(pw) {
      return encP.then(function (enc) {
        return decrypt(enc, pw).then(function (buf) { ss(false, pw); show(el, cfg, new TextDecoder().decode(buf), pw, enc.u); });
      });
    }
    function gate(msg) {
      el.innerHTML = '<div class="eh-gate"><form autocomplete="off"><h2></h2><p>For trustees and Co-Leads. Enter the password to view.</p>' +
        '<label>Password</label><input type="password" required><button type="submit">Open</button><div class="eh-msg" aria-live="polite"></div></form></div>';
      el.querySelector('h2').textContent = cfg.title;
      var form = el.querySelector('form'), input = el.querySelector('input'), btn = el.querySelector('button'), m = el.querySelector('.eh-msg');
      if (msg) m.textContent = msg;
      form.addEventListener('submit', function (e) {
        e.preventDefault(); btn.disabled = true; btn.textContent = 'Checking…'; m.textContent = '';
        attempt(input.value.trim()).catch(function (err) {
          btn.disabled = false; btn.textContent = 'Open';
          m.textContent = /fetch/.test(String(err && err.message)) ? 'Could not load the page. Check your connection and refresh.' : 'That password is not right. Try again.';
          input.select();
        });
      });
    }
    var saved = ss(true);
    if (saved) { el.innerHTML = '<p style="font:14px Inter,Arial,sans-serif;color:#5f6670;padding:24px">Loading…</p>'; attempt(saved).catch(function () { ss(false, null); gate(); }); } else gate();
  }

  function init() { Array.prototype.forEach.call(document.querySelectorAll('.eh-page'), mount); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  // GHL can render custom code late
  setTimeout(init, 1000); setTimeout(init, 3000);
})();
