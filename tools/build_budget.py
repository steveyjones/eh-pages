"""Turn the Claude dashboard page + its CSV datasets into one standalone HTML document.

usage: python3 build_budget.py PAGE.html DATA_DIR SNAPSHOT_TEXT OUT.html
DATA_DIR holds budget.csv assumptions.csv development.csv bookings.csv usage.csv bank.csv
"""
import csv, json, re, sys, os

page_path, data_dir, snapshot, out = sys.argv[1:5]
def rows(name):
    p = os.path.join(data_dir, name + '.csv')
    return list(csv.DictReader(open(p, encoding='utf-8'))) if os.path.exists(p) else []
data = {k: rows(k) for k in ['budget', 'assumptions', 'development', 'bookings', 'usage', 'bank']}
missing = [k for k, v in data.items() if not v and k != 'bank']
if missing: sys.exit('missing data: ' + ', '.join(missing))

page = open(page_path, encoding='utf-8').read()
style = re.search(r'<style>(.*?)</style>', page, re.S).group(1)
body = re.sub(r'<style>.*?</style>', '', page, flags=re.S)
script = re.search(r'<script>(.*)</script>', body, re.S).group(1)
body = re.sub(r'<script>.*</script>', '', body, flags=re.S)
body = re.sub(r'<title>.*?</title>', '', body, flags=re.S)

tokens = '''
#eh-dash{
 --font-anthropic-sans:"Inter",Arial,Helvetica,sans-serif; --font-anthropic-serif:"Source Serif 4",Georgia,"Times New Roman",serif;
 --color-fg:#1f2328; --color-fg-muted:#5f6670; --color-bg:#ffffff; --color-panel:#f7f8fa; --color-border-line:#e3e6ea;
 --color-ok:#1e7a46; --color-warn:#9a6700; --color-bad:#b42318;
 --cds-chart-grid:#eceff3; --cds-chart-axis:#c5cad1; --cds-chart-muted:#c9ced6; --cds-chart-status-critical:#d4483b; --cds-chart-reference:#8a9099;
 --cds-surface-popover:#ffffff; --cds-border:#d9dde3; --cds-shadow-popover:0 4px 16px rgba(0,0,0,.12); --cds-text-secondary:#5f6670;
 --cds-font-size-caption:.8125rem; --cds-font-size-body:.9375rem; --cds-font-size-heading:1.0625rem; --cds-font-size-title:1.5rem; --cds-font-weight-medium:600;
 --cds-gap-xs:.25rem; --cds-gap-sm:.5rem; --cds-gap-md:1rem; --cds-gap-lg:1.5rem; --cds-gap-xl:2.5rem;
 --cds-pad-xs:.375rem; --cds-pad-sm:.625rem; --cds-pad-md:.875rem; --cds-pad-lg:1.25rem; --cds-pad-xl:2rem;
 --cds-radius:10px; --cds-dur-slow:.3s;
 background:var(--color-bg); color:var(--color-fg); padding:24px 16px; box-sizing:border-box;
}
#eh-dash [hidden]{display:none!important}
#eh-dash *,#eh-dash *::before,#eh-dash *::after{box-sizing:border-box}
#eh-dash .dash-skeleton{color:transparent;background:var(--color-border-line);border-radius:4px}
#eh-dash .eh-foot-src{margin-top:24px;font-size:.75rem;color:var(--color-fg-muted)}
'''
shim = '''
(function(){
var RAW=__DATA__;
var calcs={}, cache={}, subs=[], params={residents:1,dev:'off',days:0}, defaults={residents:1,dev:'off',days:0};
function get(id){ if(cache[id]) return cache[id]; if(RAW[id]&&RAW[id].length) return cache[id]=RAW[id]; var c=calcs[id]; if(!c) return RAW[id]||[]; return cache[id]=c.fn.apply(null,c.inputs.map(get)); }
function run(){ subs.forEach(function(fn){ try{fn();}catch(e){console.error(e);} }); }
window.dash={
  calc:function(id,o){calcs[id]=o;}, loader:function(){},
  data:function(id){ var d=get(id); return {status:'ok',data:d,columns:d.length?Object.keys(d[0]):[],meta:[],refreshing:false}; },
  onData:function(fn){subs.push(fn); if(document.readyState!=='loading') fn();},
  params:function(){return Object.assign({},params);},
  setParams:function(p){Object.assign(params,p); run();},
  resetParams:function(){params=Object.assign({},defaults); run();},
  colors:['#2f6fb0','#e08a2c','#3a9b6a','#8a5cc2','#c2457a','#4aa3b8','#9c7a3c','#5b6bbf'],
  refresh:function(){}, setLink:function(){}
};
document.addEventListener('DOMContentLoaded',run);
var t; window.addEventListener('resize',function(){clearTimeout(t);t=setTimeout(run,150);});
})();
'''.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))

html = f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Epiphany House Budget</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Source+Serif+4:opsz,wght@8..60,400&display=swap" rel="stylesheet">
<style>html,body{{margin:0;background:#fff}}{tokens}{style.replace('.eh-page {', '#eh-dash .eh-page {')}</style></head><body>
<div id="eh-dash">{body}
<p class="eh-foot-src">Snapshot of {snapshot}: budget from 12 months of bank statements, bookings from the Checkfront calendars.</p>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>{shim}</script>
<script>{script}</script>
</body></html>'''
open(out, 'w', encoding='utf-8').write(html)
print(out, len(html))
