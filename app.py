from flask import Flask, request, jsonify
import hashlib
from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager


app = Flask(__name__)
# Setup Flask-JWT-Extended extension
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)

# Database Schema validation

user_validator ={
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

# Setup database connection
try:
    client = MongoClient("mongodb+srv://ayobanji:jinaboya1212@cluster0.uirbk.mongodb.net/?retryWrites=true&w=majority&authSource=admin")
    db = client["sloovidata"]
    db.create_collection("users")
    db.command("collMod", "users", validator=user_validator)
    db.create_collection("templates")
    db.command("collMod", "templates", validator=template_validator)
    client.server_info() # Trigger exception if connection to db failed
except Exception as e:
    print( e)

########### user registration ###########
@app.route("/register", methods=["POST"])
def register():
    
    try:
        new_user = request.json # store the json body request
        new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() # encrpt password
        
        if db.users.find_one({"email":new_user["email"]}): # Check if email exist
            return jsonify({"Message":"Email address already in use"}), 409
        db.users.insert_one(new_user)
        return jsonify({"message":"User created successfully"}) ,200

    except:
        return jsonify({"message":"failed to create user"}), 500

################## login ############### 
@app.route("/login", methods=["POST"])
def login():

    try:
        login_details = request.json # store the json body request
        user_from_db = db.users.find_one({"email":login_details["email"]})# search for user in database
        if not user_from_db:
            return jsonify({"message":"User not found for the email"}), 401
        if user_from_db:
            encrypted_password = hashlib.sha256(login_details["password"].encode("utf-8")).hexdigest()
            if encrypted_password == user_from_db["password"]:
                access_token = create_access_token(identity=user_from_db["email"]) # create jwt token
                return jsonify({"message":"login successful", "Token":access_token}), 200
            return jsonify({"message":"password not match"}), 401
        return jsonify({"message":"User not found"}), 401

    except:
        return jsonify({"message": "failed to login"}), 401

################# create template ####################
@app.route("/template", methods=["POST"])
@jwt_required()
def create_template():

    try:
        template = request.json
        current_user = get_jwt_identity() # Get the identity of the current user
        template["user_id"] = current_user
        user_in_db = db.users.find_one({"email":current_user}) #check if user exist in db to avoid deleted account access
        if not user_in_db:
            return jsonify({"message":"You must be a user to create template"}), 401
        if db.templates.find_one({"template_name":template["template_name"]}):
            return jsonify({"message":"Template name already exist"}), 409
        template_to_db = db.templates.insert_one(template)
        return jsonify({"message":"Template created", "id":f"{template_to_db.inserted_id}"}), 200

    except:
        return jsonify({"message":"failed to create template"}),  500 

################### read template ####################
@app.route("/template", methods=["GET"])
@jwt_required()
def get_templates():
    
    try:
        current_user = get_jwt_identity() # Get the identity of the current user  
        user_in_db = db.users.find_one({"email":current_user}) #check if user exist in db to avoid deleted account access
        if not user_in_db:
            return jsonify({"message":"You must be a user to view templates"}), 401  
        templates_from_db = list(db.templates.find({"user_id":current_user}))
        if not templates_from_db:
            return jsonify({"message":"no template found"}),  500
        for template in templates_from_db:
            template["_id"] = str(template["_id"])
        return jsonify(templates_from_db), 200
    
    except:
        return jsonify({"message":"failed to read templates"}),  500

################### read single template ####################
@app.route("/template/<id>", methods=["GET"])
@jwt_required()
def get_template(id):
    
    try:
        current_user = get_jwt_identity() # Get the identity of the current user
        user_in_db = db.users.find_one({"email":current_user}) #check if user exist in db to avoid deleted account access
        if not user_in_db:
            return jsonify({"message":"You must be a user to view template"}), 401
        template = db.templates.find_one({"_id":ObjectId(id)})
        if not template:
            return jsonify({"message":"Template not found"}), 401
        template["_id"] = str(template["_id"])

        if template["user_id"] != current_user:
            return jsonify({"message":"No authorization"}), 401

        return jsonify(template), 200
    except Exception as e:
        return e #jsonify({"message":"cannot read template"}),  500

################# update template ######################
@app.route("/template/<id>", methods=["PUT"])
@jwt_required()
def update_template(id):

    try:
        current_user = get_jwt_identity() # Get the identity of the current user
        user_in_db = db.users.find_one({"email":current_user}) #check if user exist in db to avoid deleted account access
        if not user_in_db:
            return jsonify({"message":"You must be a user to update template"}), 401
        template = db.templates.find_one({"_id":ObjectId(id)})
        if not template:
            return jsonify({"message":"Template not found"}), 401

        if template["user_id"] != current_user:
            return jsonify({"message":"No authorization"}), 401
        
        db_data = db.templates.update_one(
            {"_id":ObjectId(id)},
            {"$set":{"template_name":request.json["template_name"],"subject":request.json["subject"],"body":request.json["body"]}})
        
        if db_data.modified_count == 1:
            return jsonify({"message":"template updated"}), 200
        return jsonify({"message":"No changes made"}), 409
    except:
        return jsonify({"message":"failed to update template"}), 500

##################### delete template ###################
@app.route("/template/<id>", methods=["DELETE"])
@jwt_required()
def delete_template(id):
    try:
        current_user = get_jwt_identity() # Get the identity of the current user
        user_in_db = db.users.find_one({"email":current_user}) #check if user exist in db to avoid deleted account access
        if not user_in_db:
            return jsonify({"message":"You must be a user to update template"}), 401
        template = db.templates.find_one({"_id":ObjectId(id)})
        if not template:
            return jsonify({"message":"Template not found"}), 401

        if template["user_id"] != current_user:
            return jsonify({"message":"No authorization"}), 401

        db_data = db.templates.delete_one({"_id":ObjectId(id)})
        if db_data.deleted_count == 1:
            return jsonify({"message":"template deleted", "id":f"{id}"}), 200
        return jsonify({"message":"template not found", "id":f"{id}"}), 200
    except:
        return jsonify({"message":"failed to deleted template"}), 500

if __name__ == "__main__":
    app.run(debug=True)