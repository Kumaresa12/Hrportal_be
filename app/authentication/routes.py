from flask import Blueprint, Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import make_response

from app.authentication.models import get_user, insert_user

auth = Blueprint('auth', __name__)


@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if get_user(username):
        return jsonify({"msg": "User already exists"}), 400
    
    hashed_password = generate_password_hash(password)

    insert_user(username, hashed_password)
    
    return jsonify({"msg": "User registered successfully"}), 201

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    user = get_user(username)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=username)
    response = make_response(jsonify({"msg": "Login successful"}), 200)
    response.set_cookie("access_token", access_token, httponly=True, secure=True)
    return response

@auth.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"msg": f"Hello, {current_user}!"}), 200