from flask import Blueprint,session,jsonify,request,render_template,redirect,url_for
from models.user_settings import users_collection
from pymongo.errors import OperationFailure


settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/load_settings', methods=['GET'])
def load_settings():   

    if "username" not in session:
        return jsonify({'status': 'fail', 'message': 'User not logged in.'}), 403

    username = session.get('username')

    if request.method == "GET":
        try:
            # Retrieve user settings from the database
            user_settings = users_collection.find_one({"username": username}, {"_id": 0, "useremail": 1, "key": 1, "command": 1,"ebtcommand": 1, "phone": 1, "deviceSerialNumber": 1,"deviceMake": 1,"deviceFriendlyName": 1,"deviceId": 1, "googlePay": 1, "ebtOnline": 1,"threeds": 1, "ccdevice": 1})
            
            if user_settings:
                return jsonify({'status': 'success', 'settings': user_settings})
            else:
                return jsonify({'status': 'fail', 'message': 'Settings not found.'})

        except OperationFailure as e:
            # Handle MongoDB OperationFailure
            error_message = str(e)
            return jsonify({'status': 'error', 'message': error_message})

    return jsonify({'status': 'fail', 'message': 'Invalid request method.'})


@settings_bp.route('/save_settings', methods=['POST'])
def save_settings():
   

    if "username" not in session:
        return jsonify({'status': 'fail', 'message': 'User not logged in.'}), 403

    username = session.get('username')

    if request.method == "POST":
        settings_data = request.get_json()
        if settings_data:
            try:
                # Retrieve settings from the JSON data
                new_email = settings_data.get('email')
                new_key = settings_data.get('key')
                new_command = settings_data.get('command')
                new_ebtcommand = settings_data.get('ebtcommand')
                new_phone = settings_data.get('phone')
                new_deviceSerialNumber = settings_data.get('deviceSerialNumber')
                new_deviceMake= settings_data.get('deviceMake')
                new_deviceFriendlyName = settings_data.get('deviceFriendlyName')
                new_deviceId = settings_data.get('deviceId')
                new_threeds = settings_data.get('threeds')
                new_googlePay = settings_data.get('googlePay')
                new_ebtOnline = settings_data.get('ebtOnline')
                new_ccdevice = settings_data.get('ccdevice')

                

                # Update the user's settings in the database
                users_collection.update_one(
                    {"username": username},
                    {"$set": {"useremail": new_email, "key": new_key,"command": new_command,"ebtcommand": new_ebtcommand,"phone": new_phone,"deviceSerialNumber": new_deviceSerialNumber,"deviceMake": new_deviceMake,"deviceFriendlyName": new_deviceFriendlyName,"deviceId": new_deviceId,"googlePay": new_googlePay,"ebtOnline": new_ebtOnline,"threeds": new_threeds,"ccdevice": new_ccdevice}}
                )

                return jsonify({'status': 'success', 'message': 'Settings updated successfully!'})

            except OperationFailure as e:
                # Handle MongoDB OperationFailure
                error_message = str(e)
                return jsonify({'status': 'error', 'message': error_message})
        
        else:
            return jsonify({'status': 'fail', 'message': 'Invalid JSON data.'})

    return jsonify({'status': 'fail', 'message': 'Invalid request method.'})


@settings_bp.route('/settings')
def settings():
    if "username" in session:
        username = session.get('username', 'Guest')    
        message = f"You are logged in as {username}! This is your settings."    
        user_is_logged_in = session.get('user_is_logged_in', True)
        return render_template('settings.html', message=message, user_is_logged_in=user_is_logged_in)
    else:
        return redirect(url_for("auth.login"))  
