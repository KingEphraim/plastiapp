import requests,json
from models.mylogs import add_to_log

with open('config.json') as f:
    config = json.load(f)

def verify_recaptcha(recaptcha_response):
    secret_key = config.get('reCAPTCHASecretKey')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    
    # Prepare the payload
    payload = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    
    # Make the POST request to Google's reCAPTCHA verification endpoint
    response = requests.post(url, data=payload)
    result = response.json()
    add_to_log(f"reCAPTCHA result: {result}")
    
    # Extract the success status and score
    success = result.get('success', False)
    score = result.get('score', None)
    
    # Return both success and score
    return success, score
