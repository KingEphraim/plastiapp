import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi


with open('config.json') as f:
    config = json.load(f) 

client = MongoClient(config['client'],server_api=ServerApi('1'))
db = client[config['db']]  # Change this to your actual database name
users_collection = db["users"]
class UserSettingsManager:
    def __init__(self, session):
        self.user_settings = None
        self.load_user_settings(session)

    def load_user_settings(self, session):
        try:
            username = session.get('username')
            print(username)
            if username is None:
                raise ValueError("Username not found in session.")
            
            self.user_settings = users_collection.find_one({"username": username}, {"_id": 0, "useremail": 1, "key": 1,"command": 1, "ebtcommand": 1, "phone": 1,"deviceSerialNumber": 1,"deviceMake": 1,"deviceFriendlyName": 1,"deviceId": 1,"allowDuplicate":1})
            
        except Exception as e:
            print(f"An error occurred: {e}")
            self.user_settings = None