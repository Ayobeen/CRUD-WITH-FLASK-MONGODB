from database.database import db

# Database Schema validation
user_validator = {
    "$jsonSchema": {
         "bsonType": "object",
         "required": [ "first_name", "last_name", "email", "password"],
         "properties": {
            "first_name": {
               "bsonType": "string",
               "description": "must be a string and is required"
            },
            "last_name": {
               "bsonType": "string",
               "description": "must be an email and is required"
            },
            "email": {
               "bsonType": "string",
               "description": "must be a string and is required"
            },
            "password": {
               "bsonType": "string",
               "description": "must be a string and is required"
            },
         }
      }
}

db.command("collMod", "users", validator=user_validator)