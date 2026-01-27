from flask import Blueprint, jsonify, request

from handlers.auth import get_current_user
from models import Role, UserRoleRelation, User, db

user_bp = Blueprint("admin_users", __name__)


@user_bp.route("/api/admin/users")
def get_users():
    """获取所有用户列表"""
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

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    users_query = User.query.paginate(page=page, per_page=per_page, error_out=False)

    users_data = []
    for user in users_query.items:
        roles = []
        is_admin = False
        relations = UserRoleRelation.query.filter_by(user_id=user.id).all()
        for relation in relations:
            roles.append(relation.role.name)
            if relation.role.name == "admin":
                is_admin = True

        users_data.append(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "invite_code": user.invite_code,
                "status": user.status,
                "roles": roles,
                "is_admin": is_admin,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    return jsonify(
        {
            "success": True,
            "users": users_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": users_query.total,
                "pages": users_query.pages,
            },
        }
    )


@user_bp.route("/api/admin/users/<int:user_id>/status", methods=["PUT"])
def update_user_status(user_id):
    """更新用户状态"""
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

    if user_id == user.id:
        return jsonify({"success": False, "message": "不能修改自己的状态"}), 400

    target_user = User.query.get_or_404(user_id)

    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["active", "inactive"]:
        return jsonify({"success": False, "message": "无效的状态值"}), 400

    try:
        target_user.status = new_status
        db.session.commit()
        return jsonify({"success": True, "message": "用户状态更新成功"})
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "更新失败"}), 500


@user_bp.route("/api/admin/users/<int:user_id>/role", methods=["PUT"])
def update_user_role(user_id):
    """更新用户角色"""
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

    if user_id == user.id:
        return jsonify({"success": False, "message": "不能修改自己的角色"}), 400

    target_user = User.query.get_or_404(user_id)

    data = request.get_json()
    action = data.get("action")

    if action not in ["add_admin", "remove_admin"]:
        return jsonify({"success": False, "message": "无效的操作"}), 400

    try:
        admin_role = Role.query.filter_by(name="admin").first()
        if not admin_role:
            return jsonify({"success": False, "message": "管理员角色未配置"}), 500

        if action == "add_admin":
            existing_relation = UserRoleRelation.query.filter_by(
                user_id=target_user.id, role_id=admin_role.id
            ).first()

            if not existing_relation:
                user_role_relation = UserRoleRelation(user_id=target_user.id, role_id=admin_role.id)
                db.session.add(user_role_relation)
                db.session.commit()
                return jsonify({"success": True, "message": "已添加管理员权限"})
            else:
                return jsonify({"success": False, "message": "用户已经是管理员"})
        else:
            user_role_relation = UserRoleRelation.query.filter_by(
                user_id=target_user.id, role_id=admin_role.id
            ).first()

            if user_role_relation:
                db.session.delete(user_role_relation)
                db.session.commit()
                return jsonify({"success": True, "message": "已移除管理员权限"})
            else:
                return jsonify({"success": False, "message": "用户不是管理员"})

    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "操作失败"}), 500
