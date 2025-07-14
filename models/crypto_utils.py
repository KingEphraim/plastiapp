import base64
import re
import requests
from models.mylogs import add_to_log
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

# Public key cache
SOLA_PUBLIC_KEYS = {}

def parse_signature_header(header_value):
    try:
        parts = re.split(r',\s*', header_value)
        return {k.strip(): v.strip() for k, v in (part.split('=') for part in parts if '=' in part)}
    except Exception as e:
        add_to_log(f"Failed to parse signature header: {e}")
        return {}

def verify_cloudim_signature(request):
    try:
        signature_header = request.headers.get('X-Cim-Signature', '')
        params = parse_signature_header(signature_header)
        key_id = params.get('keyId')
        algorithm = params.get('algorithm')
        signature = params.get('signature')

        if not key_id or not algorithm or not signature:
            add_to_log("Missing one or more required fields in X-Cim-Signature header.")
            return False

        add_to_log(f'X-Cim-Signature received: keyId={key_id}, algorithm={algorithm}, signature={signature}')

        if algorithm != 'ES256':
            add_to_log(f"Unsupported algorithm: {algorithm}")
            return False

        # Download and cache public key if not cached
        if key_id not in SOLA_PUBLIC_KEYS:
            public_key_url = f'https://cdn.cardknox.com/.well-known/device/{key_id}.pem'
            response = requests.get(public_key_url, timeout=10)
            if response.status_code == 200:
                SOLA_PUBLIC_KEYS[key_id] = serialization.load_pem_public_key(response.content)
                add_to_log(f'Public key for {key_id} downloaded and cached.')
            else:
                add_to_log(f'Failed to download public key for keyId: {key_id}')
                return False

        # Decode base64 URL-safe signature
        signature += '=' * ((4 - len(signature) % 4) % 4)
        signature_bytes = base64.urlsafe_b64decode(signature)

        public_key = SOLA_PUBLIC_KEYS[key_id]
        public_key.verify(signature_bytes, request.data, ec.ECDSA(hashes.SHA256()))
        add_to_log(f'Signature verified successfully for keyId: {key_id}')
        return True

    except InvalidSignature:
        add_to_log(f'Invalid signature for keyId: {key_id}')
    except Exception as e:
        add_to_log(f'Exception while verifying signature: {str(e)}')
    return False
