#send_slack_utils handles sending messages to Slack channels.
import json,requests
with open('config.json') as f:
    config = json.load(f)

def send_slack_webhook(data, md5_hash, ck_signature, signature_verified, slack_url):
    """
    Sends a message to a Slack channel using the provided  URL.
    
    Args:
        data (dict): The data to be sent to Slack.
        slack_url (str): The Slack URL.
    Raises:
        ValueError: If the request to Slack fails or if the data cannot be encoded to JSON
    Returns:
        response: The response from the Slack API.
    """
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
                "image_url": config['slack_image_url'],
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
    response = requests.post(slack_url, headers=headers, data=payload)

    if response.status_code != 200:
        raise ValueError(f"Request to Slack failed with status code {response.status_code}: {response.text}")

    return response

  
    

