import json
from pymongo import MongoClient
from bson.objectid import ObjectId

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Connect to MongoDB
client = MongoClient(config['client'])
db = client["invoices"]
invoices_collection = db["invoice"]

# Function to create an invoice
def create_invoice(invoice_data):
    """
    Creates a new invoice in the MongoDB collection.
    
    :param invoice_data: Dictionary containing invoice details
    :return: The inserted invoice ID
    """
    result = invoices_collection.insert_one(invoice_data)
    return str(result.inserted_id)

# Function to update an existing invoice
def update_invoice(invoice_id, update_data):
    """
    Updates an invoice in the MongoDB collection.

    :param invoice_id: The ID of the invoice to update
    :param update_data: Dictionary containing fields to update
    :return: The update result
    """
    result = invoices_collection.update_one(
        {"_id": ObjectId(invoice_id)},
        {"$set": update_data}
    )
    return result.modified_count

# Function to view a specific invoice
def view_invoice(invoice_id):
    """
    Retrieves an invoice from the MongoDB collection.

    :param invoice_id: The ID of the invoice to retrieve
    :return: The invoice data or None if not found
    """
    invoice = invoices_collection.find_one({"_id": ObjectId(invoice_id)})
    if invoice:
        invoice["_id"] = str(invoice["_id"])  # Convert ObjectId to string for easier handling
    return invoice

# Function to list all invoices
def list_invoices():
    """
    Retrieves all invoices from the MongoDB collection.

    :return: A list of all invoice documents
    """
    invoices = list(invoices_collection.find())
    for invoice in invoices:
        invoice["_id"] = str(invoice["_id"])  # Convert ObjectId to string
    return invoices

# Function to delete an invoice
def delete_invoice(invoice_id):
    """
    Deletes an invoice from the MongoDB collection.

    :param invoice_id: The ID of the invoice to delete
    :return: The deletion result
    """
    result = invoices_collection.delete_one({"_id": ObjectId(invoice_id)})
    return result.deleted_count
