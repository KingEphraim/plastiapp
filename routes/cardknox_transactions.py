from flask import Blueprint, json, request, session, jsonify
from models.user_settings import UserSettingsManager
from models.apiconnector import send_api_request
from models.databaselog import add_item_to_database,update_item_in_database
from models.handleRecaptcha import verify_recaptcha
from models.invoiceDB import modify_invoice
import uuid

cardknox_transactions_bp = Blueprint('cardknox_transactions', __name__)

with open('config.json') as f:
    config = json.load(f)


@cardknox_transactions_bp.route('/sendtocardknox', methods=['POST'])
def sendtocardknox():
    user_manager = UserSettingsManager(session)
    settings = user_manager.user_settings or {
        "useremail": "",
        "key": config['xKey'],
        "command": "cc:sale",
        "ebtcommand": "ebtonline:fssale",
        "phone": "",
        "lbendpoint": config['lbendpoint'],
        "deviceSerialNumber": "",
        "deviceMake": "",
        "deviceFriendlyName": "",
        "deviceId": "",
        "allowDuplicate": False,
        "allowNonAuthenticated": False,
    }
    headers = {"Content-Type": "application/json"}
    datafromuser = request.get_json()
    transactionData = {
        'xAllowDuplicate': settings.get('allowDuplicate', False),
        'xAllowNonAuthenticated': settings.get('allowNonAuthenticated', False),
        'xBillFirstName': ' '.join(datafromuser.get('name', '').split()[:-1]),
        'xBillLastName': datafromuser.get('name', '').split()[-1] if datafromuser.get('name') else '',
        'xEmail': datafromuser.get('email', ''),
        'xBillPhone': datafromuser.get('phone', ''),
        'xBillStreet': datafromuser.get('address', ''),
        'xBillCity': datafromuser.get('city', ''),
        'xBillState': datafromuser.get('state', ''),
        'xBillZip': datafromuser.get('zip', ''),
        'xInvoice': datafromuser.get('invoice', ''),
        'xDescription': datafromuser.get('comments', ''),
        'xAmount': datafromuser.get('amount', ''),
        'xCardnum': datafromuser.get('card', ''),
        'xExp': datafromuser.get('exp', ''),
        'xCvv': datafromuser.get('cvv', ''),
        'xEMVData': datafromuser.get('encryptedPayload', ''),
        'xSerialNumber': datafromuser.get('xSerialNumber', ''),
        'xMobileTapType': datafromuser.get('xMobileTapType', ''),
    }

    #remove any empty values from transactionData
    transactionData = {k: v for k, v in transactionData.items() if v is not None and v != ''}

    
    lbendpoint = settings.get('lbendpoint') or config['lbendpoint']

    db_invoice_id = datafromuser.get('dbinvoiceid')  
    
        
    
    if (datafromuser['tranzType'] == 'R'):
        recaptcha_response = datafromuser.get('g-recaptcha-response')  # Get the reCAPTCHA token

        # Check if the reCAPTCHA response is missing
        if not recaptcha_response:
            return jsonify({'status': 'fail', 'message': 'reCAPTCHA response is missing.'})

        success, score = verify_recaptcha(recaptcha_response)

        # Check if reCAPTCHA verification was successful and score meets the threshold
        if not success or score < 0.5:  # Assuming you want a minimum score of 0.5
            return jsonify({'status': 'fail', 'message': 'reCAPTCHA verification failed.', 'score': score})


        tockmethod = 'post'
        url = f"https://{lbendpoint}/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': settings.get('command', "cc:sale"),
            'xVendorID': '128717',
            'xIP': request.headers.get('X-Forwarded-For', request.remote_addr),
            # 'xAllowNonAuthenticated': 'true',
        }
        #add the transactionData to the tockdata
        tockdata.update(transactionData)
    elif (datafromuser['tranzType'] == 'void'):
        tockmethod = 'post'
        url = f"https://{lbendpoint}/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xIP': request.headers.get('X-Forwarded-For', request.remote_addr),
            'xCommand': settings.get('voidtype', "cc:voidrefund"),
            'xRefNum': datafromuser.get('refnum', None),
        }
    elif (datafromuser['tranzType'] == 'capture'):
        tockmethod = 'post'
        url = f"https://{lbendpoint}/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xIP': request.headers.get('X-Forwarded-For', request.remote_addr),
            'xCommand': 'cc:capture',
            'xRefNum': datafromuser.get('refnum', None),
        }
    elif (datafromuser['tranzType'] == 'V'):
        tockmethod = 'post'
        url = f"https://{lbendpoint}/verifyjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'x3dsActionCode': datafromuser['x3dsActionCode'],
            'xCavv': datafromuser['xCavv'],
            'xEci': datafromuser['xEci'],
            'xRefNum': datafromuser['xRefNum'],
            'x3dsAuthenticationStatus': datafromuser['x3dsAuthenticationStatus'],
            'x3dsSignatureVerificationStatus': datafromuser['x3dsSignatureVerificationStatus'],
            # 'x3dsError': datafromuser['x3dsError']
        }
    elif (datafromuser['tranzType'] == 'createdevice'):
        tockmethod = 'post'
        url = 'https://device.cardknox.com/v1/device'
        tockdata = {
            'xDeviceSerialNumber': settings['deviceSerialNumber'],
            'xDeviceMake': settings['deviceMake'],
            'xDeviceFriendlyName': settings['deviceFriendlyName'],

        }
        headers['Authorization'] = settings.get('key', config['xKey'])
    elif (datafromuser['tranzType'] == 'cloudIM'):
        tockmethod = 'post'
        url = 'https://device.cardknox.com/v1/Session/initiate'
        tockdata = {
            "xPayload": {
                'xSoftwareName': 'tranzact',
                'xSoftwareVersion': '1.0',
                'xAmount': datafromuser['amount'],
                'xCommand': settings.get('command', "cc:sale"),
                'xExternalRequestId': str(uuid.uuid4()),
                'xInvoice': datafromuser['invoice']
            },
            "xDeviceId":   settings['deviceId']
        }
        headers['Authorization'] = settings.get('key', config['xKey'])

    elif (datafromuser['tranzType'] == 'GP'):
        tockmethod = 'post'
        url = f"https://{lbendpoint}/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': settings.get('command', "cc:sale"),
            'xVendorID': '128717',
            'xIP': request.headers.get('X-Forwarded-For', request.remote_addr),
            'xBillFirstName': str.join(' ', datafromuser['name'].split()[:-1]) if datafromuser['name'] else '',
            'xBillLastName': datafromuser['name'].split()[-1] if datafromuser['name'] else '',
            'xEmail': datafromuser['email'],
            'xBillPhone': datafromuser['phone'],
            'xBillStreet': datafromuser['address'],
            'xBillCity': datafromuser['city'],
            'xBillState': datafromuser['state'],
            'xBillZip': datafromuser['zip'],
            'xInvoice': datafromuser['invoice'],
            'xDescription': datafromuser['comments'],
            'xAmount': datafromuser['amount'],
            'xCardnum': datafromuser['gptoken'],
            'xDigitalWalletType': 'GooglePay',
        }
    elif (datafromuser['tranzType'] == 'AP'):
        tockmethod = 'post'
        url = f"https://{lbendpoint}/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': settings.get('command', "cc:sale"),
            'xVendorID': '128717',
            'xIP': request.headers.get('X-Forwarded-For', request.remote_addr),
            'xBillFirstName': str.join(' ', datafromuser['name'].split()[:-1]) if datafromuser['name'] else '',
            'xBillLastName': datafromuser['name'].split()[-1] if datafromuser['name'] else '',
            'xEmail': datafromuser['email'],
            'xBillPhone': datafromuser['phone'],
            'xBillStreet': datafromuser['address'],
            'xBillCity': datafromuser['city'],
            'xBillState': datafromuser['state'],
            'xBillZip': datafromuser['zip'],
            'xInvoice': datafromuser['invoice'],
            'xDescription': datafromuser['comments'],
            'xAmount': datafromuser['amount'],
            'xCardnum': datafromuser['aptoken'],
            'xDigitalWalletType': 'ApplePay',
        }    
    elif (datafromuser['tranzType'] == 'ebtOnlineInitiate'):
        tockmethod = 'post'
        url = f"https://{lbendpoint}/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': 'ebtonline:initiate',
            'xVendorID': '128717',
            'xIP': request.headers.get('X-Forwarded-For', request.remote_addr),
            'xBillFirstName': str.join(' ', datafromuser['name'].split()[:-1]) if datafromuser['name'] else '',
            'xBillLastName': datafromuser['name'].split()[-1] if datafromuser['name'] else '',
            'xEmail': datafromuser['email'],
            'xBillPhone': datafromuser['phone'],
            'xBillStreet': datafromuser['address'],
            'xBillCity': datafromuser['city'],
            'xBillState': datafromuser['state'],
            'xBillZip': datafromuser['zip'],
            'xInvoice': datafromuser['invoice'],
            'xDescription': datafromuser['comments'],
            'xAmount': datafromuser['amount'],
            'xCardnum': datafromuser['card'],
            'xExp': datafromuser['exp'],
            'xCvv': datafromuser['cvv'],
            'xShipMethod': 'CustomerPickup',
        }
    elif (datafromuser['tranzType'] == 'ebtOnlineComplete'):
        tockmethod = 'post'
        url = f"https://{lbendpoint}/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': settings.get('ebtcommand', "ebtonline:fssale"),
            'xVendorID': '128717',
            'xIP': request.headers.get('X-Forwarded-For', request.remote_addr),
            # 'xAllowNonAuthenticated': 'true',
            'xBillFirstName': str.join(' ', datafromuser['name'].split()[:-1]) if datafromuser['name'] else '',
            'xBillLastName': datafromuser['name'].split()[-1] if datafromuser['name'] else '',
            'xEmail': datafromuser['email'],
            'xBillPhone': datafromuser['phone'],
            'xBillStreet': datafromuser['address'],
            'xBillCity': datafromuser['city'],
            'xBillState': datafromuser['state'],
            'xBillZip': datafromuser['zip'],
            'xInvoice': datafromuser['invoice'],
            'xDescription': datafromuser['comments'],
            'xAmount': datafromuser['amount'],
            'xShipMethod': 'CustomerPickup',
            'xRefNum': datafromuser.get('refnum', None),
        }
    else:
        return {'status': 'fail','message': 'missing tranzType'}

    logdata = {
        "userinfo": UserSettingsManager(session).user_settings,
        "method": tockmethod,
        "url": url,
        "headers": headers,
        "jsonBody": tockdata,
        "dataFromUser":datafromuser
    }
    document_id = add_item_to_database(logdata)
    

    response = send_api_request(
        method=tockmethod,
        url=url,
        headers=headers,
        jsonBody=tockdata
    )
    update_item_in_database(document_id, {'apiResponse':response})
    
    paymentToInvoice = {"payments":[{"paidRefnum": response.get('xRefNum'),"paidAmount":response.get('xAuthAmount')}]} 


    if response.get('xResult') == 'A':
        if db_invoice_id:

            modify_invoice(db_invoice_id,paymentToInvoice)
            
            



    if (datafromuser['tranzType'] == 'cloudIM' and response['xResult'] == 'S'):
        tockmethod = 'get'
        url = f"https://device.cardknox.com/v1/Session/{response['xSessionId']}"
        headers['Authorization'] = settings.get('key', config['xKey'])
        tockdatapoll = {
            'xDeviceSerialNumber': settings['deviceSerialNumber'],
            'xDeviceMake': settings['deviceMake'],
            'xDeviceFriendlyName': settings['deviceFriendlyName'],
        }
        status_check_list = ['COMPLETED', 'ERROR',
                             'TIMEOUT', 'USER_CANCELLED', 'API_CANCELLED']
        pollResponse = {}

        while pollResponse.get('xSessionStatus') not in status_check_list:
            pollResponse = send_api_request(
                method=tockmethod,
                url=url,
                headers=headers,
                jsonBody=tockdatapoll
            )
        tockdata = tockdata['xPayload']
        response = pollResponse
        update_item_in_database(document_id, {'pollResponse':response})

    return jsonify({'ckRequest': tockdata, 'ckResponse': response,'status': 'success','message':'success'})
