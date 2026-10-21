"""Encrypt a file for the EH pages loader (AES-GCM, key from PBKDF2-SHA256).

usage: EH_PAGES_PASSWORD=... python3 encrypt.py IN_FILE OUT.enc [--name download-name.xlsx]
The password is never stored in this repository.
"""
import base64, json, os, sys, datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

pw = os.environ.get('EH_PAGES_PASSWORD')
if not pw: sys.exit('set EH_PAGES_PASSWORD')
src, out = sys.argv[1], sys.argv[2]
name = sys.argv[sys.argv.index('--name') + 1] if '--name' in sys.argv else None
it = 250000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(pw.encode())
ct = AESGCM(key).encrypt(iv, open(src, 'rb').read(), None)
b = lambda x: base64.b64encode(x).decode()
doc = {'v': 1, 's': b(salt), 'i': b(iv), 'n': it, 'c': b(ct),
       'u': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}
if name: doc['name'] = name
json.dump(doc, open(out, 'w'))
print(out, os.path.getsize(out))
