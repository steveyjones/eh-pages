# eh-pages

Password-protected Epiphany House pages for the GHL site: budget, trustee report and workplan.

- `loader.js`: the script each GHL page loads. It asks for the password, then fetches and decrypts the page in the browser.
- `*.enc`: page content, AES-GCM encrypted. Nothing here is readable without the password, and the password is not stored in this repository.
- `tools/build_budget.py`: turns the Claude budget dashboard and its CSVs into one standalone page.
- `tools/encrypt.py`: encrypts a page or the spreadsheet (`EH_PAGES_PASSWORD=... python3 tools/encrypt.py in out.enc`).

GHL custom code, one per page (`data-page` is `budget`, `report` or `plan`):

```html
<div class="eh-page" data-page="budget"></div>
<script src="https://steveyjones.github.io/eh-pages/loader.js"></script>
```

The files are refreshed by a scheduled task every Monday morning. GHL never needs to change.
