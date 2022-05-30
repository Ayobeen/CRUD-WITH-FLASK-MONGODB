from database.database import db

template_validator = {
      "$jsonSchema": {
         "bsonType": "object",
         "required": [ "template_name", "user_id", "subject", "body"],
         "properties": {
            "template_name": {
               "bsonType": "string",
               "description": "must be a string and is required"
            },
            "user_id": {
               "bsonType": "string",
               "description": "must be an email and is required"
            },
            "subject": {
               "bsonType": "string",
               "description": "must be a string and is required"
            },
            "body": {
               "bsonType": "string",
               "description": "must be a string and is required"
            },
         }
      }
   }

db.command("collMod", "templates", validator=template_validator)
