"""Rebuild the encrypted pages from a work folder.

usage: EH_PAGES_PASSWORD=... python3 tools/refresh.py WORK_DIR
WORK_DIR holds:
  budget-page.html   the dashboard page (files/index.html, field "text")
  data/*.csv         budget assumptions development bookings usage bank
  report.html        the trustee report artifact's index.html
  plan.html          the workplan artifact's index.html
  budget.xlsx        optional: a new spreadsheet to replace the download
Any piece that is missing is left as it is in the repository.
"""
import os, subprocess, sys, datetime
work = sys.argv[1]
repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tools = os.path.join(repo, 'tools')
py = sys.executable
def enc(src, out, *extra):
    subprocess.run([py, os.path.join(tools, 'encrypt.py'), src, os.path.join(repo, out), *extra], check=True)
done = []
page, data = os.path.join(work, 'budget-page.html'), os.path.join(work, 'data')
if os.path.exists(page) and os.path.isdir(data):
    snap = datetime.date.today().strftime('%-d %B %Y')
    out = os.path.join(work, 'budget-built.html')
    subprocess.run([py, os.path.join(tools, 'build_budget.py'), page, data, snap, out], check=True)
    enc(out, 'budget.enc'); done.append('budget')
for name in ('report', 'plan'):
    p = os.path.join(work, name + '.html')
    if os.path.exists(p) and os.path.getsize(p) > 1000:
        enc(p, name + '.enc'); done.append(name)
x = os.path.join(work, 'budget.xlsx')
if os.path.exists(x):
    nm = os.environ.get('EH_XLSX_NAME', 'EH budget.xlsx')
    enc(x, 'budget-xlsx.enc', '--name', nm); done.append('spreadsheet')
print('refreshed:', ', '.join(done) or 'nothing')
