from flask import Blueprint, request, json
from models.mylogs import add_to_log
import hashlib
import requests
import re
from models.crypto_utils import verify_cloudim_signature
from models.slack_notifier import send_slack_webhook

with open('config.json') as f:
    config = json.load(f)

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    signature_verified = None  # None = not checked, True/False = result

    if 'X-Cim-Signature' in request.headers:
        signature_verified = verify_cloudim_signature(request)

    try:
        content_type = request.headers['Content-Type']
        add_to_log(f'content_type: {content_type}')
    except KeyError:
        return "Content-Type header is missing", 400

    ck_signature = request.headers.get('ck-signature')
    if ck_signature:
        add_to_log(f'ck-sig: {ck_signature}')
    else:
        add_to_log(f'missing ck signature')

    # Parse request data based on content type
    if content_type == 'application/json':
        data = request.get_json()
    elif content_type.startswith(('multipart/form-data', 'application/x-www-form-urlencoded')):
        data = request.form.to_dict()
    elif content_type.startswith('text/plain'):
        datatext = request.data.decode('utf-8')
        try:
            data = json.loads(datatext)
        except json.JSONDecodeError:
            data = {"text/plain": datatext}
    else:
        return f"Unsupported content type Content Type: {content_type}", 400

    # Create hash
    pin = config['webhookpin']
    sorted_dict = dict(sorted(data.items(), key=lambda item: item[0]))
    values_string = ''.join([str(value) for value in sorted_dict.values()])
    md5_hash = hashlib.md5((values_string + pin).encode()).hexdigest()

    slack_url = config['ipn-webhook-hooks.slack']
    send_slack_webhook(data, md5_hash, ck_signature, signature_verified, slack_url)

    return 'OK'
