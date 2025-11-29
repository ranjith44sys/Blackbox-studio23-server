# from database.mongo_connection import db
#   # 👈 import existing db

# collection = db["contact_messages"]   # new collection inside your same DB

# def save_contact(data):
#     result = collection.insert_one(data)
#     return str(result.inserted_id)


from database.mongo_connection import db

def save_contact(data):
    """Save contact form data to MongoDB"""
    try:
        contact_collection = db["contacts"]
        result = contact_collection.insert_one(data)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error saving contact: {str(e)}")
        raise