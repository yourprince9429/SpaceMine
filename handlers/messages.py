from flask import jsonify, session

from models import Notification, db


def get_unread_messages():
    """获取未读消息"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "error": "未登录"}), 401

        messages = (
            Notification.query.filter_by(user_id=user_id, is_read=False)
            .order_by(Notification.created_at.desc())
            .all()
        )

        return jsonify({"success": True, "list": [message.to_dict() for message in messages]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def get_all_messages():
    """获取所有消息"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "error": "未登录"}), 401

        messages = (
            Notification.query.filter_by(user_id=user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

        return jsonify({"success": True, "messages": [message.to_dict() for message in messages]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def get_message_detail(message_id):
    """获取消息详情"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "error": "未登录"}), 401

        message = Notification.query.filter_by(id=message_id, user_id=user_id).first()

        if not message:
            return jsonify({"success": False, "error": "消息不存在"}), 404

        return jsonify({"success": True, "message": message.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def mark_message_as_read(message_id):
    """标记消息为已读"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "error": "未登录"}), 401

        message = Notification.query.filter_by(id=message_id, user_id=user_id).first()

        if not message:
            return jsonify({"success": False, "error": "消息不存在"}), 404

        message.is_read = True
        db.session.commit()

        return jsonify({"success": True, "message": "已标记为已读"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
