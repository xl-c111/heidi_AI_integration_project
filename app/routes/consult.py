from flask import Blueprint, jsonify
from app.api.consult import  generate_consult_note
from app.api.auth import get_jwt_token

main = Blueprint('consult_main', __name__)


@main.route('/generate-note', methods=['POST'])
def generate_note():
    jwt = get_jwt_token()

    if not jwt or "Error" in jwt or "Exception" in jwt:
        return jsonify({"error": "Failed to retrieve JWT", "detail": jwt}), 400

    result = generate_consult_note(jwt)
    return jsonify(result)
