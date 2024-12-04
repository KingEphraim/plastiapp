from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from mylogs import add_to_log  # Assuming 'mylogs.py' contains your logging function

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# MongoDB connection utility
def get_db():
    client = MongoClient(config['client'])
    return client, client['tranzact']

# Add item to database
def add_item_to_database(item):
    """
    Inserts an item into the 'transactions' collection and returns the inserted document's ID.

    Args:
        item (dict): The item to be added to the database.

    Returns:
        str: The ID of the inserted document.
    """
    try:
        # Get the database client and the database instance
        client, db = get_db()
        
        # Specify the collection to insert into
        collection = db['transactions']  # Ensure 'transactions' is the correct collection name
        
        # Insert the item into the collection
        result = collection.insert_one(item)
        
        # Log the operation
        log_message = f"Item added to database with ID: {result.inserted_id} {item}"
        add_to_log(log_message)  # Log the insertion
        
        # Return the ID of the inserted document as a string
        return str(result.inserted_id)
    except Exception as e:
        # Log or debug the exception
        raise RuntimeError(f"Failed to add item to database: {e}") from e
    finally:
        # Ensure the client is closed to release resources
        if client:
            client.close()

# Update item in database
def update_item_in_database(document_id, additional_data):
    """
    Updates a document in the 'transactions' collection by adding or modifying fields.

    Args:
        document_id (str): The ID of the document to update.
        additional_data (dict): The additional data to add or update in the document.

    Returns:
        dict: The result of the update operation.
    """
    try:
        # Get the database client and the database instance
        client, db = get_db()
        
        # Specify the collection to update
        collection = db['transactions']
        
        # Convert the document_id back to ObjectId
        object_id = ObjectId(document_id)
        
        # Update the document with new data
        result = collection.update_one(
            {"_id": object_id},  # Match document by ID
            {"$set": additional_data}  # Add or update fields
        )
        
        # Log the update operation
        log_message = f"Item with ID {document_id} updated. Matched count: {result.matched_count}, Modified count: {result.modified_count} {additional_data}"
        add_to_log(log_message)  # Log the update
        
        # Return the result of the update operation
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }
    except Exception as e:
        # Log or debug the exception
        raise RuntimeError(f"Failed to update item in database: {e}") from e
    finally:
        # Ensure the client is closed to release resources
        if client:
            client.close()
