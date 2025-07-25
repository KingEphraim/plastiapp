from flask import Flask, render_template, request, jsonify, session,send_from_directory,current_app
import requests
import json
import hashlib
import csv
import io
import boto3
from botocore.exceptions import ClientError
import uuid
from models.mylogs import add_to_log
from models.user_settings import UserSettingsManager

from routes.main import main_bp
from routes.auth import auth_bp
from routes.settings import settings_bp
from routes.cardknox_transactions import cardknox_transactions_bp
from routes.contact import contact__bp
from routes.invoice import invoice__bp
from routes.customer import customer__bp
from routes.ebtresponse import ebtresponse__bp
from routes.tranzact.main import tranzact_bp
from routes.webhook import webhook_bp

with open('config.json') as f:
    config = json.load(f) 
app = Flask(__name__)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(cardknox_transactions_bp)
app.register_blueprint(contact__bp)
app.register_blueprint(invoice__bp)
app.register_blueprint(customer__bp)
app.register_blueprint(ebtresponse__bp)
app.register_blueprint(tranzact_bp)
app.register_blueprint(webhook_bp)


app.secret_key = config['secret_key']  # Change this to a secure secret key



@app.route('/.well-known/<filename>')
def serve_well_known(filename):
    # Serve the file from the static/.well-known folder directly
    return send_from_directory(current_app.static_folder + '/.well-known', filename)

@app.route('/ewiclist')
def ewiclist():
    if "username" in session: 
        user_is_logged_in = session.get('user_is_logged_in', True)        
        return render_template('ewiclist.html', user_is_logged_in=user_is_logged_in)
    else:
        return render_template('ewiclist.html')  







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
        "deviceSerialNumber": "",
        "deviceMake": "",
        "deviceFriendlyName": "",
        "deviceId": "",
    }
    
    apltype = request.args.get('apltype')
    aplstate = request.args.get('state')
    aplenvironment = request.args.get('environment')
    
    print(aplstate)
    print(apltype)
    
    url = "https://x1.cardknox.com/reportjson/"
    payload = json.dumps({
        'xkey': settings.get('key', config['xKey']),
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

# Challenge POST with text from CloudIM that returns it with 200
@app.route('/challenge', methods=['POST'])
def challenge():
    data = request.get_data(as_text=True)
    add_to_log(f'Challenge data: {data}')
    if data:
        add_to_log(f'Challenge data: {data}')
        return data, 200
    else:
        add_to_log('Challenge data is empty')
        return "No data received", 400
    
    





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
            add_to_log(f'MGI: {message_group_id}')
            for key, value in data_dict.items():
                message_body = str(value)
                message_deduplication_id = str(uuid.uuid4())
                add_to_log(f'Transaction # {key} Data: {value} Message_deduplication_id: {message_deduplication_id}')
                result = queue.send_message(MessageBody=message_body, MessageGroupId=message_group_id, MessageDeduplicationId=message_deduplication_id)  
                add_to_log(f'Send_message result: {result}')
            responsedata = {'message': 'Form data and CSV file uploaded successfully', 'groupid': message_group_id}
            return json.dumps(responsedata)
        except ClientError as e:
            add_to_log(e)
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

if __name__ == '__main__':
    app.run()
    #dev
    # app.run(debug=True)
