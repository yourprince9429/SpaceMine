from flask import Blueprint, jsonify, request

from handlers.auth import get_current_user
from models import SupportEmail, db

support_bp = Blueprint("admin_support", __name__)


@support_bp.route("/api/admin/support-emails")
def get_support_emails():
    """获取所有客服邮箱"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    from models import Role, UserRoleRelation

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    emails = SupportEmail.query.all()

    emails_data = []
    for email in emails:
        emails_data.append(
            {
                "id": email.id,
                "email": email.email,
                "name": email.name,
                "is_active": email.is_active,
            }
        )

    return jsonify({"success": True, "emails": emails_data})


@support_bp.route("/api/admin/support-emails/<int:email_id>", methods=["PUT"])
def update_support_email(email_id):
    """更新客服邮箱"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    from models import Role, UserRoleRelation

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    data = request.get_json()
    new_email = data.get("email")
    new_name = data.get("name")

    if not new_email:
        return jsonify({"success": False, "message": "邮箱不能为空"}), 400

    try:
        support_email = SupportEmail.query.get_or_404(email_id)
        support_email.email = new_email
        support_email.name = new_name

        db.session.commit()
        return jsonify({"success": True, "message": "客服信息更新成功"})
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "更新失败"}), 500


@support_bp.route("/api/admin/support-emails/<int:email_id>/toggle", methods=["PUT"])
def toggle_support_email(email_id):
    """切换客服邮箱状态"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    from models import Role, UserRoleRelation

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    try:
        support_email = SupportEmail.query.get_or_404(email_id)
        support_email.is_active = not support_email.is_active

        db.session.commit()
        return jsonify({"success": True, "message": "状态更新成功"})
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "更新失败"}), 500
