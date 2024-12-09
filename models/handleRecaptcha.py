import requests,json

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
    
    # Check if the verification was successful
    return result.get('success', False)