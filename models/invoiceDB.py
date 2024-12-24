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



def modify_invoice(invoice_id, update_data):
    """
    Updates an invoice in the MongoDB collection by setting or appending to fields.

    :param invoice_id: The ID of the invoice to update
    :param update_data: Dictionary containing fields to update (either set or append data)
    :return: The number of documents modified
    """
    update_query = {}

    # Constructing the update query
    for key, value in update_data.items():
        if isinstance(value, list):  # Append to an array field
            update_query.setdefault("$push", {})[key] = {"$each": value}
        else:  # Set non-array fields
            update_query.setdefault("$set", {})[key] = value

    # Perform the update
    result = invoices_collection.update_one(
        {"_id": ObjectId(invoice_id)},
        update_query
    )
    mark_invoice_as_paid(invoice_id)
    return result.modified_count

def mark_invoice_as_paid(invoice_id):
    """
    Checks if the total amount paid (sum of paidAmount in payments array) is greater than or equal to the total
    amount due for the invoice. If true, updates the status to 'paid'.

    :param invoice_id: The ID of the invoice to check and update
    :return: The number of documents modified
    """
    # Retrieve the invoice to check total and payments
    invoice = invoices_collection.find_one({"_id": ObjectId(invoice_id)})

    if invoice:
        # Convert total to float to ensure comparison works properly
        total = float(invoice.get("total", 0))  # Ensure total is a float
        payments = invoice.get("payments", [])

        # Calculate the total paid amount from the payments array, ensuring paidAmount is treated as a float
        total_paid = sum(float(payment.get("paidAmount", 0)) for payment in payments)

        # Check if the paid amount is greater than or equal to the total amount
        if total_paid >= total:
            # Update the status to 'paid'
            update_query = {
                "$set": {"status": "paid"}
            }
            result = invoices_collection.update_one(
                {"_id": ObjectId(invoice_id)},
                update_query
            )
            return result.modified_count

    return 0  # Return 0 if the invoice is not found or condition is not met



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
