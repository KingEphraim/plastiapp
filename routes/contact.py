from flask import Blueprint, request, jsonify
from models.sendEmail import send_email
contact__bp = Blueprint('contact', __name__)


@contact__bp.route('/contact', methods=['POST'])
def contact_form():
    try:
        # Assuming the form data is sent as JSON
        data = request.get_json()
        
        # Example: Extracting form data (name, email, message)
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        print(data)

        try:
            # Attempt to send the email
            send_email("Contact Us Message (plastiqz)", f'From: {name} Email: {email} Message: {message}', "elefkowitz@cardknox.com")
            print("The email was sent successfully.")
        except Exception as e:
            # Handle any exceptions that occur
            print(f"An error occurred while sending the email: {e}")

        if not name or not email or not message:
            return jsonify({'error': 'All fields are required'}), 400
        
        # You can process the data here (e.g., send an email, store it in the database, etc.)
        # For this example, we just return a success response
        return jsonify({'status': 'success', 'message': 'Your message has been sent successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500