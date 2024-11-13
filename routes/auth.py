from flask import Blueprint,request,jsonify,url_for,render_template,session,redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_settings import users_collection
from pymongo.errors import OperationFailure

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


@auth_bp.route("/login", methods=["GET", "POST"])
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

@auth_bp.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("auth.login"))