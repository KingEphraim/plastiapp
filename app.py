from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import json
import hashlib
import csv
import io
import boto3
from botocore.exceptions import ClientError
import uuid
import mylogs
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import OperationFailure
from werkzeug.security import generate_password_hash, check_password_hash
#from databaseop import add_item_to_database, update_item_in_database
with open('config.json') as f:
    config = json.load(f) 
app = Flask(__name__)

app.secret_key = config['secret_key']  # Change this to a secure secret key
client = MongoClient(config['client'],server_api=ServerApi('1'))
db = client[config['db']]  # Change this to your actual database name
users_collection = db["users"]

class UserSettingsManager:
    def __init__(self, session):
        self.user_settings = None
        self.load_user_settings(session)

    def load_user_settings(self, session):
        try:
            username = session.get('username')
            print(username)
            if username is None:
                raise ValueError("Username not found in session.")
            
            self.user_settings = users_collection.find_one({"username": username}, {"_id": 0, "useremail": 1, "key": 1, "phone": 1})
            print(self.user_settings['key'])
        except Exception as e:
            print(f"An error occurred: {e}")
            self.user_settings = None





@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy"), 200

@app.route('/')
def index():
    mylogs.add_to_log(f"Visit to / Method: {request.method} Remote_addr: {request.headers.get('X-Forwarded-For', request.remote_addr)} User-Agent: {request.headers.get('User-Agent')}") 
    if "username" in session:
        username = session.get('username', 'Guest')    
        message = f"You are logged in as {username}! This is your dashboard."    
        user_is_logged_in = session.get('user_is_logged_in', True)
        return render_template('index.html', message=message, user_is_logged_in=user_is_logged_in)
    else:
        return redirect(url_for("login"))   

@app.route("/register", methods=["GET", "POST"])
def register():
    mylogs.add_to_log(f"Visit to /register Method: {request.method} Remote_addr: {request.headers.get('X-Forwarded-For', request.remote_addr)} User-Agent: {request.headers.get('User-Agent')}")

    if request.method == "POST":
        datafromuser = request.get_json()
        if datafromuser:
            try:
                username = datafromuser.get('username')
                useremail = datafromuser.get('email')
                password = datafromuser.get('password')

                if not username or not useremail or not password:
                    return jsonify({'status': 'fail', 'message': 'Missing username, email, or password.'})

                # Check if username already exists
                if users_collection.find_one({"username": username}):
                    return jsonify({'status': 'fail', 'message': 'Username already exists.'})

                # Hash the password using the 'scrypt' method
                hashed_password = generate_password_hash(password, method="scrypt")

                # Insert the user into the database
                users_collection.insert_one({"username": username, "useremail": useremail, "password": hashed_password})

                return jsonify({'status': 'success', 'redirect': url_for('login')})

            except OperationFailure as e:
                # Handle MongoDB OperationFailure
                error_message = str(e)
                return jsonify({'status': 'error', 'message': error_message})

        else:
            return jsonify({'status': 'fail', 'message': 'Invalid JSON data.'})

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        datafromuser = request.get_json()
        if datafromuser:
            try:
                username = datafromuser.get('username')
                password = datafromuser.get('password')

                if not username or not password:
                    return jsonify({'status': 'fail', 'message': 'Missing username or password.'})

                user = users_collection.find_one({"username": username})

                if not user:
                    return jsonify({'status': 'fail', 'message': 'User not found.'})

                if not check_password_hash(user['password'], password):
                    return jsonify({'status': 'fail', 'message': 'Incorrect password.'})

                session['username'] = username
                session['user_is_logged_in'] = True

                return jsonify({'status': 'success', 'message': 'Login successful.'})

            except Exception as e:
                error_message = str(e)
                return jsonify({'status': 'error', 'message': error_message})

        else:
            return jsonify({'status': 'fail', 'message': 'Invalid JSON data.'})

    return render_template("login.html")

@app.route('/save_settings', methods=['POST'])
def save_settings():
    mylogs.add_to_log(f"Visit to /save_settings Method: {request.method} Remote_addr: {request.headers.get('X-Forwarded-For', request.remote_addr)} User-Agent: {request.headers.get('User-Agent')}")

    if "username" not in session:
        return jsonify({'status': 'fail', 'message': 'User not logged in.'}), 403

    username = session.get('username')

    if request.method == "POST":
        settings_data = request.get_json()
        if settings_data:
            try:
                # Retrieve settings from the JSON data
                new_email = settings_data.get('email')
                new_key = settings_data.get('key')
                new_phone = settings_data.get('phone')
                new_threeds = settings_data.get('threeds')

                # Ensure required fields are provided
                if not new_email or not new_key or not new_phone:
                    return jsonify({'status': 'fail', 'message': 'Missing email or key or phone.'})

                # Update the user's settings in the database
                users_collection.update_one(
                    {"username": username},
                    {"$set": {"useremail": new_email, "key": new_key,"phone": new_phone,"threeds": new_threeds}}
                )

                return jsonify({'status': 'success', 'message': 'Settings updated successfully!'})

            except OperationFailure as e:
                # Handle MongoDB OperationFailure
                error_message = str(e)
                return jsonify({'status': 'error', 'message': error_message})
        
        else:
            return jsonify({'status': 'fail', 'message': 'Invalid JSON data.'})

    return jsonify({'status': 'fail', 'message': 'Invalid request method.'})


@app.route('/load_settings', methods=['GET'])
def load_settings():
    mylogs.add_to_log(f"Visit to /load_settings Method: {request.method} Remote_addr: {request.headers.get('X-Forwarded-For', request.remote_addr)} User-Agent: {request.headers.get('User-Agent')}")

    if "username" not in session:
        return jsonify({'status': 'fail', 'message': 'User not logged in.'}), 403

    username = session.get('username')

    if request.method == "GET":
        try:
            # Retrieve user settings from the database
            user_settings = users_collection.find_one({"username": username}, {"_id": 0, "useremail": 1, "key": 1, "phone": 1, "threeds": 1})
            
            if user_settings:
                return jsonify({'status': 'success', 'settings': user_settings})
            else:
                return jsonify({'status': 'fail', 'message': 'Settings not found.'})

        except OperationFailure as e:
            # Handle MongoDB OperationFailure
            error_message = str(e)
            return jsonify({'status': 'error', 'message': error_message})

    return jsonify({'status': 'fail', 'message': 'Invalid request method.'})


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return f"Welcome, {session['username']}! This is your dashboard."
    else:
        return redirect(url_for("login"))

# Logout route
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route('/settings')
def settings():
    if "username" in session:
        username = session.get('username', 'Guest')    
        message = f"You are logged in as {username}! This is your settings."    
        user_is_logged_in = session.get('user_is_logged_in', True)
        return render_template('settings.html', message=message, user_is_logged_in=user_is_logged_in)
    else:
        return redirect(url_for("login"))  

@app.route('/ewiclist')
def ewiclist():
    if "username" in session: 
        user_is_logged_in = session.get('user_is_logged_in', True)        
        return render_template('ewiclist.html', user_is_logged_in=user_is_logged_in)
    else:
        return render_template('ewiclist.html')  


@app.route('/tranzact')
def tranzact():
    if "username" in session: 
        user_is_logged_in = session.get('user_is_logged_in', True)        
        return render_template('tranzact.html', user_is_logged_in=user_is_logged_in)
    else:
        return render_template('tranzact.html')     
    


@app.route('/sendtocardknox', methods=['POST'])
def sendtocardknox(): 
    mylogs.add_to_log(f'Incoming data: {request.data}')      
    user_manager = UserSettingsManager(session)
    
    settings = user_manager.user_settings or {
        "useremail": "",
        "key": config['xKey'],
        "phone": "",
        }
    
    

    datafromuser = request.get_json()     

    if (datafromuser['tranzType'] == 'R'):

        url = "https://x1.cardknox.com/gatewayjson"
        tockdata = {
            'xkey': settings['key'],
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': 'cc:sale',
            'xVendorID': '128717',
            #'xAllowNonAuthenticated': 'true',
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
    elif (datafromuser['tranzType'] == 'V'):
        url = 'https://x1.cardknox.com/verifyjson'
        tockdata = {
            'xkey': settings['key'],
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'x3dsActionCode': datafromuser['x3dsActionCode'],
            'xCavv': datafromuser['xCavv'],
            'xEci': datafromuser['xEci'],
            'xRefNum': datafromuser['xRefNum'],
            'x3dsAuthenticationStatus': datafromuser['x3dsAuthenticationStatus'],
            'x3dsSignatureVerificationStatus': datafromuser['x3dsSignatureVerificationStatus'],            
            #'x3dsError': datafromuser['x3dsError']
        }
    elif(datafromuser['tranzType'] == 'GP'):

        url = "https://x1.cardknox.com/gatewayjson"
        tockdata = {
            'xkey': settings['key'],
            'xVersion': '5.0.0',
            'xSoftwareName': 'tranzact',
            'xSoftwareVersion': '1.0',
            'xCommand': 'cc:sale',
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
    
    
   


    
    try:
        json_data = json.dumps(tockdata)
        
    except Exception as e:
        print("Error:", e)

    headers = {"Content-Type": "application/json"} 
    mylogs.add_to_log(f'Data sent to ck: {json_data}')  
    response = requests.post(url, data=json_data, headers=headers)
    if response.status_code == 200:
        ck_response = response.json()
        mylogs.add_to_log(f'Ck 200 response: {ck_response}')  
        
    else:
        mylogs.add_to_log(f'Ck fail response: statuscode - {response.status_code} - error{response.text}')
        

    # item_id = inserted_id
    # result = update_item_in_database(item_id, response.json())

    
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
    user_manager = UserSettingsManager(session)
    
    settings = user_manager.user_settings or {
        "useremail": "",
        "key": config['xKey'],
        "phone": "",
    }
    
    apltype = request.args.get('apltype')
    aplstate = request.args.get('state')
    aplenvironment = request.args.get('environment')
    
    print(aplstate)
    print(apltype)
    
    url = "https://x1.cardknox.com/reportjson/"
    payload = json.dumps({
        'xkey': settings['key'],
        "xversion": "5.0.0",
        "xsoftwarename": "PlatiappAPL",
        "xsoftwareversion": "1.0",
        "xCommand": "report:ebtwapl",
        "xewicaplenvironment": aplenvironment,
        "xebtwstate": aplstate
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        
        responseparse = response.json()
        
        # Check for specific error response
        if responseparse.get("xResult") == "E" and responseparse.get("xStatus") == "Error":
            error_message = responseparse.get("xError", "Unknown error occurred.")
            ref_num = responseparse.get("xRefNum", "N/A")
            return f"Error: {error_message} (Reference Number: {ref_num})", 400
        
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}", 500
    except ValueError as e:
        return f"Error parsing JSON: {str(e)}", 500

    products_url = categories_url = None
    for item in responseparse.get("xReportData", []):
        if item.get('Type') == 'Products':
            products_url = item.get('URL')
        elif item.get('Type') == 'Categories':
            categories_url = item.get('URL')
            break
    
    urlreport = None
    if apltype == "prod":
        urlreport = products_url
    elif apltype == "catg":
        urlreport = categories_url
    
    if not urlreport:
        return "Error: No report URL found.", 404
    
    try:
        prodresponse = requests.get(urlreport)
        prodresponse.raise_for_status()
        return prodresponse.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching report: {str(e)}", 500


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
        mylogs.add_to_log(f'content_type: {content_type}')
    except KeyError:
        return "Content-Type header is missing", 400
    try:
        cksig = request.headers['ck-signature']
        mylogs.add_to_log(f'ck-sig: {cksig}')
    except KeyError:
        mylogs.add_to_log(f'missing ck signature')

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
def bulk():   

    if "username" in session: 
        user_is_logged_in = session.get('user_is_logged_in', True)        
        return render_template('bulk.html', user_is_logged_in=user_is_logged_in)
    else:
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
            # Check if the row contains any non-empty values
            if any(row):
                # Initialize an empty dictionary for each row of data
                row_dict = {}
                # Loop through each column of data and add it to the row dictionary
                for i, value in enumerate(row):
                    row_dict[keys[i]] = value
                # Add the row dictionary to the main data dictionary
                data_dict[len(data_dict)+1] = row_dict

        try:
            session = boto3.Session(
                aws_access_key_id=config['aws_access_key_id'],
                aws_secret_access_key=config['aws_secret_access_key'],               
                region_name='us-east-1',  # Update with the correct region
            )
            
            sqs = session.resource('sqs') 
            queue_name = 'bulktransactions.fifo'
            queue = sqs.get_queue_by_name(QueueName=queue_name)
            queue.set_attributes(Attributes={'ContentBasedDeduplication': 'true'})
            message_group_id = str(uuid.uuid4())
            mylogs.add_to_log(f'MGI: {message_group_id}')
            for key, value in data_dict.items():
                message_body = str(value)
                message_deduplication_id = str(uuid.uuid4())
                mylogs.add_to_log(f'Transaction # {key} Data: {value} Message_deduplication_id: {message_deduplication_id}')
                result = queue.send_message(MessageBody=message_body, MessageGroupId=message_group_id, MessageDeduplicationId=message_deduplication_id)  
                mylogs.add_to_log(f'Send_message result: {result}')
            responsedata = {'message': 'Form data and CSV file uploaded successfully', 'groupid': message_group_id}
            return json.dumps(responsedata)
        except ClientError as e:
            mylogs.add_to_log(e)
            if e.response['Error']['Code'] == 'InvalidClientTokenId':
                print("Error: Invalid AWS credentials or permissions.")
            else:
                print(f"An error occurred: {e}")  

    return json.dumps({'error':'e'})


@app.route('/dynamobatchdata')
def dynamobatchdata():
    try:
        # Get the 'groupid' parameter from the request
        group_id = request.args.get('groupid')

        # Check if 'groupid' parameter is missing
        if not group_id:
            return jsonify({'error': 'groupid parameter is missing'}), 400

        # Create a DynamoDB client
        session = boto3.Session(
            aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key=config['aws_secret_access_key'],
        )
        dynamodb = session.client('dynamodb', region_name='us-east-1')

        # Define the table name
        table_name = 'transactionresponses'

        # Initialize an empty list to hold all items
        all_items = []

        # Define the initial query parameters for the first page
        query_params = {
            'TableName': table_name,
            'KeyConditionExpression': 'GroupId = :group_id',
            'ExpressionAttributeValues': {
                ':group_id': {'S': group_id}
            }
        }

        # Loop to retrieve all pages of data
        while True:
            # Query the table for the current page
            response = dynamodb.query(**query_params)

            # Extract the items from the response
            items = response.get('Items', [])

            # Append the items from the current page to the list of all items
            all_items.extend(items)

            # Check if there are more pages to retrieve
            if 'LastEvaluatedKey' in response:
                # Set the exclusive start key for the next page
                query_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
            else:
                # If no more pages, break out of the loop
                break

        # Clean up the items
        clean_items = []
        for item in all_items:
            clean_item = {}
            for key, value in item.items():
                # Extracting the value without the data type
                clean_item[key] = list(value.values())[0]
            clean_items.append(clean_item)

        # Return the clean items as JSON response
        return jsonify(clean_items)

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
