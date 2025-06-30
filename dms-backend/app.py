# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token
)
from db import db

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'your-very-secret-key-here'  # Change for production
jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "Missing username or password"}), 400

    try:
        user_id = db.create_user(
            username=data['username'],
            password=data['password'],
            role=data.get('role', 'user')
        )
        return jsonify({
            "msg": "User registered successfully",
            "user_id": user_id
        }), 201
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "Missing username or password"}), 400

    user = db.get_user_by_username(data['username'])
    if not user or not db.verify_password(user['password_hash'], data['password']):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity={
        "id": user['id'],
        "role": user['role'],
        "username": user['username']
    })
    return jsonify(access_token=access_token), 200

# Comment out document-related routes for login testing
"""
@app.route('/upload', methods=['POST'])
def upload():
    pass

@app.route('/documents', methods=['GET'])
def documents():
    pass
"""

if __name__ == '__main__':
    app.run(debug=True)