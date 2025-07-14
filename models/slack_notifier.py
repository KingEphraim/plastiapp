import json
import requests

def send_slack_webhook(data, md5_hash, ck_signature, signature_verified, url):
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
                "image_url": "https://cardknoxdemo.com/img/moneysola.png",
                "alt_text": "computer thumbnail"
            }
        }
    ]

    if signature_verified is not None:
        blocks[1]["text"]["text"] += f"\n*CloudIM Signature Verification: * `{ 'Success' if signature_verified else 'Failed' }`"

    if ck_signature:
        matchcheck = "Match" if ck_signature.lower() == md5_hash.lower() else "No Match"
        blocks[1]["text"]["text"] += (
            f"\n*ck_signature: * `{ck_signature}`"
            f"\n*Hash: * `{md5_hash}`"
            f"\n*ck_signature - Hash:* `{matchcheck}`"
        )

    payload = json.dumps({
        "text": f"message{data}{ck_signature}",
        "blocks": blocks
    })

    headers = {'Content-Type': 'application/json'}
    return requests.post(url, headers=headers, data=payload)
