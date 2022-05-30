from flask import Blueprint, request, jsonify
import hashlib
from flask_jwt_extended import create_access_token
from apps.auth.models import db


auth = Blueprint('auth', __name__)

########### user registration ###########
@auth.route("/register", methods=["POST"])
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
@auth.route("/login", methods=["POST"])
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
