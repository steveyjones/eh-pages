"""Make pubkey.json from the trustee password. Run by a person, only when the password is set or changed.

usage: EH_PAGES_PASSWORD=... python3 tools/make_pubkey.py
The private key is derived from the password in the trustee's browser (PBKDF2-SHA256 -> P-256 scalar);
only the public half is stored here, so the weekly refresh can encrypt pages without knowing the password.
"""
import base64, json, os, sys
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
pw = os.environ.get('EH_PAGES_PASSWORD') or sys.exit('set EH_PAGES_PASSWORD')
salt, it = os.urandom(16), 250000
d = int.from_bytes(PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(pw.encode()), 'big')
if not 0 < d < N: sys.exit('unlucky salt; run again')
pub = ec.derive_private_key(d, ec.SECP256R1()).public_key().public_numbers()
u = lambda n: base64.urlsafe_b64encode(n.to_bytes(32, 'big')).decode().rstrip('=')
json.dump({'v': 2, 's': base64.b64encode(salt).decode(), 'n': it, 'x': u(pub.x), 'y': u(pub.y)},
          open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pubkey.json'), 'w'), indent=1)
print('pubkey.json written')
