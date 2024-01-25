from flask import Flask, render_template, request, jsonify
from databaseop import add_item_to_database, update_item_in_database
import requests
import json
import hashlib
import csv
import io
import boto3
import uuid
import os
import systemlogs
with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ewiclist')
def ewiclist():
    return render_template('ewiclist.html')


@app.route('/tranzact')
def tranzact():
    return render_template('tranzact.html')


@app.route('/sendtocardknox', methods=['POST'])
def sendtocardknox():
    systemlogs.configure_logging()
    # print(request.data)
    datafromuser = request.get_json()
    #print(datafromuser)
    
    systemlogs.log_info(datafromuser)

    try:
        inserted_id = add_item_to_database(datafromuser)        
        print(f"Item added to the database with ID: {inserted_id}")
    except Exception as e:
        print(f"Error: {e}")

    if (datafromuser['tranzType'] == 'R'):

        url = "https://x1.cardknox.com/gatewayjson"
        tockdata = {
            "xkey": config['xKey'],
            "xVersion": "5.0.0",
            "xSoftwareName": "tranzact",
            "xSoftwareVersion": "1.0",
            "xCommand": "cc:sale",
            "xVendorID": "128717",
            "xBillFirstName": str.join(' ', datafromuser['name'].split()[:-1]) if datafromuser['name'] else "",
            "xBillLastName": datafromuser['name'].split()[-1] if datafromuser['name'] else "",
            "xEmail": datafromuser['email'],
            "xBillPhone": datafromuser['phone'],
            "xBillStreet": datafromuser['address'],
            "xBillCity": datafromuser['city'],
            "xBillState": datafromuser['state'],
            "xBillZip": datafromuser['zip'],
            "xInvoice": datafromuser['invoice'],
            "xDescription": datafromuser['comments'],
            "xAmount": datafromuser['amount'],
            "xCardnum": datafromuser['card'],
            "xExp": datafromuser['exp'],
            "xCvv": datafromuser['cvv'],
        }
    elif (datafromuser['tranzType'] == 'V'):
        url = "https://x1.cardknox.com/verifyjson"
        tockdata = {
            "xkey": config['xKey'],
            "xVersion": "5.0.0",
            "xSoftwareName": "tranzact",
            "xSoftwareVersion": "1.0",
            "xRefNum": datafromuser['xRefNum'],
            "xCavv": datafromuser['xCavv'],
            "xEci": datafromuser['xEci'],
            "x3dsAuthenticationStatus": datafromuser['x3dsAuthenticationStatus'],
            "x3dsSignatureVerificationStatus": datafromuser['x3dsSignatureVerificationStatus'],
            "x3dsActionCode": datafromuser['x3dsActionCode'],
            "x3dsError": datafromuser['x3dsError']
        }
    else:
        return {'message': 'missing tranzType'}
    
    
   


    
    try:
        print(tockdata)
        json_data = json.dumps(tockdata)
        
    except Exception as e:
        print("Error:", e)

    headers = {"Content-Type": "application/json"} 
    response = requests.post(url, data=json_data, headers=headers)
    if response.status_code == 200:
        print("POST request successful!")
        print("Response:", response.json())
    else:
        print("POST request failed. Status code:", response.status_code)
        print("Response:", response.text)

    item_id = inserted_id
    result = update_item_in_database(item_id, response.json())

    systemlogs.log_info(response.json())
    
    return response.json()


@app.route('/webhookpin', methods=['GET', 'POST'])
def webhookpin():
    if request.method == 'POST':

        trnsdata = request.form.get('data')
        pin = request.form.get('pin')

        lines = trnsdata.split('\n')

        # Remove empty lines
        lines = [line for line in lines if line.strip()]

        # Parse key-value pairs
        pairs = {}
        for i in range(0, len(lines), 2):
            key = lines[i].strip()
            value = lines[i+1].strip().strip("'")
            pairs[key] = value

        sorted_dict = dict(sorted(pairs.items(), key=lambda item: item[0]))
        values_string = ''.join([str(value) for value in sorted_dict.values()])
        print(values_string)
        values_string_pin = values_string + pin
        md5_hash = hashlib.md5(values_string_pin.encode()).hexdigest()
        print(md5_hash)
        # process the form data and return a response
        return jsonify(md5_hash)
    else:
        return render_template('webhookpin.html')


@app.route('/aplpull', methods=['POST', 'GET'])
def process_data():
    apltype = request.args.get('apltype')
    aplstate = request.args.get('state')
    print(aplstate)
    print(apltype)
    url = "https://x1.cardknox.com/reportjson/"
    payload = json.dumps({
        "xkey": config['xKey'],
        "xversion": "5.0.0",
        "xsoftwarename": "PlatiappAPL",
        "xsoftwareversion": "1.0",
        "xCommand": "report:ebtwapl",
        "xewicaplenvironment": "production",
        "xebtwstate": aplstate
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    responseparse = json.loads(response.text)
    for item in responseparse["xReportData"]:
        if item['Type'] == 'Products':
            products_url = item['URL']
        elif item['Type'] == 'Categories':
            categories_url = item['URL']
            break
    if apltype == "prod":
        urlreport = products_url
    elif apltype == "catg":
        urlreport = categories_url

    print(urlreport)
    prodresponse = requests.get(urlreport)
    return prodresponse.text


@app.route('/receipt')
def receipt():
    # Get all the query parameters
    params = request.args
    print(request.args)
    # Create an empty list to store the HTML for each parameter
    fields = []

    # Iterate through the parameters and generate HTML for each one
    for key, value in params.items():
        field = f"<p><strong>{key.replace('_', ' ')}:</strong> {value}</p>"
        fields.append(field)

    # Join all the HTML fields together into a single string
    receipt_html = ''.join(fields)

    # Render the HTML template with the dynamic fields
    return render_template('receipt.html', receipt_html=receipt_html)


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        content_type = request.headers['Content-Type']
        print(content_type)
    except KeyError:
        return "Content-Type header is missing", 400

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
    if ck_signature is None:
        ck_signature = ""
        print(ck_signature)
        url = config['ipn-webhook-hooks.slack']
        payload = json.dumps({
            "text": f"message{data}{ck_signature}",
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "A new transaction has been processed:"}}, {"type": "section", "text": {"type": "mrkdwn", "text": f"*Payload:*\n```{json.dumps(data, indent=4)}```"}, "accessory": {"type": "image", "image_url": "https://cardknoxdemo.com/img/logo.png", "alt_text": "computer thumbnail"}}]
        })

    else:
        if ck_signature.lower() == md5_hash.lower():
            print("The two strings are equal (ignoring case).")
            matchcheck = "Match"
        else:
            print("The two strings are not equal.")
            matchcheck = "No Match"
        url = config['ipn-webhook-hooks.slack']
        payload = json.dumps({
            "text": f"message{data}{ck_signature}",
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "A new transaction has been processed:"}}, {"type": "section", "text": {"type": "mrkdwn", "text": f"*Payload:*\n```{json.dumps(data, indent=4)}```\n*ck_signature: * `{ck_signature}` \n*Hash: * `{md5_hash}`\n*ck_signature - Hash:* `{matchcheck}`"}, "accessory": {"type": "image", "image_url": "https://cardknoxdemo.com/img/logo.png", "alt_text": "computer thumbnail"}}]
        })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response)

    return 'OK'


@app.route('/slackrefnum', methods=['POST'])
def handle_slackrefnum():

    userid = request.form.get('user_id')
    refnum = request.form.get('text')
    print(userid)

    url = f"https://slack.com/api/users.info?user={userid}&pretty=1"
    payload = {}
    headers = {'Authorization': f'Bearer {config["slackauth"]}'}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    responseparse = json.loads(response.text)
    email = responseparse["user"]["profile"]["email"]
    print(email)
    url = f"https://x1.cardknox.com/report/rptpwd/{refnum}?xemail={email}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    print(response.status_code)
    if response.status_code == 200:
        if response.text == "OK":
            return "Your reference number details are on their way to your email. Don't blink or you might miss them!"
        else:
            return f"Oops! Something's not right. Please check the reference number and try again. {response.text}"
    else:
        return f"Oops! Something's not right. Please check the reference number and try again. {response.text}"


@app.route('/bulk')
def handle_bulk():
    return render_template('bulk.html')


@app.route('/bulk_csv', methods=['POST'])
def bulk_csv():
    data = request.form
    print(data)  # Print the data
    url = request.form['url']
    email = request.form['email']
    csv_file = request.files['csvfile']

    if csv_file:
        csvData = csv.reader(io.StringIO(csv_file.read().decode('utf-8-sig')))
        # Process CSV data as needed

        # Get the headers (keys) from the first row of the CSV
        keys = next(csvData)
        # Initialize an empty dictionary
        data_dict = {}
        # Loop through the remaining rows of the CSV
        for row in csvData:
            # Initialize an empty dictionary for each row of data
            row_dict = {}
            # Loop through each column of data and add it to the row dictionary
            for i, value in enumerate(row):
                row_dict[keys[i]] = value
            # Add the row dictionary to the main data dictionary
            data_dict[len(data_dict)+1] = row_dict

        session = boto3.Session(
            aws_access_key_id=os.environ["ACCESS_ID"],
            aws_secret_access_key=os.environ["ACCESS_KEY"],
        )
        sqs = session.resource('sqs', 'us-east-1',)

        # Get the SQS queue by its name
        queue_name = 'bulktransactions.fifo'
        queue = sqs.get_queue_by_name(QueueName=queue_name)

        # Enable content-based deduplication on the queue
        queue.set_attributes(Attributes={'ContentBasedDeduplication': 'true'})
        message_group_id = str(uuid.uuid4())
        for key, value in data_dict.items():
            print(key, json.dumps(value))

            message_body = str(value)
            message_deduplication_id = str(uuid.uuid4())
            print(message_group_id)
            queue.send_message(MessageBody=message_body, MessageGroupId=message_group_id,
                               MessageDeduplicationId=message_deduplication_id)

        print("Messages sent to SQS successfully.")

        # Send each item in the dictionary collection to the SQS queue
        # for item in data_dict:
        #     message_body = str(item)
        #     message_group_id = 'group1'  # Replace with your desired message group ID
        #     queue.send_message(MessageBody=message_body, MessageGroupId=message_group_id)
        # print("Messages sent to SQS successfully.")

        # print(data_dict[2])

        # key = 'xCardNum'
        # for item_key, item_value in data_dict.items():
        #     if key in item_value:
        #         print(item_value[key])

        responsedata = {
            'message': 'Form data and CSV file uploaded successfully', 'groupid': message_group_id}
    return json.dumps(responsedata)


@app.route('/dynamobatchdata')
def your_endpoint():

    # Create a DynamoDB client
    session = boto3.Session(
        aws_access_key_id=os.environ["ACCESS_ID"],
        aws_secret_access_key=os.environ["ACCESS_KEY"],
    )
    dynamodb = session.client('dynamodb', region_name='us-east-1')

    # Define the table name
    try:
        group_id = request.args.get('groupid')

        # Replace 'your_table_name' with the actual name of your DynamoDB table
        table_name = 'transactionresponses'

        # Specify the desired GroupId value

        query_params = {
            'TableName': table_name,
            'KeyConditionExpression': 'GroupId = :group_id',
            'ExpressionAttributeValues': {
                # Assuming the GroupId is a number (change to 'S' if it's a string)
                ':group_id': {'S': group_id}
            }
        }
        # Query the table
        response = dynamodb.query(**query_params)
        # Extract the items from the response

        items = response['Items']
        clean_items = []
        for item in items:
            clean_item = {}
            for key, value in item.items():
                # Extracting the value without the data type
                clean_item[key] = list(value.values())[0]
            clean_items.append(clean_item)

        # Convert the list of dictionaries to a JSON string
        json_string = json.dumps(clean_items)

        # Print the JSON string
        print(json_string)

        return jsonify(json_string)
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/customer')
def justbored():
    return render_template('customer.html')

try:
    with open('invoices.json', 'r') as file:
        invoices = json.load(file)
except FileNotFoundError:

    invoices = []

@app.route('/invoice')
def invoice():
    return render_template('invoice.html')


@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    customer_name = request.form.get('customer_name')
    amount = request.form.get('amount')
    email = request.form.get('customer_email')

    # Create invoice dictionary
    invoice_data = {
        'customer_name': customer_name,
        'amount': amount,
        'email': email,
    }

    # Add invoice to the list
    invoices.append(invoice_data)

    # Save invoices to a JSON file
    save_invoices_to_json()

    return jsonify({'status': 'success'})

@app.route('/delete_invoice/<int:index>', methods=['DELETE'])
def delete_invoice(index):
    if 0 <= index < len(invoices):
        del invoices[index]
        save_invoices_to_json()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid index'})

@app.route('/invoices')
def show_invoices():
    return jsonify({'invoices': invoices})

def save_invoices_to_json():
    with open('invoices.json', 'w') as file:
        json.dump(invoices, file)

if __name__ == '__main__':
    app.run()
    #dev
    # app.run(debug=True)
