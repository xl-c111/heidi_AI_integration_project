from flask import Blueprint, jsonify
from app.api.auth import get_jwt_token

main = Blueprint('auth_main', __name__)

@main.route('/')
def home():
    return 'Welcome to Heidi Hackathon!'

@main.route('/get-token')
def token():
    token = get_jwt_token()
    return jsonify({'jwt': token})