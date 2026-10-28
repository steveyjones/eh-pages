"""Add the black-and-white print layout and a Print button to a page.

usage: python3 tools/print_kit.py IN.html OUT.html [--landscape]
Safe to run more than once: an earlier copy of the kit is replaced.
Used by refresh.py on every page it publishes, and on the Claude pages themselves.

In print the page becomes black text on white, with no grey or coloured
backgrounds, larger text, no navy header band, and page breaks kept out of
cards, rows and list items. Anything that used colour to carry meaning
(bars, chart series, legend swatches) is given a black-and-white pattern
instead, the same pattern for the same colour, so legends still match.
"""
import re, sys

START, END = '<!--eh-print-->', '<!--/eh-print-->'

CSS = r'''
.eh-printbtn{position:absolute;top:14px;right:14px;z-index:50;display:inline-flex;align-items:center;gap:7px;
 font:500 14px/1 Jost,"Avenir Next","Segoe UI",Arial,sans-serif;color:#1f3442;background:#fff;border:1px solid #c5cad1;
 border-radius:999px;padding:8px 14px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.12)}
.eh-printbtn:hover{border-color:#1f3442}
.eh-printbtn svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
html.eh-in-portal .eh-printbtn{display:none}
@media print{
 @page{size:A4 %ORIENT%;margin:14mm 12mm}
 html{font-size:125% !important}
 *,*::before,*::after{color:#000 !important;background-color:transparent !important;background-image:none !important;
  box-shadow:none !important;text-shadow:none !important;backdrop-filter:none !important;filter:none !important;
  animation:none !important;transition:none !important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
 html,body{background:#fff !important}
 body{font-size:13pt !important;line-height:1.5 !important}
 /* things that only make sense on screen */
 .eh-printbtn,.eh-tip,.tools,.savebar,.drawer,.scrim,.toast,.edit-only,.ro,.eh-dl,.private{display:none !important}
 /* header band and hero: plain black on white, rule underneath */
 .band,.hero,.eh-head{padding:0 0 10pt !important;margin-bottom:14pt !important;border-bottom:2pt solid #000 !important}
 .band::before,.band::after,.hero::before,.hero::after{display:none !important}
 img.logo{display:none !important}
 .wrap{max-width:none !important}
 .meet,.rail,.stop{border-color:#000 !important}
 .stop::before{background:#fff !important;border:2pt solid #000 !important}
 .rail::before{background:#000 !important;height:1pt !important}
 .lede,.muted,.small,.note,.sub,.ms,.ks,.pd,.ld{color:#000 !important}
 /* lines and boxes black instead of grey */
 .tw,.board,.chart,.card,.tile,.tiles,.strip,.chip,.kpi,.paper,.lib,.agenda>div,.ask>div,.rhythm>div,.cote,.note,
 .eh-card,.eh-tile,.eh-seg,.eh-tablewrap,.keyinfo{border:1pt solid #000 !important}
 .keyinfo,.kpis,.lift{margin-top:0 !important}
 .keyinfo li{border-top:1pt solid #000 !important;padding:8pt 0 !important}
 .keyinfo ol{grid-template-columns:1fr !important}
 .tiles,.strip{gap:0 !important}
 th,td,.grid>div,.dec li,.done li{border-color:#000 !important}
 th{font-weight:700 !important}
 table{border-collapse:collapse !important}
 .board,.tw,.eh-tablewrap{overflow:visible !important}
 .grid,table{min-width:0 !important}
 .strand{border-top:2pt solid #000 !important;border-bottom:1pt solid #000 !important;font-weight:700 !important}
 .pill,.tag,.chip[aria-pressed],.lg{border:1pt solid #000 !important;font-weight:600 !important}
 .kpi::before,.paper .ic,.arr{display:none !important}
 /* status shown by colour on screen gets words in print */
 .c li.done::after,.done.eh-mark::after{content:" (done)"}
 .c li.s::after{content:" (moved)"}
 .c li::before,.c li.t::before,.dia,.slip{background:#000 !important}
 .gap{border:1pt dashed #000 !important}
 .tick{border:1pt solid #000 !important}
 .eh-seg button[aria-pressed="true"]{outline:2pt solid #000 !important;outline-offset:-2pt;font-weight:700 !important;text-decoration:underline}
 .eh-cover-track{border:1pt solid #000 !important}
 .eh-cover-tick{background:#000 !important}
 svg text{fill:#000 !important}
 svg line,svg .domain,svg .tick line{stroke:#000 !important}
 .eh-chart text,.eh-chart svg text{font-size:14px !important}
 /* page breaks */
 h1,h2,h3,.strand,.hd{break-after:avoid;page-break-after:avoid}
 tr,li,.tile,.kpi,.paper,.lib,.card,.chart,.agenda>div,.ask>div,.rhythm>div,.eh-tile,.eh-card,.keyinfo li,.pj,.c,figure{break-inside:avoid;page-break-inside:avoid}
 thead{display:table-header-group}
 section{break-inside:auto}
}
'''

JS = r'''
(function(){
 if(window.ehPrint)return;
 var PAT=[
  {h:'#000',s:'solid'},
  {h:'#fff',s:'outline'},
  {h:'repeating-linear-gradient(45deg,#000 0 2px,#fff 2px 6px)',s:'diag'},
  {h:'radial-gradient(#000 1.2px,#fff 1.4px) 0 0/5px 5px',s:'dots'},
  {h:'repeating-linear-gradient(45deg,#000 0 1.5px,transparent 1.5px 6px),repeating-linear-gradient(-45deg,#000 0 1.5px,#fff 1.5px 6px)',s:'cross'},
  {h:'repeating-linear-gradient(0deg,#000 0 2px,#fff 2px 5px)',s:'horiz'},
  {h:'repeating-linear-gradient(90deg,#000 0 2px,#fff 2px 5px)',s:'vert'},
  {h:'repeating-linear-gradient(-45deg,#000 0 2px,#fff 2px 6px)',s:'anti'}
 ];
 var SEL='.bar,.fb i,.legend i,.mixkey i,.mix span,.bar2 i,.eh-bar-seg,.eh-mini-bar,.eh-cellbar,.eh-swatch,.eh-cover-fill,.dot,[data-print-swatch]';
 var undo=[];
 function plain(c){if(!c)return true;var m=c.match(/rgba?\(([^)]+)\)/);if(!m)return c==='none'||c==='transparent';var p=m[1].split(',').map(parseFloat);
  if(p.length>3&&p[3]===0)return true;return (p[0]>235&&p[1]>235&&p[2]>235);}
 function key(c){var m=c.match(/rgba?\(([^)]+)\)/);return m?m[1].split(',').slice(0,3).map(function(x){return Math.round(parseFloat(x))}).join(','):c}
 function before(){
  undo=[];var map={},n=0;
  function pick(c){var k=key(c);if(!(k in map)){map[k]=n++%PAT.length}return PAT[map[k]]}
  Array.prototype.forEach.call(document.querySelectorAll(SEL),function(el){
   var cs=getComputedStyle(el),c=cs.backgroundColor;if(plain(c))return;
   var p=pick(c);undo.push([el,el.getAttribute('style')]);
   el.style.setProperty('background',p.s==='outline'?'#fff':p.h,'important');
   if(p.s==='outline')el.style.setProperty('box-shadow','inset 0 0 0 1.5px #000','important');
   el.style.setProperty('-webkit-print-color-adjust','exact');el.style.setProperty('print-color-adjust','exact');
  });
  Array.prototype.forEach.call(document.querySelectorAll('svg'),function(svg){
   var shapes=svg.querySelectorAll('rect,path,circle,polygon,ellipse');if(!shapes.length)return;
   var defs=document.createElementNS('http://www.w3.org/2000/svg','defs');defs.setAttribute('data-ehp','1');svg.insertBefore(defs,svg.firstChild);
   var made={};
   Array.prototype.forEach.call(shapes,function(sh){
    var f=getComputedStyle(sh).fill;if(!f||f==='none'||/url\(/.test(f)||plain(f))return;
    var p=pick(f),id='ehp-'+p.s;undo.push([sh,sh.getAttribute('style')]);
    if(p.s==='solid'){sh.style.setProperty('fill','#000','important');return}
    if(p.s==='outline'){sh.style.setProperty('fill','#fff','important');sh.style.setProperty('stroke','#000','important');sh.style.setProperty('stroke-width','1.5','important');return}
    if(!made[id]){made[id]=1;defs.innerHTML+=svgPat(id,p.s)}
    sh.style.setProperty('fill','url(#'+id+')','important');sh.style.setProperty('stroke','#000','important');sh.style.setProperty('stroke-width','1','important');
   });
  });
 }
 function svgPat(id,s){
  var b='<pattern id="'+id+'" patternUnits="userSpaceOnUse" width="6" height="6"><rect width="6" height="6" fill="#fff"/>';
  var d={diag:'<path d="M-1,1 l2,-2 M0,6 l6,-6 M5,7 l2,-2" stroke="#000" stroke-width="1.6"/>',
   anti:'<path d="M-1,5 l2,2 M0,0 l6,6 M5,-1 l2,2" stroke="#000" stroke-width="1.6"/>',
   dots:'<circle cx="3" cy="3" r="1.3" fill="#000"/>',
   cross:'<path d="M0,0 l6,6 M6,0 l-6,6" stroke="#000" stroke-width="1.2"/>',
   horiz:'<path d="M0,3 h6" stroke="#000" stroke-width="1.8"/>',
   vert:'<path d="M3,0 v6" stroke="#000" stroke-width="1.8"/>'}[s]||'';
  return b+d+'</pattern>';
 }
 function after(){
  undo.forEach(function(u){if(u[1]===null)u[0].removeAttribute('style');else u[0].setAttribute('style',u[1])});undo=[];
  Array.prototype.forEach.call(document.querySelectorAll('defs[data-ehp]'),function(d){d.remove()});
 }
 window.addEventListener('beforeprint',before);window.addEventListener('afterprint',after);
 window.ehPrint=function(){window.print()};
 function addBtn(){
  if(document.querySelector('.eh-printbtn')||!document.body)return;
  var b=document.createElement('button');b.type='button';b.className='eh-printbtn';
  b.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M6 14h12v7H6z"/></svg>Print';
  b.title='Print in black and white';b.addEventListener('click',function(){window.ehPrint()});
  document.body.appendChild(b);
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',addBtn);else addBtn();
})();
'''


def kit(landscape=False):
    css = CSS.replace('%ORIENT%', 'landscape' if landscape else 'portrait')
    return f'{START}<style id="eh-print-css">{css}</style><script id="eh-print-js">{JS}</script>{END}'


def add(page, landscape=False):
    page = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', page, flags=re.S)
    block = kit(landscape)
    i = page.rfind('</body>')
    return page[:i] + block + page[i:] if i >= 0 else page + block


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    page = open(src, encoding='utf-8').read()
    open(out, 'w', encoding='utf-8').write(add(page, '--landscape' in sys.argv))
    print(out)
