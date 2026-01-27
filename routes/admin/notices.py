from flask import Blueprint, jsonify, request

from handlers.auth import get_current_user
from handlers.notice import create_notice, delete_notice, get_notices
from models import Role, UserRoleRelation

notice_bp = Blueprint("admin_notices", __name__)


@notice_bp.route("/api/admin/notices", methods=["GET"])
def get_admin_notices():
    """获取所有公告列表"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    return get_notices()


@notice_bp.route("/api/admin/notices", methods=["POST"])
def create_admin_notice():
    """创建新公告"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    return create_notice()


@notice_bp.route("/api/admin/notices/<int:notice_id>", methods=["DELETE"])
def delete_admin_notice(notice_id):
    """删除公告"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    return delete_notice(notice_id)
