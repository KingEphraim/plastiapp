from flask import Blueprint,request,jsonify,url_for,render_template,session,redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_settings import users_collection
from pymongo.errors import OperationFailure
from models.mylogs import add_to_log

auth_bp = Blueprint('auth', __name__)


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
                username = datafromuser.get('username')
                useremail = datafromuser.get('email')
                password = datafromuser.get('password')

                if not username or not useremail or not password:
                    log_details = get_request_details()
                    add_to_log(f"Registration failed: Missing fields. Data received: {datafromuser}. {log_details}")
                    return jsonify({'status': 'fail', 'message': 'Missing username, email, or password.'})

                # Check if username already exists
                if users_collection.find_one({"username": username}):
                    log_details = get_request_details()
                    add_to_log(f"Registration failed: Username '{username}' already exists. {log_details}")
                    return jsonify({'status': 'fail', 'message': 'Username already exists.'})

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