from flask import Blueprint,request,json
from models.mylogs import add_to_log
import hashlib
import requests 
import base64
import re
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization


with open('config.json') as f:
    config = json.load(f) 

webhook_bp = Blueprint('webhook', __name__)

SOLA_PUBLIC_KEYS = {}

def parse_signature_header(header_value):
    # Safely parse key=value pairs from the header
    try:
        parts = re.split(r',\s*', header_value)
        parsed = {}
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                parsed[key.strip()] = value.strip()
        return parsed
    except Exception as e:
        add_to_log(f"Failed to parse signature header: {e}")
        return {}

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    signature_verified = False

    if 'X-Cim-Signature' in request.headers:
        try:
            signature_header = request.headers['X-Cim-Signature']
            params = parse_signature_header(signature_header)

            key_id = params.get('keyId')
            algorithm = params.get('algorithm')
            signature = params.get('signature')

            if not key_id or not algorithm or not signature:
                add_to_log(f"Missing one or more required fields in X-Cim-Signature header.")
                

            add_to_log(f'X-Cim-Signature received: keyId={key_id}, algorithm={algorithm}, signature={signature}')

            # Support only ES256 for now
            if algorithm != 'ES256':
                add_to_log(f"Unsupported algorithm: {algorithm}")
                

            # Download and cache public key if not already available
            if key_id not in SOLA_PUBLIC_KEYS:
                public_key_url = f'https://cdn.cardknox.com/.well-known/device/{key_id}.pem'
                response = requests.get(public_key_url, timeout=10)
                if response.status_code == 200:
                    SOLA_PUBLIC_KEYS[key_id] = serialization.load_pem_public_key(response.content)
                    add_to_log(f'Public key for {key_id} downloaded and cached.')
                else:
                    add_to_log(f'Failed to download public key for keyId: {key_id}')                    

            # Decode Base64-URL-safe signature
            signature += '=' * ((4 - len(signature) % 4) % 4)  # Correct padding
            signature_bytes = base64.urlsafe_b64decode(signature)

            # Verify signature using the cached public key
            public_key = SOLA_PUBLIC_KEYS[key_id]
            public_key.verify(
                signature_bytes,
                request.data,
                ec.ECDSA(hashes.SHA256())
            )
            add_to_log(f'Signature verified successfully for keyId: {key_id}')
            signature_verified = True

        except InvalidSignature:
            add_to_log(f'Invalid signature for keyId: {key_id}')
            
        except Exception as e:
            add_to_log(f'Exception while verifying signature: {str(e)}')
            

     
    try:
        content_type = request.headers['Content-Type']
        add_to_log(f'content_type: {content_type}')
    except KeyError:
        return "Content-Type header is missing", 400
    try:
        cksig = request.headers['ck-signature']
        add_to_log(f'ck-sig: {cksig}')
    except KeyError:
        add_to_log(f'missing ck signature')

    ck_signature = request.headers.get('ck-signature')
    if content_type == 'application/json':
        data = request.get_json()
    elif content_type.startswith('multipart/form-data'):
        data = request.form.to_dict()
    elif content_type == 'application/x-www-form-urlencoded':
        data = request.form.to_dict()
    elif content_type.startswith('application/x-www-form-urlencoded'):
        data = request.form.to_dict()
    elif content_type.startswith('text/plain'):
        datatext = request.data.decode('utf-8')
        try:
            data = json.loads(datatext)
        except json.JSONDecodeError as e:
            data = {"text/plain": request.data.decode('utf-8')}
    else:
        # Unsupported content type
        return f"Unsupported content type Content Type: {request.headers['Content-Type']}", 400

    pin = config['webhookpin']
    sorted_dict = dict(sorted(data.items(), key=lambda item: item[0]))
    values_string = ''.join([str(value) for value in sorted_dict.values()])
    values_string_pin = values_string + pin
    md5_hash = hashlib.md5(values_string_pin.encode()).hexdigest()
    print(md5_hash)

    url = config['ipn-webhook-hooks.slack']
    ck_signature = ck_signature or ""
    print(ck_signature)

    # Base message block
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "A new transaction has been processed:"}
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Payload:*\n```{json.dumps(data, indent=4)}```"
            },
            "accessory": {
                "type": "image",
                "image_url": "https://cardknoxdemo.com/img/logo.png",
                "alt_text": "computer thumbnail"
            }
        }
    ]
    # Add signature verification status on a new line in bold
    if 'X-Cim-Signature' in request.headers:
        if signature_verified:
            blocks[1]["text"]["text"] += "\n*CloudIM Signature Verification: * `Success`"
        else:
            blocks[1]["text"]["text"] += "\n*CloudIM Signature Verification: * `Failed`"
    
    # Add hash comparison if signature is provided
    if ck_signature:
        if ck_signature.lower() == md5_hash.lower():
            print("The two strings are equal (ignoring case).")
            matchcheck = "Match"
        else:
            print("The two strings are not equal.")
            matchcheck = "No Match"

        blocks[1]["text"]["text"] += f"\n*ck_signature: * `{ck_signature}`\n*Hash: * `{md5_hash}`\n*ck_signature - Hash:* `{matchcheck}`"

    payload = json.dumps({
        "text": f"message{data}{ck_signature}",
        "blocks": blocks
    })

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response)

    return 'OK'