from pymongo import MongoClient
import json

with open('config.json') as f:
    config = json.load(f)

def add_item_to_database(item):
    try:
        # Connect to MongoDB
        client = MongoClient(config['mongodbstring'])
        db = client['tranzact']

        
        # Insert the item into the collection
        collection = db['transactions']
        result = collection.insert_one(item)

        # Close the MongoDB connection
        client.close()
        
        

        return result.inserted_id
    except Exception as e:
        # Handle exceptions and close the connection
        client.close()
        raise e
    
def update_item_in_database(item_id, updated_data):
    try:
        # Connect to MongoDB
        client = MongoClient(config['mongodbstring'])
        db = client['tranzact']
        
        # Specify the collection
        collection = db['transactions']

        # Define the filter based on the item_id
        filter_criteria = {'_id': item_id}

        # Use the update_one method to update the existing item
        result = collection.update_one(filter_criteria, {'$set': updated_data})

        # Close the MongoDB connection
        client.close()

        return result.modified_count  # Returns the number of modified documents
    except Exception as e:
        # Handle exceptions and close the connection
        client.close()
        raise e