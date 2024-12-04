import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Initialize MongoDB client
client = MongoClient(config['client'], server_api=ServerApi('1'))
db = client[config['db']]  # Replace with your actual database name
users_collection = db["users"]

class UserSettingsManager:
    def __init__(self, session):
        self.user_settings = None
        self.load_user_settings(session)

    def load_user_settings(self, session):   
        try:
            username = session.get('username')
            if not username:
                raise ValueError("Username not found in session (user not logged in).")

            # Use a projection to limit the fields retrieved
            self.user_settings = users_collection.find_one(
                {"username": username},
                {
                    "_id": 0,
                    "useremail": 1,
                    "key": 1,
                    "command": 1,
                    "ebtcommand": 1,
                    "phone": 1,
                    "deviceSerialNumber": 1,
                    "deviceMake": 1,
                    "deviceFriendlyName": 1,
                    "deviceId": 1,
                    "allowDuplicate": 1,
                },
            )
            if not self.user_settings:
                raise ValueError(f"No settings found for user: {username}")
        except ValueError as ve:
            print(f"Validation error: {ve}")
            self.user_settings = None
        except Exception as e:
            print(f"An error occurred while loading user settings: {e}")
            self.user_settings = None
