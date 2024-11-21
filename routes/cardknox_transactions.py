from flask import Blueprint, json, request, session,jsonify
import requests
from models.user_settings import UserSettingsManager
import mylogs
from models.apiconnector import send_api_request
cardknox_transactions_bp = Blueprint('cardknox_transactions', __name__)

with open('config.json') as f:
    config = json.load(f)


@cardknox_transactions_bp.route('/sendtocardknox', methods=['POST'])
def sendtocardknox():
    mylogs.add_to_log(f'Incoming data: {request.data}')
    user_manager = UserSettingsManager(session)
    settings = user_manager.user_settings or {
        "useremail": "",
        "key": config['xKey'],
        "command": "cc:sale",
        "phone": "",
        "deviceSerialNumber": "",
        "deviceMake": "",
        "deviceFriendlyName": "",
        "deviceId": "",
    }

    headers = {"Content-Type": "application/json"}
    datafromuser = request.get_json()

    if (datafromuser['tranzType'] == 'R'):
        tockmethod = 'post'
        url = "https://x1.cardknox.com/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': settings.get('command', "cc:sale"),
            'xVendorID': '128717',
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
            'xCardnum': datafromuser['card'],
            'xExp': datafromuser['exp'],
            'xCvv': datafromuser['cvv'],
        }
    elif (datafromuser['tranzType'] == 'void'):
        tockmethod = 'post'
        url = "https://x1.cardknox.com/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': 'cc:voidrefund',
            'xRefNum': datafromuser.get('refnum', None),
        }
    elif (datafromuser['tranzType'] == 'capture'):
        tockmethod = 'post'
        url = "https://x1.cardknox.com/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': 'cc:capture',
            'xRefNum': datafromuser.get('refnum', None),
        }
    elif (datafromuser['tranzType'] == 'V'):
        tockmethod = 'post'
        url = 'https://x1.cardknox.com/verifyjson'
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

    elif (datafromuser['tranzType'] == 'polldevicesession'):
        tockmethod = 'get'
        url = f"https://device.cardknox.com/v1/Session/{
            datafromuser['sessionid']}"
        tockdata = {
            'xDeviceSerialNumber': settings['deviceSerialNumber'],
            'xDeviceMake': settings['deviceMake'],
            'xDeviceFriendlyName': settings['deviceFriendlyName'],

        }
        headers['Authorization'] = settings.get('key', config['xKey'])

    elif (datafromuser['tranzType'] == 'sessioninitiate'):
        tockmethod = 'post'
        url = 'https://device.cardknox.com/v1/Session/initiate'
        tockdata = {
            "xPayload": {
                'xSoftwareName': 'tranzact',
                'xSoftwareVersion': '1.0',
                'xAmount': datafromuser['amount'],
                'xCommand': settings.get('command', "cc:sale"),
                'xExternalRequestId': datafromuser['invoice'],
                'xInvoice': datafromuser['invoice']
            },
            "xDeviceId":   settings['deviceId']
        }
        headers['Authorization'] = settings.get('key', config['xKey'])

    elif (datafromuser['tranzType'] == 'GP'):
        tockmethod = 'post'
        url = "https://x1.cardknox.com/gatewayjson"
        tockdata = {
            'xkey': settings.get('key', config['xKey']),
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': settings.get('command', "cc:sale"),
            'xVendorID': '128717',
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
    else:
        return {'message': 'missing tranzType'}
         
    response = send_api_request(
        method=tockmethod,
        url=url,
        headers=headers,
        jsonBody=tockdata
    )

    return jsonify(response)
    
