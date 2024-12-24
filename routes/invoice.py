from flask import Blueprint,request,jsonify
from models.invoiceDB import create_invoice
from datetime import datetime
import re
from models.sendEmail import send_email
import socket
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
        comments = data.get('comments','')

        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        new_invoice = {
        "customer_name": name,
        "items": [
            {"name": comments, "price": amount, "quantity": 1}
        ],
        "total": amount,
        "status": "Unpaid",
        "created_at": todaysDate
        }
        
        invoice_id = create_invoice(new_invoice)
        print(f"Invoice created with ID: {invoice_id}")

        email = data.get('email')
        if email and re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
            print(f"Valid email: {email}")

                # Determine the correct origin based on the host
            is_local = request.host.startswith('127.0.0.1') or request.host.startswith('localhost')
            base_url = 'http://127.0.0.1:5000' if is_local else 'https://app.cardknox.link'

            
            encoded_name = quote_plus(name)
            # Construct the URL dynamically
            payURL = f"{base_url}/tranzact?payinvoice=true&name={encoded_name}&amount={amount}"

            subject = f'New Invoice: {invoice_id}'
            body = f'Dear {data.get('name')}, a new invoice has been created for you. Item: {comments}, Amount: ${amount}, Total: ${amount}, Status: Unpaid, Invoice Date: {todaysDate}. Please make the payment at your earliest convenience. Thank you, Sola. Click this link to pay {payURL}'
            send_email(subject, body, email)
        else:
            print("Invalid or missing email")
        

        return jsonify({"status": "success", "invoice": invoice_id}), 201
    
    except Exception as e:
        # Log the exception (optional) for debugging purposes
        print(f"Error: {e}")
        
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


