from flask import Blueprint, jsonify, request, current_app

from handlers.auth import get_current_user
from models import Config, db

config_bp = Blueprint("admin_configs", __name__)


@config_bp.route("/api/admin/configs")
def get_configs():
    """获取所有配置"""
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

    configs = Config.query.all()

    configs_data = []
    for config in configs:
        username = config.user.username if config.user else "系统"
        configs_data.append(
            {
                "key": config.key,
                "value": config.value,
                "description": config.description,
                "username": username,
            }
        )

    return jsonify({"success": True, "configs": configs_data})


@config_bp.route("/api/admin/configs/<key>", methods=["PUT"])
def update_config(key):
    """更新配置"""
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
    new_value = data.get("value")

    if not new_value:
        return jsonify({"success": False, "message": "配置值不能为空"}), 400

    try:
        config = Config.query.filter_by(key=key).first()
        if config:
            config.value = new_value
            config.user_id = user.id
        else:
            config = Config(key=key, value=new_value, user_id=user.id)
            db.session.add(config)

        db.session.commit()

        if key == "mine_settlement_interval_minutes":
            from handlers.scheduler import update_scheduler_interval

            with current_app.app_context():
                new_scheduler = update_scheduler_interval(current_app)
                if new_scheduler:
                    print(f"[DEBUG] 调度器更新成功")

        return jsonify({"success": True, "message": "配置更新成功"})
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "更新失败"}), 500
