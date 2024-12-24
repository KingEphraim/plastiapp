from flask import Blueprint,request,jsonify
from models.invoiceDB import create_invoice
from datetime import datetime
import re
from models.sendEmail import send_email
from urllib.parse import quote_plus

invoice__bp = Blueprint('invoice', __name__)

@invoice__bp.route('/invoice', methods=['POST'])
def invoice():
    return

from flask import jsonify, request

@invoice__bp.route('/emailInvoice', methods=['POST'])
def emailInvoice():
    try:
        data = request.get_json()
        
        todaysDate = datetime.now().strftime('%Y-%m-%d')

        amount = data.get('amount')
        name = data.get('name')
        email = data.get('email')
        address = data.get('address')
        city = data.get('city')
        state = data.get('state')
        zip = data.get('zip')
        comments = data.get('comments')
        invoice = data.get('invoice')
        phone = data.get('phone')     

        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        new_invoice = {
        "customer_name": name,
        "email": email,
        "address": address,
        "city": city,
        "state": state,
        "zip": zip,
        "phone": phone,
        "items": [
            {"name": comments, "price": amount, "quantity": 1}
        ],
        "total": amount,
        "status": "Unpaid",
        "created_at": todaysDate,
        "invoice": invoice
        }

        
        invoice_id = create_invoice(new_invoice)
        print(f"Invoice created with ID: {invoice_id}")

        
        if email and re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
            print(f"Valid email: {email}")

                # Determine the correct origin based on the host
            is_local = request.host.startswith('127.0.0.1') or request.host.startswith('localhost')
            base_url = 'http://127.0.0.1:5000' if is_local else 'https://app.cardknox.link'



            
            encoded_name = quote_plus(name)
            encoded_invoice = quote_plus(str(invoice))
            encoded_comments = quote_plus(comments)
            encoded_amount = quote_plus(str(amount))
            encoded_email = quote_plus(email)
            encoded_address = quote_plus(address)
            encoded_city = quote_plus(city)
            encoded_state = quote_plus(state)
            encoded_zip = quote_plus(zip)
            encoded_phone = quote_plus(phone)
            encoded_todaysDate = quote_plus(todaysDate)

            
            payURL = f'{base_url}/tranzact?payinvoice=true&name={encoded_name}&invoice={encoded_invoice}&comments={encoded_comments}&amount={encoded_amount}&email={encoded_email}&address={encoded_address}&city={encoded_city}&state={encoded_state}&zip={encoded_zip}&phone={encoded_phone}&todaysDate={encoded_todaysDate}'

            subject = f'New Invoice: {invoice}'
            body = f"""
            Dear {name},  # Keep name unencoded in body for readability

            A new invoice has been created for you. Below are the details:

            Invoice #: {invoice}
            Item: {comments}
            Amount: ${amount}
            Status: Unpaid
            Invoice Date: {todaysDate}

            Billing Information:
            Name: {name}  # Keep name unencoded in body for readability
            Email: {email}
            Address: {address}
            City: {city}
            State: {state}
            Zip: {zip}
            Phone: {phone}

            Please make the payment at your earliest convenience. You can pay by clicking the link below:

            {payURL}

            Thank you,
            Sola
            """


            send_email(subject, body, email)
        else:
            print("Invalid or missing email")
        

        return jsonify({"status": "success", "invoice": invoice_id}), 201
    
    except Exception as e:
        # Log the exception (optional) for debugging purposes
        print(f"Error: {e}")
        
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


