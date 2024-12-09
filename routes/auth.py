from flask import Blueprint,request,jsonify,url_for,render_template,session,redirect,json
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_settings import users_collection
from pymongo.errors import OperationFailure
from models.mylogs import add_to_log
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from models.sendEmail import send_email
from models.handleRecaptcha import verify_recaptcha

auth_bp = Blueprint('auth', __name__)

with open('config.json') as f:
    config = json.load(f) 

def get_request_details():
    """Helper function to get relevant request details for logging."""
    remote_addr = request.remote_addr
    forwarded_for = request.headers.get('X-Forwarded-For', remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown User-Agent')
    return f"Remote Addr: {remote_addr}, X-Forwarded-For: {forwarded_for}, User-Agent: {user_agent}"

@auth_bp.route("/register", methods=["GET", "POST"])
def register():    
    if request.method == "POST":
        datafromuser = request.get_json()
        if datafromuser:
            try:
                # Extract form fields
                username = datafromuser.get('username')
                useremail = datafromuser.get('email')
                password = datafromuser.get('password')
                recaptcha_response = datafromuser.get('g-recaptcha-response')  # Get the reCAPTCHA token

                # Check if all required fields are present
                if not username or not useremail or not password or not recaptcha_response:
                    log_details = get_request_details()
                    add_to_log(f"Registration failed: Missing fields. Data received: {datafromuser}. {log_details}")
                    return jsonify({'status': 'fail', 'message': 'Missing username, email, password, or reCAPTCHA token.'})

                # Verify reCAPTCHA response and get the score
                success, score = verify_recaptcha(recaptcha_response)
                if not success:
                    log_details = get_request_details()
                    add_to_log(f"Registration failed: reCAPTCHA verification failed. {log_details}")
                    return jsonify({'status': 'fail', 'message': 'reCAPTCHA verification failed.'})

                # Optionally, handle the score: if it's below a threshold, deny registration
                if score is not None and score < 0.5:
                    log_details = get_request_details()
                    add_to_log(f"Registration failed: Low reCAPTCHA score of {score}. {log_details}")
                    return jsonify({'status': 'fail', 'message': 'Low reCAPTCHA score. Registration not allowed.'})

                # Check if username already exists
                if users_collection.find_one({"username": username}):
                    log_details = get_request_details()
                    add_to_log(f"Registration failed: Username '{username}' already exists. {log_details}")
                    return jsonify({'status': 'fail', 'message': 'Username already exists.'})

                # Check if email already exists
                if users_collection.find_one({"useremail": useremail}):
                    log_details = get_request_details()
                    add_to_log(f"Registration failed: Email '{useremail}' already exists. {log_details}")
                    return jsonify({'status': 'fail', 'message': 'Email already exists.'})

                # Hash the password using the 'scrypt' method
                hashed_password = generate_password_hash(password, method="scrypt")

                # Insert the user into the database
                users_collection.insert_one({"username": username, "useremail": useremail, "password": hashed_password})

                log_details = get_request_details()
                add_to_log(f"Registration successful for username: {username}, email: {useremail}. {log_details}")
                return jsonify({'status': 'success', 'redirect': url_for('auth.login')})

            except OperationFailure as e:
                error_message = str(e)
                log_details = get_request_details()
                add_to_log(f"Registration error: {error_message}. {log_details}")
                return jsonify({'status': 'error', 'message': error_message})

        else:
            log_details = get_request_details()
            add_to_log(f"Registration failed: Invalid JSON data. {log_details}")
            return jsonify({'status': 'fail', 'message': 'Invalid JSON data.'})

    log_details = get_request_details()
    add_to_log(f"Registration page accessed. {log_details}")
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        datafromuser = request.get_json()
        if datafromuser:
            try:
                username = datafromuser.get('username')
                password = datafromuser.get('password')

                if not username or not password:
                    log_details = get_request_details()
                    add_to_log(f"Login failed: Missing username or password. Data received: {datafromuser}. {log_details}")
                    return jsonify({'status': 'fail', 'message': 'Missing username or password.'})

                user = users_collection.find_one({"username": username})

                if not user:
                    log_details = get_request_details()
                    add_to_log(f"Login failed: User '{username}' not found. {log_details}")
                    return jsonify({'status': 'fail', 'message': 'User not found.'})

                if not check_password_hash(user['password'], password):
                    log_details = get_request_details()
                    add_to_log(f"Login failed: Incorrect password for user '{username}'. {log_details}")
                    return jsonify({'status': 'fail', 'message': 'Incorrect password.'})

                session['username'] = username
                session['user_is_logged_in'] = True

                log_details = get_request_details()
                add_to_log(f"Login successful for user '{username}'. {log_details}")
                return jsonify({'status': 'success', 'message': 'Login successful.'})

            except Exception as e:
                error_message = str(e)
                log_details = get_request_details()
                add_to_log(f"Login error for user '{username}': {error_message}. {log_details}")
                return jsonify({'status': 'error', 'message': error_message})

        else:
            log_details = get_request_details()
            add_to_log(f"Login failed: Invalid JSON data. {log_details}")
            return jsonify({'status': 'fail', 'message': 'Invalid JSON data.'})

    log_details = get_request_details()
    add_to_log(f"Login page accessed. {log_details}")
    return render_template("login.html")

@auth_bp.route('/auth_check', methods=['GET'])
def auth_check():
    if "username" in session:
        return jsonify({'status': 'success', 'message': 'User is logged in.'})
    return jsonify({'status': 'fail', 'message': 'User is not logged in.'}), 401


@auth_bp.route("/logout")
def logout():
    username = session.get("username", None)
    log_details = get_request_details()
    if username:
        add_to_log(f"User '{username}' logged out. {log_details}")
    else:
        add_to_log(f"Logout attempt with no user logged in. {log_details}")
    
    session.pop("username", None)
    return redirect(url_for("auth.login"))

@auth_bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if request.method == "GET":
        # Render the reset password request form for GET requests
        return render_template("reset_password_request.html")
    
    # Handle the POST request for password reset
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        log_details = get_request_details()
        add_to_log(f"Reset password request failed: No email provided. {log_details}")
        return jsonify({'status': 'fail', 'message': 'No email provided.'})

    user = users_collection.find_one({"useremail": email})
    if not user:
        log_details = get_request_details()
        add_to_log(f"Reset password request failed: No account with email '{email}' found. {log_details}")
        return jsonify({'status': 'fail', 'message': 'No account found with that email.'})   
    
    username = user.get('username', 'User')  # Retrieve the username (default to 'User' if not found)
    
    # Generate a reset token with expiration
    s = URLSafeTimedSerializer(config['reset_email_secret_key'])
    token = s.dumps(email, salt='password-reset')
    
    reset_link = url_for('auth.reset_password', token=token, _external=True)
    
    # Save the token in the database (invalidate old ones)
    users_collection.update_one(
        {"useremail": email},
        {"$set": {"reset_token": token}}
    )
    
    # Send the password reset link to the user's email
    send_email("Plastiqz Password Reset Request", 
               f"Hello {username},\n\nClick here to reset your password: {reset_link}", 
               email)
    
    log_details = get_request_details()
    add_to_log(f"Password reset request sent to email '{email}'. {log_details}")
    
    return jsonify({'status': 'success', 'message': 'Password reset link sent to your email.'})


@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        s = URLSafeTimedSerializer(config['reset_email_secret_key'])
        email = s.loads(token, salt='password-reset', max_age=3600)  # Token expires in 1 hour
    except (BadSignature, SignatureExpired):
        return jsonify({'status': 'fail', 'message': 'Invalid or expired reset token.'})

    user = users_collection.find_one({"useremail": email})
    if not user:
        return jsonify({'status': 'fail', 'message': 'No account found with that email.'})
    
    # Validate the token
    if user.get("reset_token") != token:
        return jsonify({'status': 'fail', 'message': 'Invalid or expired reset token.'})
    
    if request.method == "POST":
        data = request.get_json()
        new_password = data.get('password')
        
        if not new_password:
            return jsonify({'status': 'fail', 'message': 'Password is required.'})
        
        # Hash the new password
        hashed_password = generate_password_hash(new_password, method="scrypt")
        
        # Update the user's password in the database and invalidate the token
        users_collection.update_one(
            {"useremail": email},
            {"$set": {"password": hashed_password}, "$unset": {"reset_token": ""}}
        )
        
        log_details = get_request_details()
        add_to_log(f"Password for email '{email}' has been reset. {log_details}")
        
        # Redirect to login page with a query parameter
        return redirect(url_for('auth.login', message='password-reset-success'))

    return render_template("reset_password.html", token=token)



