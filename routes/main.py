from flask import Blueprint, render_template,request,session,redirect,url_for,jsonify
from models.mylogs import add_to_log
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():    
    return render_template('index.html', user_is_logged_in='username' in session)


@main_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy"), 200


@main_bp.route("/dashboard")
def dashboard():
    add_to_log(f"Visit to / Method: {request.method} Remote_addr: {request.headers.get('X-Forwarded-For', request.remote_addr)} User-Agent: {request.headers.get('User-Agent')}") 
    if "username" in session:
        username = session.get('username', 'Guest')    
        message = f"You are logged in as {username}! This is your dashboard."    
        user_is_logged_in = session.get('user_is_logged_in', True)
        return render_template('dashboard.html', message=message, user_is_logged_in=user_is_logged_in)
    else:
        return redirect(url_for("auth.login"))  

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')