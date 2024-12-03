from pymongo import MongoClient
from bson.objectid import ObjectId
import json

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# MongoDB connection utility
def get_db():
    client = MongoClient(config['mongodbstring'])
    return client, client['tranzact']

# Add item to database
def add_item_to_database(item):
    try:
        client, db = get_db()

        # Example input validation (ensure 'amount' is a positive number)
        if 'amount' in item and (not isinstance(item['amount'], (int, float)) or item['amount'] <= 0):
            raise ValueError("Invalid 'amount' value")

        result = db['transactions'].insert_one(item)
        return result.inserted_id
    except Exception as e:
        raise e
    finally:
        client.close()

# Update item in database
def update_item_in_database(item_id, updated_data):
    try:
        client, db = get_db()

        # Validate ObjectId
        if not ObjectId.is_valid(item_id):
            raise ValueError("Invalid ObjectId format")
        object_id = ObjectId(item_id)

        # Example sanitization: Remove keys that shouldn't be updated
        sanitized_data = {k: v for k, v in updated_data.items() if k not in ['_id']}
        result = db['transactions'].update_one({'_id': object_id}, {'$set': sanitized_data})

        return result.modified_count
    except Exception as e:
        raise e
    finally:
        client.close()
