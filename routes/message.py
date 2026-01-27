from flask import Blueprint

from handlers.messages import (
    get_all_messages,
    get_message_detail,
    get_unread_messages,
    mark_message_as_read,
)

message_bp = Blueprint("message", __name__)


@message_bp.route("/api/messages")
def messages():
    return get_all_messages()


@message_bp.route("/api/messages/unread")
def unread_messages():
    return get_unread_messages()


@message_bp.route("/api/messages/<int:message_id>")
def message_detail(message_id):
    return get_message_detail(message_id)


@message_bp.route("/api/messages/<int:message_id>/read", methods=["POST"])
def mark_as_read(message_id):
    return mark_message_as_read(message_id)
