from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from flask_jwt_extended import get_jwt_identity, jwt_required
from apps.post.models import db


post = Blueprint('post', __name__)

################# create template ####################
@post.route("/template", methods=["POST"])
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
@post.route("/template", methods=["GET"])
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
@post.route("/template/<id>", methods=["GET"])
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
@post.route("/template/<id>", methods=["PUT"])
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
@post.route("/template/<id>", methods=["DELETE"])
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
