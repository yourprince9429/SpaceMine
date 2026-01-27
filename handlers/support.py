from flask import jsonify

from models import SupportEmail


def get_support_info():
    """获取客服邮箱信息"""
    try:
        support_emails = SupportEmail.query.filter_by(is_active=True).all()
        emails = [email.email for email in support_emails]

        return jsonify({"success": True, "emails": emails})
    except Exception:
        return jsonify({"success": True, "emails": []})
