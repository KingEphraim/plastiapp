import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load configuration
try:
    with open('config.json') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    raise RuntimeError(f"Failed to load config file: {e}")

# Initialize MongoDB client
try:
    client = MongoClient(config.get('client'), server_api=ServerApi('1'))
    db = client[config.get('db')]
    users_collection = db["users"]
except Exception as e:
    raise RuntimeError(f"Failed to connect to MongoDB: {e}")

class UserSettingsManager:
    def __init__(self, session):
        self.user_settings = None
        self.load_user_settings(session)

    def load_user_settings(self, session):
        if not isinstance(session, dict):
            print("Invalid session object.")
            return

        username = session.get('username')
        if not username:
            print("Username not found in session (user not logged in).")
            return

        try:
            self.user_settings = users_collection.find_one(
                {"username": username},
                {
                    "_id": 0,
                    "username": 1,
                    "useremail": 1,
                    "lbendpoint": 1,
                    "key": 1,
                    "command": 1,
                    "voidtype": 1,
                    "ebtcommand": 1,
                    "phone": 1,
                    "deviceSerialNumber": 1,
                    "deviceMake": 1,
                    "deviceFriendlyName": 1,
                    "deviceId": 1,
                    "allowDuplicate": 1,
                    "emailInvoice": 1,
                    "tapToPhone": 1,
                },
            )
            if not self.user_settings:
                print(f"No settings found for user: {username}")
        except Exception as e:
            print(f"An error occurred while loading user settings: {e}")
            self.user_settings = None
