from pymongo import MongoClient

# Setup database connection
try:
    client = MongoClient("mongodb+srv://ayobanji:password123@cluster0.uirbk.mongodb.net/?retryWrites=true&w=majority&authSource=admin")
    db = client["sloovi"]
    db.create_collection("users")
    db.create_collection("templates")
    client.server_info() # Trigger exception if connection to db failed
except Exception as e:
    print( e)
