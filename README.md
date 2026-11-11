# eh-pages

Password-protected Epiphany House pages for the GHL site: budget, trustee report, workplan and policy register.

- `loader.js`: the script each GHL page loads. It asks for the password, then fetches and decrypts the page in the browser.
- `*.enc`: page content, encrypted to the trustees' public key (`pubkey.json`, format v2: ECDH P-256 + AES-GCM). Only the trustee password can rebuild the private key, in the browser. The password is not stored anywhere in this repository or in the scheduled task; older v1 files (password-based AES-GCM) still open.
- `home-state.enc`: the homepage's working data, encrypted with a separate data key (`EH_STATE_KEY`) held by the weekly task. It is not the trustee password and opens nothing else.
- `tools/make_pubkey.py`: run by a person (never the task) when the trustee password is set or changed.
- `tools/build_budget.py`: turns the Claude budget dashboard and its CSVs into one standalone page.
- `tools/build_home.py`, `tools/update_home.py`: build the portal homepage and refresh its figures from the trustee report each week.
- `manifest.json`: last-updated time of each page (no content).
- `tools/encrypt.py`: encrypts a page or the spreadsheet to the public key (`python3 tools/encrypt.py in out.enc`); no password needed.

GHL custom code. The trustee portal is one page with `data-page="home"`; every other page opens inside it. A single paper can also have its own GHL page (`data-page` is `budget`, `report`, `plan` or `policies`):

```html
<div class="eh-page" data-page="home"></div>
<script src="https://steveyjones.github.io/eh-pages/loader.js"></script>
```

The files are refreshed by a scheduled task every Monday morning. GHL never needs to change.
