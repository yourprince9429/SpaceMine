import traceback

from flask import Blueprint, jsonify, request, Response
from sqlalchemy import or_

from handlers.auth import get_current_user
from models import File, Notification, Recharge, db

recharge_bp = Blueprint("admin_recharges", __name__)


@recharge_bp.route("/api/admin/recharges")
def get_recharges():
    """获取所有USDT充值记录"""
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

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")
    search = request.args.get("search")

    try:
        query = Recharge.query.filter_by(method="usdt")

        if status:
            query = query.filter_by(status=status)

        if search:
            from models import User

            query = query.join(User, Recharge.user_id == User.id).filter(
                or_(User.username.like(f"%{search}%"), Recharge.order_number.like(f"%{search}%"))
            )

        recharges_query = query.order_by(Recharge.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        recharges_data = []
        for recharge in recharges_query.items:
            reviewer_name = recharge.reviewer.username if recharge.reviewer else None
            recharges_data.append(
                {
                    "id": recharge.id,
                    "user_id": recharge.user_id,
                    "username": recharge.user.username,
                    "amount": float(recharge.amount),
                    "status": recharge.status,
                    "order_number": recharge.order_number,
                    "created_at": recharge.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "reviewer_name": reviewer_name,
                }
            )

        return jsonify(
            {
                "success": True,
                "recharges": recharges_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": recharges_query.total,
                    "pages": recharges_query.pages,
                },
            }
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


@recharge_bp.route("/api/admin/recharges/<int:recharge_id>")
def get_recharge_detail(recharge_id):
    """获取充值详情"""
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

    recharge = Recharge.query.get_or_404(recharge_id)

    return jsonify(
        {
            "success": True,
            "recharge": {
                "id": recharge.id,
                "user_id": recharge.user_id,
                "username": recharge.user.username,
                "amount": float(recharge.amount),
                "status": recharge.status,
                "order_number": recharge.order_number,
                "created_at": recharge.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "screenshot_file_id": recharge.screenshot_file_id,
            },
        }
    )


@recharge_bp.route("/api/admin/recharges/<int:recharge_id>/screenshot")
def get_recharge_screenshot(recharge_id):
    """获取充值截图"""
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

    recharge = Recharge.query.get_or_404(recharge_id)

    if not recharge.screenshot_file_id:
        return jsonify({"success": False, "message": "没有充值截图"}), 404

    file = File.query.get_or_404(recharge.screenshot_file_id)

    return Response(
        file.file_data,
        mimetype=(
            file.file_data[:4].decode("latin1") if file.file_data else "application/octet-stream"
        ),
    )


@recharge_bp.route("/api/admin/recharges/<int:recharge_id>/review", methods=["PUT"])
def review_recharge(recharge_id):
    """审核充值"""
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

    recharge = Recharge.query.get_or_404(recharge_id)

    if recharge.status in ["completed", "failed"]:
        return jsonify({"success": False, "message": "该充值记录已处理"}), 400

    data = request.get_json()
    status = data.get("status")

    if status not in ["completed", "failed"]:
        return jsonify({"success": False, "message": "无效的审核结果"}), 400

    try:
        recharge.status = status
        recharge.reviewer_id = user.id

        if status == "completed":
            recharge.user.balance += recharge.amount

            notification = Notification(
                title="充值成功",
                content=f"訂單號：{recharge.order_number}\n金額：{recharge.amount:.2f}\n結果：充值成功到賬 {recharge.amount:.2f}\n方式：USDT充值",
                user_id=recharge.user_id,
            )
            db.session.add(notification)
        else:
            notification = Notification(
                title="充值審核不通過",
                content=f"訂單號：{recharge.order_number}\n金額：{recharge.amount:.2f}\n結果：充值失敗 請聯繫發卡機構\n方式：USDT充值",
                user_id=recharge.user_id,
            )
            db.session.add(notification)

        db.session.commit()
        return jsonify({"success": True, "message": "审核完成"})
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"success": False, "message": "审核失败"}), 500
