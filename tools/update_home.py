"""Refresh the trustee homepage from the current trustee report.

usage: EH_PAGES_PASSWORD=... python3 tools/update_home.py REPORT.html OUT_HOME.html
Reads the previous homepage data out of home.enc (it is embedded there), takes the
figures that live in the report, and rebuilds the page with tools/build_home.py.
Anything it cannot read from the report keeps its previous value; it prints what changed.
"""
import base64, datetime, html, json, os, re, subprocess, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
report_path, out = sys.argv[1], sys.argv[2]
pw = os.environ['EH_PAGES_PASSWORD'].encode()

enc = json.load(open(os.path.join(repo, 'home.enc')))
b = base64.b64decode
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b(enc['s']), iterations=enc['n']).derive(pw)
old = AESGCM(key).decrypt(b(enc['i']), b(enc['c']), None).decode()
data = json.loads(html.unescape(re.search(r'<script type="application/json" id="home-data">(.*?)</script>', old, re.S).group(1)))
before = json.dumps(data, ensure_ascii=False, sort_keys=True)

r = open(report_path, encoding='utf-8').read()
def text(s): return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', s)).split())
notes = []
def section(id_):
    m = re.search(r'<section id="%s">(.*?)</section>' % id_, r, re.S); return m.group(1) if m else ''
def kpi(go_k):
    for k in data.get('kpis', []):
        if k['k'] == go_k: return k

# data-to and meeting
m = re.search(r'<b>Data to</b>\s*\w+ (\d+ \w+ \d{4})', r)
year = None
if m:
    data['data_to'] = m.group(1); year = int(m.group(1)[-4:])
m = re.search(r'<b>Meeting</b>\s*\w+ (\d+) (\w+), ([^,<]+), ([^<]+)</span>', r)
if m and year:
    day, mon, tm, place = int(m.group(1)), m.group(2), m.group(3).strip(), m.group(4).strip()
    try:
        d = datetime.datetime.strptime(f'{day} {mon[:3]} {year}', '%d %b %Y')
        hh = re.match(r'(\d+)(?:[.:](\d+))?\s*(am|pm)', tm)
        h = int(hh.group(1)) % 12 + (12 if hh and hh.group(3) == 'pm' else 0) if hh else 10
        found = {'iso': d.strftime('%Y-%m-%dT') + f'{h:02d}:{int(hh.group(2) or 0) if hh else 0:02d}:00',
                 'label': d.strftime('%A %-d %B'), 'time': tm, 'place': place}
        data['report_meeting'] = found['label']
        # the report's own meeting only becomes "next meeting" if it is still ahead;
        # otherwise the next meeting set on the homepage stays
        if d.date() >= datetime.date.today():
            data['meeting'] = found
    except Exception as ex: notes.append(f'meeting not read: {ex}')

# year-ahead table (section 3): rows in a fixed order
money = section('money')
rows = re.findall(r'<tr><td>(.*?)</td><td class="num">(.*?)</td><td>(.*?)</td></tr>', money)
k = kpi('Year ahead')
if k and len(rows) >= 4 and 'Year ahead' not in data.get('kpi_lock', []):
    base, one, onev = rows[0][1], rows[1][1], rows[3][1]
    k['v'] = text(one)
    k['sub'] = f'With one more let at £660. Three residents alone: {text(base)}. One more let and the events: {text(onev)}.'
else: notes.append('year-ahead kept (locked or table not read)')

# forward book (section 2)
m = re.search(r'aria-label="Listed paid hire by month: ([^"]+)"', r)
if m:
    months = []
    for mo, v in re.findall(r'([A-Za-z]+)\s*£([\d,]+)', m.group(1)):
        months.append([mo[:3], int(v.replace(',', ''))])
    past = len(re.findall(r'class="bar past"', section('forward')))
    data['forward'] = [[mo, v, i < past] for i, (mo, v) in enumerate(months)]
    nxt = months[past:past + 3]
    k = kpi('Hire booked, next 3 months')
    if k and nxt:
        k['v'] = f'£{sum(v for _, v in nxt) / 1000:.1f}k'
        low = [mo for mo, v in months[past:] if v < 1300]
        k['sub'] = ' · '.join(f'{mo} £{v / 1000:.1f}k' for mo, v in nxt) + (f'. {low[0]}–{low[-1]} have the most room to grow.' if len(low) > 1 else '.')
else: notes.append('forward book not read; kept')

# projects (section 5)
proj = section('projects')
pills = re.findall(r'<span class="pill [a-z]+">([^<]+)</span>', proj)
k = kpi('Development projects')
if k and pills:
    c = {p: pills.count(p) for p in dict.fromkeys(pills)}
    k['v'] = str(len(pills))
    k['sub'] = ' · '.join(f'{n} {p.lower()}' for p, n in c.items())

# compliance (section 6)
comp = section('compliance')
k = kpi('Compliance checks')
m = re.search(r'(\d+) repeat checks', comp)
if k and m:
    k['v'] = m.group(1)
    booking = []
    for row in re.findall(r'<tr>(.*?)</tr>', comp, re.S):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
        if len(cells) >= 4 and 'Booking now' in cells[3]: booking.append(re.split(r' and | \(', text(cells[1]))[0])
    k['sub'] = (f'{len(booking)} overdue renewal{"s" if len(booking) != 1 else ""} being booked: ' + ', '.join(x.lower() for x in booking)) if booking else 'Nothing overdue'

# policies (section 7)
m = re.search(r'sign-off on (\d+ \w+) \((\d+)(?: of \d+)?\) and the other half in (\w+) \((\d+)(?: of \d+)?\)', section('policies'))
k = kpi('Policies to sign off')
if k and m:
    k['v'] = f'{m.group(2)}/{int(m.group(2)) + int(m.group(4))}'; k['sub'] = f'{m.group(2)} on {m.group(1)}, the other {m.group(4)} in {m.group(3)}'

# trustee asks (section 8): everything except notes
asks = re.findall(r'<span class="tag">(\w+)</span><br><strong>(.*?)</strong><p>(.*?)</p>', section('asks'), re.S)
dec = []
for tag, head, para in asks:
    if tag.lower() == 'note': continue
    h = text(head).rstrip('.')
    prev = next((d for d in data.get('decisions', []) if d[0] == tag and (d[1].lower() in h.lower() or h.lower() in d[1].lower())), None)
    if prev: dec.append(prev); continue
    first = re.split(r'(?<=[.;])\s', text(para), maxsplit=1)[0].rstrip(';.')
    if len(first) > 90: first = first[:87].rsplit(' ', 1)[0] + '…'
    dec.append([tag, h.split(',')[0], first + ('' if first.endswith('…') else '.')])
if dec: data['decisions'] = dec
else: notes.append('trustee asks not read; kept')

# dates moved since the report was written (e.g. a meeting replaced): applied to text taken from the report
def fixdates(t):
    for a, b2 in data.get('date_fix', {}).items(): t = t.replace(a, b2)
    return t
for k in data.get('kpis', []): k['sub'] = fixdates(k['sub'])
data['decisions'] = [[t, fixdates(h), fixdates(p)] for t, h, p in data.get('decisions', [])]

after = json.dumps(data, ensure_ascii=False, sort_keys=True)
tmp = out + '.json'
json.dump(data, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(repo, 'tools', 'build_home.py'), tmp, os.path.join(repo, 'tools', 'logo.txt'), out], check=True)
print('home data changed' if after != before else 'home data unchanged')
for n in notes: print('note:', n)
