"""Build the trustee homepage (dashboard + links) from a data file.

usage: python3 build_home.py DATA.json LOGO.txt OUT.html
DATA.json and the logo are kept outside this repository; only the encrypted page is published.
"""
import json, sys, html
data = json.load(open(sys.argv[1], encoding='utf-8'))
logo = open(sys.argv[2]).read().strip()
e = html.escape

ICONS = {
 'chart': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
 'doc': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6M9 13h8M9 17h6"/></svg>',
 'plan': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4M7 14h4M7 17h7"/></svg>',
}
ARROW = '<svg class="arr" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

m = data['meeting']
kpis = ''.join(
    f'<a class="kpi {k["tone"]}" href="#{k["go"]}" data-go="{k["go"]}"><span class="kk">{e(k["k"])}</span>'
    f'<span class="kv">{e(k["v"])}</span><span class="ks">{e(k["sub"])}</span></a>' for k in data.get('kpis', []))
top = max([v for _, v, _ in data.get('forward', [])] or [1])
scale = 4000 if top <= 4000 else (int(top / 1000) + 1) * 1000
bars = ''.join(
    f'<div class="fb{" past" if past else ""}{" low" if (not past and v < 1300) else ""}" style="--h:{v / scale * 100:.1f}%">'
    f'<b>£{v / 1000:.1f}k</b><i></i><span>{e(mo)}</span></div>' for mo, v, past in data.get('forward', []))
decisions = ''.join(
    f'<li><span class="tag t-{e(t.lower())}">{e(t)}</span><div><strong>{e(h)}</strong>{"<p>" + e(p) + "</p>" if p else ""}</div></li>'
    for t, h, p in data.get('decisions', []))
papers = ''.join(
    f'<a class="paper" href="#{p["go"]}" data-go="{p["go"]}"><span class="ic">{ICONS.get(p["icon"], "")}</span>'
    f'<span class="pk">{e(p["kicker"])}</span><span class="pt">{e(p["title"])}</span><span class="pd">{e(p["desc"])}</span>'
    f'<span class="pu">Updated <span data-updated="{p["go"]}">—</span>{ARROW}</span></a>' for p in data['papers'])
library = ''.join(
    f'<a class="lib" href="#{l["go"]}" data-go="{l["go"]}"><span class="lt">{e(l["title"])}</span>'
    f'<span class="ld">{e(l["desc"])}</span><span class="lg">{e(l["tag"])}</span></a>' for l in data.get('library', []))
coming = ''.join(f'<li>{e(c)}</li>' for c in data.get('coming', []))
later = ' · '.join(e(x) for x in data.get('later_meetings', []))
extra = ''
if data.get('forward'):
    extra = f'''  <section class="grid2">
    <div class="card"><h3>Room hire in the diary</h3><p class="small muted" style="margin:0">Listed paid hire by month, from Checkfront. CotE and EH's own use are not charged.</p>
      <div class="fwd" role="img" aria-label="Listed paid hire by month">{bars}</div>
      <div class="legend"><span><i style="background:var(--ink)"></i>This report</span><span><i style="background:var(--navy)"></i>Booked ahead</span><span><i style="background:var(--gold)"></i>Under £1,300 a month</span></div></div>
    <div class="card"><h3>For the trustees on {e(m["label"].split(" ",1)[1])}</h3><p class="small muted" style="margin:0">From section 8 of the report.</p><ul class="dec">{decisions}</ul></div>
  </section>



'''

page = f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Epiphany House · Trustees</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,300..500,100,1&family=Jost:wght@300..600&display=swap">
<style>
:root{{--ink:#1f3442;--navy:#3e6379;--gold:#dca13c;--leaf:#0b6844;--rust:#a3402e;--paper:#faf9f7;--panel:#fff;--line:#e3dfd8;--fg:#22323c;--muted:#5f6a68;
--display:"Fraunces",Georgia,serif;--body:"Jost","Avenir Next","Segoe UI",sans-serif}}
*{{box-sizing:border-box}}
html,body{{margin:0;background:var(--paper);color:var(--fg);font-family:var(--body);font-weight:350;font-size:16px;line-height:1.55}}
a{{color:inherit;text-decoration:none}}
.wrap{{max-width:1280px;margin:0 auto;padding:0 20px}}
/* hero */
.hero{{background:var(--ink);color:#f0efed;position:relative;overflow:hidden;padding:36px 0 120px}}
.hero::before,.hero::after{{content:"";position:absolute;border-radius:50%;border:1px solid rgba(220,161,60,.35);pointer-events:none}}
.hero::before{{width:520px;height:520px;right:-140px;top:-180px;box-shadow:0 0 0 46px rgba(220,161,60,.05),0 0 0 110px rgba(220,161,60,.035)}}
.hero::after{{width:220px;height:220px;left:-90px;bottom:-110px;border-color:rgba(240,239,237,.12)}}
.hero .wrap{{position:relative;z-index:1}}
.toprow{{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}}
.logo{{width:min(300px,62vw);height:auto;display:block}}
.private{{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:rgba(240,239,237,.7);border:1px solid rgba(240,239,237,.25);border-radius:999px;padding:5px 12px;display:inline-flex;gap:8px;align-items:center}}
.private svg{{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:2}}
.eyebrow{{margin-top:44px;font-size:.78rem;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);font-weight:500}}
h1{{font-family:var(--display);font-weight:300;font-size:clamp(2.2rem,5.6vw,3.9rem);line-height:1.04;margin:.25em 0 .3em;font-variation-settings:"SOFT" 100,"WONK" 1;max-width:20ch}}
h1 em{{font-style:italic;color:var(--gold)}}
.meet{{display:inline-grid;grid-template-columns:auto 1fr;gap:4px 18px;align-items:center;margin-top:10px;padding:16px 20px;border-radius:14px;background:rgba(240,239,237,.07);border:1px solid rgba(240,239,237,.14);backdrop-filter:blur(4px)}}
.count{{grid-row:span 2;font-family:var(--display);font-weight:300;font-size:2.8rem;line-height:1;color:var(--gold);min-width:2ch;text-align:center}}
.count small{{display:block;font-family:var(--body);font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:rgba(240,239,237,.65);margin-top:6px}}
.mt{{font-weight:500}} .ms{{font-size:.88rem;color:rgba(240,239,237,.7)}}
/* kpis */
.lift{{margin-top:-84px;position:relative;z-index:2}}
.kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:-84px;position:relative;z-index:2}}
.kpi{{display:flex;flex-direction:column;gap:6px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px 20px;box-shadow:0 10px 30px rgba(31,52,66,.08);transition:transform .2s,box-shadow .2s;position:relative;overflow:hidden}}
.kpi::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--navy)}}
.kpi.bad::before{{background:var(--rust)}} .kpi.ok::before{{background:var(--leaf)}} .kpi.warn::before{{background:var(--gold)}}
.kpi:hover{{transform:translateY(-3px);box-shadow:0 16px 36px rgba(31,52,66,.14)}}
.kk{{font-size:.74rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:500}}
.kv{{font-family:var(--display);font-weight:300;font-size:2.5rem;line-height:1.05;font-variant-numeric:tabular-nums}}
.kpi.bad .kv{{color:var(--rust)}}
.ks{{font-size:.86rem;color:var(--muted);line-height:1.4}}
/* sections */
section{{margin-top:56px}}
h2{{font-family:var(--display);font-weight:400;font-size:clamp(1.4rem,2.6vw,1.8rem);margin:0 0 14px;display:flex;align-items:baseline;gap:12px}}
h2 .rule{{flex:1;height:1px;background:var(--line);transform:translateY(-6px)}}
.grid2{{display:grid;grid-template-columns:1.1fr .9fr;gap:22px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px 22px}}
.card h3{{margin:0 0 4px;font-weight:500;font-size:1rem}}
.muted{{color:var(--muted)}} .small{{font-size:.86rem}}
/* forward book */
.fwd{{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;align-items:end;height:250px;margin-top:18px;padding-top:22px}}
.fb{{position:relative;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center}}
.fb i{{display:block;width:100%;height:var(--h);min-height:3px;background:var(--navy);border-radius:6px 6px 2px 2px;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.7,.2,1) both}}
.fb.past i{{background:var(--ink)}} .fb.low i{{background:var(--gold)}}
.fb b{{font-size:.72rem;font-weight:500;margin-bottom:5px;white-space:nowrap}}
.fb span{{position:absolute;bottom:-22px;font-size:.76rem;color:var(--muted)}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
.legend{{display:flex;flex-wrap:wrap;gap:14px;margin-top:34px;font-size:.78rem;color:var(--muted)}}
.legend i{{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}}
/* decisions */
.dec{{list-style:none;margin:10px 0 0;padding:0}}
.dec li{{display:grid;grid-template-columns:76px 1fr;gap:12px;padding:12px 0;border-bottom:1px solid var(--line)}}
.dec li:last-child{{border-bottom:0}}
.dec strong{{font-weight:500}} .dec p{{margin:2px 0 0;font-size:.86rem;color:var(--muted)}}
.tag{{align-self:start;justify-self:start;font-size:.66rem;letter-spacing:.12em;text-transform:uppercase;font-weight:600;padding:3px 8px;border-radius:999px;background:rgba(62,99,121,.12);color:var(--navy)}}
.t-decide{{background:rgba(163,64,46,.12);color:var(--rust)}} .t-confirm{{background:rgba(220,161,60,.18);color:#8a5b12}}
/* papers */
.papers{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
.paper{{display:flex;flex-direction:column;gap:6px;padding:22px;border-radius:16px;background:var(--panel);border:1px solid var(--line);position:relative;overflow:hidden;transition:transform .2s,box-shadow .2s,border-color .2s}}
.paper:hover{{transform:translateY(-3px);box-shadow:0 16px 36px rgba(31,52,66,.12);border-color:var(--gold)}}
.paper .ic{{width:46px;height:46px;border-radius:12px;background:var(--ink);display:grid;place-items:center;margin-bottom:8px}}
.paper .ic svg{{width:22px;height:22px;stroke:var(--gold);fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}}
.pk{{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);font-weight:500}}
.pt{{font-family:var(--display);font-size:1.6rem;font-weight:400;line-height:1.1}}
.pd{{font-size:.9rem;color:var(--muted);flex:1}}
.pu{{display:flex;align-items:center;gap:6px;font-size:.8rem;color:var(--muted);margin-top:10px;padding-top:12px;border-top:1px solid var(--line)}}
.arr{{width:18px;height:18px;margin-left:auto;stroke:var(--navy);fill:none;stroke-width:2;transition:transform .2s}}
.paper:hover .arr{{transform:translateX(4px)}}
/* library */
.libs{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.lib{{display:flex;flex-direction:column;gap:4px;padding:16px 18px;border-radius:12px;border:1px solid var(--line);background:var(--panel);transition:border-color .2s,background .2s}}
.lib:hover{{border-color:var(--navy);background:#f6f8f9}}
.lt{{font-weight:500}} .ld{{font-size:.84rem;color:var(--muted);flex:1}}
.lg{{font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--navy);margin-top:6px}}
.coming{{margin-top:14px;font-size:.84rem;color:var(--muted)}}
.coming ul{{display:inline;list-style:none;padding:0;margin:0}} .coming li{{display:inline}} .coming li+li::before{{content:" · "}}
footer{{margin:64px 0 0;padding:22px 0 36px;border-top:1px solid var(--line);font-size:.8rem;color:var(--muted);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}}
:focus-visible{{outline:2px solid var(--gold);outline-offset:3px;border-radius:8px}}
@media (max-width:900px){{.kpis,.papers{{grid-template-columns:1fr 1fr}}.libs{{grid-template-columns:1fr 1fr}}.grid2{{grid-template-columns:1fr}}}}
@media (max-width:560px){{.kpis,.papers,.libs{{grid-template-columns:1fr}}.hero{{padding-bottom:100px}}.fwd{{gap:6px}}.fb b{{font-size:.62rem}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
</style></head><body>
<header class="hero"><div class="wrap">
  <div class="toprow"><img class="logo" src="{logo}" alt="Epiphany House">
  <span class="private"><svg viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>Trustees and Co-Leads only</span></div>
  <div class="eyebrow">Trustee portal</div>
  <h1>The house, <em>at a glance</em></h1>
  <div class="meet" data-meet="{e(m["iso"])}"><div class="count"><span id="cd">–</span><small id="cdl">days to go</small></div>
  <div class="mt">Next meeting: {e(m["label"])}, {e(m["time"])}, {e(m["place"])}</div>
  <div class="ms">Then {later}</div></div>
</div></header>
<main class="wrap">
  {'<div class="kpis">'+kpis+'</div>' if kpis else ''}

  <section class="{'' if kpis else 'lift'}">{'<h2>The three papers <span class="rule"></span></h2>' if kpis else ''}<div class="papers">{papers}</div></section>

  {extra}

  <footer><span>Epiphany House, Truro · private to trustees and Co-Leads</span><span>Figures to {e(data["data_to"])}</span></footer>
</main>
<script type="application/json" id="home-data">{html.escape(json.dumps(data, ensure_ascii=False))}</script>
<script>
(function(){{var el=document.querySelector('[data-meet]');if(!el)return;var d=new Date(el.getAttribute('data-meet'));
var now=new Date();var days=Math.round((new Date(d.getFullYear(),d.getMonth(),d.getDate())-new Date(now.getFullYear(),now.getMonth(),now.getDate()))/864e5);
var c=document.getElementById('cd'),l=document.getElementById('cdl');
if(days>1){{c.textContent=days;l.textContent='days to go'}}else if(days===1){{c.textContent='1';l.textContent='day to go'}}else if(days===0){{c.textContent='Today';c.style.fontSize='1.6rem'}}else{{c.textContent='✓';l.textContent='held'}}}})();
</script>
</body></html>'''
open(sys.argv[3], 'w', encoding='utf-8').write(page)
print(sys.argv[3], len(page))
