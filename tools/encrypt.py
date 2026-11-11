"""Encrypt a file for the EH pages loader. No password needed.

usage: python3 encrypt.py IN_FILE OUT.enc [--name download-name.xlsx]
Format v2: a fresh P-256 key pair per file; ECDH with the trustees' public key (pubkey.json);
HKDF-SHA256 -> AES-256-GCM. Only someone with the trustee password can rebuild the private key
(in the browser, see loader.js), so the weekly task never holds the password.
"""
import base64, json, os, sys, datetime
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pk = json.load(open(os.path.join(repo, 'pubkey.json')))
ub = lambda s: int.from_bytes(base64.urlsafe_b64decode(s + '=' * (-len(s) % 4)), 'big')
trustees = ec.EllipticCurvePublicNumbers(ub(pk['x']), ub(pk['y']), ec.SECP256R1()).public_key()
src, out = sys.argv[1], sys.argv[2]
name = sys.argv[sys.argv.index('--name') + 1] if '--name' in sys.argv else None
eph = ec.generate_private_key(ec.SECP256R1())
salt, iv = os.urandom(16), os.urandom(12)
key = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=b'eh-pages v2').derive(eph.exchange(ec.ECDH(), trustees))
ct = AESGCM(key).encrypt(iv, open(src, 'rb').read(), None)
b = lambda x: base64.b64encode(x).decode()
doc = {'v': 2, 'e': b(eph.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)),
       's': b(salt), 'i': b(iv), 'c': b(ct), 'u': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}
if name: doc['name'] = name
json.dump(doc, open(out, 'w'))
print(out, os.path.getsize(out))
