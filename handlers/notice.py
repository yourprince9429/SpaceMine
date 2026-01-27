from flask import jsonify, request

from handlers.auth import get_current_user
from models import Notice, db


def get_notices():
    """获取公告列表"""
    try:
        from models import User

        notices = Notice.query.order_by(Notice.created_at.desc()).all()
        notices_data = []
        for notice in notices:
            user = User.query.get(notice.user_id)
            notice_dict = notice.to_dict()
            notice_dict["username"] = user.username if user else "未知用户"
            notices_data.append(notice_dict)
        return jsonify({"success": True, "notices": notices_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def create_notice():
    """创建新公告"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "error": "未登录"}), 401

        data = request.get_json()

        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return jsonify({"success": False, "error": "标题和内容不能为空"}), 400

        notice = Notice(title=title, content=content, user_id=user.id)
        db.session.add(notice)
        db.session.commit()

        return jsonify({"success": True, "message": "公告创建成功", "notice": notice.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


def delete_notice(notice_id):
    """删除公告"""
    try:
        notice = Notice.query.get(notice_id)
        if not notice:
            return jsonify({"success": False, "error": "公告不存在"}), 404

        db.session.delete(notice)
        db.session.commit()

        return jsonify({"success": True, "message": "公告删除成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
