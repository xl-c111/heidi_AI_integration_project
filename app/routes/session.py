from flask import Blueprint, jsonify, request
from app.api.auth import get_jwt_token
from app.api.session import create_session, get_session_details, update_session

session_bp = Blueprint('session', __name__)


@session_bp.route('', methods=['POST'])
def create():
    jwt_token = get_jwt_token()
    if not jwt_token:
        return jsonify({"error": "JWT token not found"}), 401

    session_id = create_session(jwt_token)
    if isinstance(session_id, dict) and session_id.get("error"):
        return jsonify(session_id), session_id.get("status_code", 500)

    return jsonify({"session_id": session_id}), 201


@session_bp.route('/<session_id>', methods=['GET'])
def details(session_id):
    jwt_token = get_jwt_token()
    if not jwt_token:
        return jsonify({"error": "JWT token not found"}), 401
   
    session_details = get_session_details( jwt_token,session_id)
    if isinstance(session_details, dict) and session_details.get("error"):
        return jsonify(session_details), session_details.get("status_code", 500)

    return jsonify(session_details), 200


@session_bp.route('/<session_id>', methods=['PATCH'])
def update_session_route(session_id):
    jwt_token = get_jwt_token()
    if not jwt_token:
        return jsonify({"error": "JWT token not found"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    updated_session = update_session(
        jwt_token=jwt_token,
        session_id=session_id,
        duration=data.get("duration"),
        language_code=data.get("language_code"),
        output_language_code=data.get("output_language_code"),
        patient=data.get("patient"),
        clinician_notes=data.get("clinician_notes"),
        generate_output_without_recording=data.get(
            "generate_output_without_recording")
    )
    if isinstance(updated_session, dict) and updated_session.get("error"):
        return jsonify(updated_session), updated_session.get("status_code", 500)

    return jsonify(updated_session), 200
