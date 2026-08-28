from functools import wraps

from flask import Blueprint, jsonify, request, session

from services.chat_service import get_response

chat_bp = Blueprint("chat", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "Authentication required."}), 401
        return view(*args, **kwargs)

    return wrapped


@chat_bp.post("/api/chat")
@login_required
def chat():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message")

    if not isinstance(message, str):
        return jsonify({"error": "Message must be a string."}), 400

    message = message.strip()

    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if len(message) > 2000:
        return jsonify({"error": "Message is too long."}), 400

    return jsonify({"answer": get_response(message)})