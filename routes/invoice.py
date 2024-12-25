from flask import Blueprint,request,jsonify,render_template,session,redirect,url_for
from models.invoiceDB import create_invoice,list_invoices
from datetime import datetime
import re
from models.sendEmail import send_email
from urllib.parse import quote_plus


invoice__bp = Blueprint('invoice', __name__)

@invoice__bp.route('/invoice', methods=['GET'])
def invoice():
    
    user_is_logged_in = "username" in session

    if 'username' not in session:        
        return redirect(url_for('auth.login'))    
    return render_template('invoice.html',user_is_logged_in=user_is_logged_in)

@invoice__bp.route('/listInvoices')
def listInvoices():
    username = session.get('username')    
    invoices = list_invoices(username) 
    for invoice in invoices:
        full_address = f"{invoice['address']}, {invoice['city']}, {invoice['state']} {invoice['zip']}"
        invoice['fullAddress'] = full_address        
        del invoice['address']
        del invoice['city']
        del invoice['state']
        del invoice['zip']
        formatted_items = [f"Name:{item['name']} Price:{item['price']}" for item in invoice['items']]
        invoice['items'] = formatted_items
        if 'payments' in invoice:
            formatted_payments = [f"Refnum:{payment['paidRefnum']} Paid:{payment['paidAmount']}\n" for payment in invoice['payments']]
            invoice['payments'] = formatted_payments
        else:
            invoice['payments'] = []  
    print(invoices)
    return jsonify(invoices)



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
        "accountUsername": session.get('username'),
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

        
        db_invoice_id = create_invoice(new_invoice)
        print(f"Invoice created with ID: {db_invoice_id}")

        
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

            
            payURL = f'{base_url}/tranzact?payinvoice=true&dbinvoiceid={db_invoice_id}&name={encoded_name}&invoice={encoded_invoice}&comments={encoded_comments}&amount={encoded_amount}&email={encoded_email}&address={encoded_address}&city={encoded_city}&state={encoded_state}&zip={encoded_zip}&phone={encoded_phone}&todaysDate={encoded_todaysDate}'

            subject = f'New Invoice: {invoice}'
            body = f"""
            Dear {name},  

            A new invoice has been created for you. Below are the details:

            Invoice #: {invoice}
            Item: {comments}
            Amount: ${amount}
            Status: Unpaid
            Invoice Date: {todaysDate}

            Billing Information:
            Name: {name}  
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
        

        return jsonify({"status": "success", "invoice": db_invoice_id}), 201
    
    except Exception as e:
        # Log the exception (optional) for debugging purposes
        print(f"Error: {e}")
        
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


