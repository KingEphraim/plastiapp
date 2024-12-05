from flask import Blueprint,request,jsonify,url_for,render_template,session,redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_settings import users_collection
from pymongo.errors import OperationFailure
from models.mylogs import add_to_log

auth_bp = Blueprint('auth', __name__)


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
                    add_to_log(f"Registration failed: Missing fields. Data received: {datafromuser}")
                    return jsonify({'status': 'fail', 'message': 'Missing username, email, or password.'})

                # Check if username already exists
                if users_collection.find_one({"username": username}):
                    add_to_log(f"Registration failed: Username '{username}' already exists.")
                    return jsonify({'status': 'fail', 'message': 'Username already exists.'})

                # Hash the password using the 'scrypt' method
                hashed_password = generate_password_hash(password, method="scrypt")

                # Insert the user into the database
                users_collection.insert_one({"username": username, "useremail": useremail, "password": hashed_password})

                add_to_log(f"Registration successful for username: {username}, email: {useremail}")
                return jsonify({'status': 'success', 'redirect': url_for('auth.login')})

            except OperationFailure as e:
                # Handle MongoDB OperationFailure
                error_message = str(e)
                add_to_log(f"Registration error: {error_message}")
                return jsonify({'status': 'error', 'message': error_message})

        else:
            add_to_log("Registration failed: Invalid JSON data.")
            return jsonify({'status': 'fail', 'message': 'Invalid JSON data.'})

    add_to_log("Registration page accessed.")
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
                    add_to_log(f"Login failed: Missing username or password. Data received: {datafromuser}")
                    return jsonify({'status': 'fail', 'message': 'Missing username or password.'})

                user = users_collection.find_one({"username": username})

                if not user:
                    add_to_log(f"Login failed: User '{username}' not found.")
                    return jsonify({'status': 'fail', 'message': 'User not found.'})

                if not check_password_hash(user['password'], password):
                    add_to_log(f"Login failed: Incorrect password for user '{username}'.")
                    return jsonify({'status': 'fail', 'message': 'Incorrect password.'})

                session['username'] = username
                session['user_is_logged_in'] = True

                add_to_log(f"Login successful for user '{username}'.")
                return jsonify({'status': 'success', 'message': 'Login successful.'})

            except Exception as e:
                error_message = str(e)
                add_to_log(f"Login error for user '{username}': {error_message}")
                return jsonify({'status': 'error', 'message': error_message})

        else:
            add_to_log("Login failed: Invalid JSON data.")
            return jsonify({'status': 'fail', 'message': 'Invalid JSON data.'})

    add_to_log("Login page accessed.")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    username = session.get("username", None)
    if username:
        add_to_log(f"User '{username}' logged out.")
    else:
        add_to_log("Logout attempt with no user logged in.")
    
    session.pop("username", None)
    return redirect(url_for("auth.login"))