from flask import Blueprint, session, jsonify, request, render_template, redirect, url_for
from models.user_settings import users_collection
from pymongo.errors import OperationFailure

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/load_settings', methods=['GET'])
def load_settings():
    if "username" not in session:
        return jsonify({'status': 'fail', 'message': 'User not logged in.'}), 403

    username = session['username']
    try:
        user_settings = users_collection.find_one({"username": username}, {"_id": 0})
        if user_settings:
            return jsonify({'status': 'success', 'settings': user_settings})
        return jsonify({'status': 'fail', 'message': 'Settings not found.'})
    except OperationFailure as e:
        return jsonify({'status': 'error', 'message': str(e)})

@settings_bp.route('/save_settings', methods=['POST'])
def save_settings():
    if "username" not in session:
        return jsonify({'status': 'fail', 'message': 'User not logged in.'}), 403

    username = session['username']
    settings_data = request.get_json()
    if not settings_data:
        return jsonify({'status': 'fail', 'message': 'Invalid JSON data.'})

    try:
        users_collection.update_one({"username": username}, {"$set": settings_data})
        return jsonify({'status': 'success', 'message': 'Settings updated successfully!'})
    except OperationFailure as e:
        return jsonify({'status': 'error', 'message': str(e)})

@settings_bp.route('/settings')
def settings():
    if "username" in session:
        return render_template('settings.html', message=f"You are logged in as {session['username']}!", user_is_logged_in=True)
    return redirect(url_for("auth.login"))
