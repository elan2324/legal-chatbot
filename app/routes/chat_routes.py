from flask import Blueprint, jsonify
from flask_login import login_required, current_user

from app.models.chat_model import (
    create_conversation,
    get_user_conversations,
    get_messages
)

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat/new", methods=["POST"])
@login_required
def new_chat():
    cid = create_conversation(current_user.id)

    return jsonify({
        "conversation_id": cid
    })


@chat_bp.route("/chat/history")
@login_required
def history():
    return jsonify(get_user_conversations(current_user.id))


@chat_bp.route("/chat/<int:conversation_id>")
@login_required
def conversation(conversation_id):
    return jsonify(get_messages(conversation_id))