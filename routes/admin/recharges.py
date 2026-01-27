from flask import Blueprint, jsonify, request, Response

from handlers.auth import get_current_user
from models import File, Recharge, db, Notification
from sqlalchemy import or_

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

    query = Recharge.query.filter_by(method="usdt")

    if status:
        query = query.filter_by(status=status)

    if search:
        from models import User

        query = query.join(User).filter(
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
    print(f"[DEBUG] 开始审核充值，recharge_id: {recharge_id}")

    user = get_current_user()
    if not user:
        print(f"[DEBUG] 用户未登录")
        return jsonify({"success": False, "message": "未登录"}), 401

    from models import Role, UserRoleRelation

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        print(f"[DEBUG] 管理员角色未配置")
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        print(f"[DEBUG] 权限不足，user_id: {user.id}")
        return jsonify({"success": False, "message": "权限不足"}), 403

    print(f"[DEBUG] 查询充值记录，recharge_id: {recharge_id}")
    recharge = Recharge.query.get_or_404(recharge_id)
    print(f"[DEBUG] 找到充值记录，status: {recharge.status}, amount: {recharge.amount}")

    if recharge.status in ["completed", "failed"]:
        print(f"[DEBUG] 充值记录已处理，status: {recharge.status}")
        return jsonify({"success": False, "message": "该充值记录已处理"}), 400

    print(f"[DEBUG] 获取请求数据")
    data = request.get_json()
    print(f"[DEBUG] 请求数据: {data}")
    status = data.get("status")
    print(f"[DEBUG] 审核状态: {status}")

    if status not in ["completed", "failed"]:
        print(f"[DEBUG] 无效的审核结果: {status}")
        return jsonify({"success": False, "message": "无效的审核结果"}), 400

    try:
        print(f"[DEBUG] 开始更新充值状态")
        recharge.status = status
        recharge.reviewer_id = user.id

        if status == "completed":
            print(
                f"[DEBUG] 更新用户余额，当前余额: {recharge.user.balance}, 增加: {recharge.amount}"
            )
            recharge.user.balance += recharge.amount
            print(f"[DEBUG] 更新后余额: {recharge.user.balance}")

            # 添加充值成功通知
            print(f"[DEBUG] 创建充值成功通知")
            notification = Notification(
                title="充值成功",
                content=f"訂單號：{recharge.order_number}\n金額：{recharge.amount:.2f}\n結果：充值成功到賬 {recharge.amount:.2f}\n方式：USDT充值",
                user_id=recharge.user_id,
            )
            db.session.add(notification)
        else:
            # 添加充值失败通知
            print(f"[DEBUG] 创建充值失败通知")
            notification = Notification(
                title="充值審核不通過",
                content=f"訂單號：{recharge.order_number}\n金額：{recharge.amount:.2f}\n結果：充值失敗 請聯繫發卡機構\n方式：USDT充值",
                user_id=recharge.user_id,
            )
            db.session.add(notification)

        print(f"[DEBUG] 提交数据库事务")
        db.session.commit()
        print(f"[DEBUG] 审核完成")
        return jsonify({"success": True, "message": "审核完成"})
    except Exception as e:
        print(f"[DEBUG] 审核失败，错误: {e}")
        import traceback

        traceback.print_exc()
        db.session.rollback()
        return jsonify({"success": False, "message": "审核失败"}), 500
