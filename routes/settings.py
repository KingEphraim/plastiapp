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
            if 'key' in user_settings:
                key = user_settings['key']
                # Determine the length of the key
                key_length = len(key)
                
                if key_length > 10:
                    # Unmask the first 5 and last 5 characters
                    masked_key = key[:5] + '*' * min(6, key_length - 10) + key[-5:]
                else:
                    # If the key is too short to apply masking, leave it as is
                    masked_key = key
                
                user_settings['key'] = masked_key  # Replace the original key with the masked key



            # Remove the password from the user settings before returning
            if 'password' in user_settings:
                del user_settings['password']

            return jsonify({'status': 'success', 'settings': user_settings})
        return jsonify({'status': 'fail', 'message': 'Settings not found.'})
    except OperationFailure as e:
        return jsonify({'status': 'error', 'message': str(e)})



@settings_bp.route('/save_settings', methods=['POST'])
def save_settings():
    if "username" not in session:
        return jsonify({'status': 'fail', 'message': 'User not logged in.'}), 403

    current_username = session['username']
    settings_data = request.get_json()

    if not settings_data:
        return jsonify({'status': 'fail', 'message': 'Invalid JSON data.'})

    # Check if "key" is in settings_data and is empty, then remove it
    if 'key' in settings_data and not settings_data['key']:
        del settings_data['key']

    try:
        # Check if username is updated
        new_username = settings_data.get('username')
        username_changed = new_username and new_username != current_username

        # Update user settings in DB
        users_collection.update_one({"username": current_username}, {"$set": settings_data})

        # If username changed, log out the user
        if username_changed:
            session.clear()
            return jsonify({'status': 'success', 'message': 'Username updated. Please log in again.'}), 401

        return jsonify({'status': 'success', 'message': 'Settings updated successfully!'})
    except OperationFailure as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@settings_bp.route('/settings')
def settings():
    if "username" in session:
        return render_template('settings.html', message=f"You are logged in as {session['username']}!", user_is_logged_in=True)
    return redirect(url_for("auth.login"))
