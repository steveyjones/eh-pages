"""Render a Markdown paper as a standalone EH-styled page.

usage: python3 render_doc.py IN.md OUT.html "Kicker text"
"""
import sys, re, html, markdown
src, out, kicker = sys.argv[1], sys.argv[2], sys.argv[3]
md = open(src, encoding='utf-8').read()
m = re.match(r'#\s+(.+)\n', md)
title = m.group(1).strip() if m else 'Epiphany House'
body_md = md[m.end():] if m else md
body = markdown.markdown(body_md, extensions=['tables', 'sane_lists'])
page = f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300..500&family=Jost:wght@300..600&display=swap">
<style>
:root{{--ink:#1f3442;--navy:#3e6379;--gold:#dca13c;--paper:#faf9f7;--line:#e3dfd8;--fg:#22323c;--muted:#5f6a68}}
*{{box-sizing:border-box}} html,body{{margin:0;background:var(--paper);color:var(--fg);font-family:"Jost","Segoe UI",sans-serif;font-weight:350;font-size:16.5px;line-height:1.65}}
header{{background:var(--ink);color:#f0efed;padding:44px 20px 40px}}
.w{{max-width:780px;margin:0 auto}}
.k{{font-size:.76rem;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);font-weight:500}}
h1{{font-family:"Fraunces",Georgia,serif;font-weight:300;font-size:clamp(1.8rem,4.4vw,2.7rem);line-height:1.12;margin:.3em 0 0}}
main{{padding:8px 20px 64px}}
h2{{font-family:"Fraunces",Georgia,serif;font-weight:400;font-size:1.45rem;margin:1.8em 0 .4em}}
h3{{font-weight:500;font-size:1.05rem;margin:1.4em 0 .3em}}
p,li{{max-width:70ch}} li{{margin:.25em 0}}
blockquote{{margin:1.2em 0;padding:12px 18px;border-left:3px solid var(--gold);background:#fff;color:var(--muted);border-radius:0 8px 8px 0}}
table{{border-collapse:collapse;width:100%;font-size:.9rem;background:#fff;border:1px solid var(--line);border-radius:8px;overflow:hidden;display:block;overflow-x:auto}}
th,td{{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-weight:500;font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);background:var(--paper)}}
strong{{font-weight:500}} em{{color:var(--muted)}}
</style></head><body>
<header><div class="w"><div class="k">{html.escape(kicker)}</div><h1>{html.escape(title)}</h1></div></header>
<main><div class="w">{body}</div></main>
</body></html>'''
open(out, 'w', encoding='utf-8').write(page)
print(out, len(page))
