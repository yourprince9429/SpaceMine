from flask import Blueprint, jsonify, render_template

from .credit_cards import credit_card_bp
from .configs import config_bp
from .notices import notice_bp
from .recharges import recharge_bp
from .support import support_bp
from .users import user_bp
from .withdrawals import withdrawal_bp

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
def admin():
    """管理员页面"""
    from handlers.auth import get_current_user
    from models import Role, UserRoleRelation

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

    return render_template("admin.html")


admin_bp.register_blueprint(user_bp)
admin_bp.register_blueprint(recharge_bp)
admin_bp.register_blueprint(config_bp)
admin_bp.register_blueprint(support_bp)
admin_bp.register_blueprint(credit_card_bp)
admin_bp.register_blueprint(withdrawal_bp)
admin_bp.register_blueprint(notice_bp)
