from datetime import datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request

from handlers.auth import get_current_user
from models import User, Withdrawal, db, Notification
from sqlalchemy import or_

withdrawal_bp = Blueprint("admin_withdrawals", __name__)


@withdrawal_bp.route("/api/admin/withdrawals")
def get_withdrawals():
    """获取提现记录列表"""
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
    withdrawal_method = request.args.get("withdrawal_method")
    user_id = request.args.get("user_id")
    username = request.args.get("username")
    search = request.args.get("search")

    query = Withdrawal.query

    if status:
        query = query.filter_by(status=status)

    if withdrawal_method:
        query = query.filter_by(withdrawal_method=withdrawal_method)

    if user_id:
        query = query.filter_by(user_id=int(user_id))

    if username:
        query = query.join(User).filter(User.username.like(f"%{username}%"))

    if search:
        query = query.join(User).filter(
            or_(User.username.like(f"%{search}%"), Withdrawal.order_number.like(f"%{search}%"))
        )

    withdrawals_query = query.order_by(Withdrawal.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    withdrawals_data = []
    for withdrawal in withdrawals_query.items:
        user_info = withdrawal.user

        if withdrawal.withdrawal_method == "bank" and withdrawal.bank_name:
            address_display = f"{withdrawal.bank_name} ({withdrawal.bank_account})"
        else:
            address_display = withdrawal.address or ""

        reviewer_name = withdrawal.reviewer.username if withdrawal.reviewer else None

        withdrawals_data.append(
            {
                "id": withdrawal.id,
                "user_id": withdrawal.user_id,
                "username": user_info.username,
                "amount": float(withdrawal.amount),
                "withdrawal_method": withdrawal.withdrawal_method,
                "withdrawal_method_text": (
                    "USDT提现" if withdrawal.withdrawal_method == "usdt" else "银行卡提现"
                ),
                "status": withdrawal.status,
                "status_text": {
                    "pending": "待审核",
                    "processing": "处理中",
                    "completed": "已通过",
                    "failed": "失败",
                }.get(withdrawal.status, withdrawal.status),
                "order_number": withdrawal.order_number,
                "address": address_display,
                "created_at": withdrawal.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": (
                    withdrawal.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                    if withdrawal.updated_at
                    else None
                ),
                "reviewer_name": reviewer_name,
            }
        )

    return jsonify(
        {
            "success": True,
            "withdrawals": withdrawals_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": withdrawals_query.total,
                "pages": withdrawals_query.pages,
            },
        }
    )


@withdrawal_bp.route("/api/admin/withdrawals/<int:withdrawal_id>")
def get_withdrawal_detail(withdrawal_id):
    """获取提现详情"""
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

    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    user_info = withdrawal.user

    if withdrawal.withdrawal_method == "bank" and withdrawal.bank_name:
        address_display = f"{withdrawal.bank_name} ({withdrawal.bank_account})"
    else:
        address_display = withdrawal.address or ""

    return jsonify(
        {
            "success": True,
            "withdrawal": {
                "id": withdrawal.id,
                "user_id": withdrawal.user_id,
                "username": user_info.username,
                "email": user_info.email,
                "phone": user_info.phone or "",
                "amount": float(withdrawal.amount),
                "withdrawal_method": withdrawal.withdrawal_method,
                "withdrawal_method_text": (
                    "USDT提现" if withdrawal.withdrawal_method == "usdt" else "银行卡提现"
                ),
                "status": withdrawal.status,
                "status_text": {
                    "pending": "待审核",
                    "processing": "处理中",
                    "completed": "已通过",
                    "failed": "失败",
                }.get(withdrawal.status, withdrawal.status),
                "order_number": withdrawal.order_number,
                "address": address_display,
                "bank_name": withdrawal.bank_name,
                "bank_account": withdrawal.bank_account,
                "bank_holder": withdrawal.bank_holder,
                "bank_code": withdrawal.bank_code,
                "created_at": withdrawal.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": (
                    withdrawal.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                    if withdrawal.updated_at
                    else None
                ),
                "notes": withdrawal.notes,
                "user_energy": float(user_info.energy),
            },
        }
    )


@withdrawal_bp.route("/api/admin/withdrawals/<int:withdrawal_id>/review", methods=["PUT"])
def review_withdrawal(withdrawal_id):
    """审核提现"""
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

    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)

    if withdrawal.status != "pending":
        return jsonify({"success": False, "message": "该提现记录不在待审核状态"}), 400

    data = request.get_json()
    new_status = data.get("status")
    notes = data.get("notes", "")

    if new_status not in ["completed", "failed"]:
        return jsonify({"success": False, "message": "无效的审核结果"}), 400

    try:
        withdrawal.status = new_status
        withdrawal.notes = notes
        withdrawal.updated_at = datetime.utcnow()
        withdrawal.reviewer_id = user.id

        if new_status == "completed":
            user_info = withdrawal.user
            if user_info.energy < Decimal(str(withdrawal.amount)):
                return (
                    jsonify({"success": False, "message": "用户能量不足，无法完成提现"}),
                    400,
                )

            user_info.energy -= Decimal(str(withdrawal.amount))
            if user_info.energy < 0:
                user_info.energy = 0

            # 添加提现审核通过通知
            notification = Notification(
                title="提現結果",
                content=f"提現審核通過，已處理 {withdrawal.amount:.2f}",
                user_id=withdrawal.user_id,
            )
            db.session.add(notification)
        else:
            # 添加提现审核不通过通知
            notification = Notification(
                title="提現結果", content="提現審核不通過", user_id=withdrawal.user_id
            )
            db.session.add(notification)

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "审核完成",
                "withdrawal": {
                    "id": withdrawal.id,
                    "status": withdrawal.status,
                    "updated_at": withdrawal.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
        )

    except Exception:
        db.session.rollback()
        import traceback

        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({"success": False, "message": "审核失败"}), 500


@withdrawal_bp.route("/api/admin/withdrawals/statistics")
def get_withdrawal_statistics():
    """获取提现统计数据"""
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
        from sqlalchemy import func
        from datetime import datetime, timedelta

        total_withdrawals = Withdrawal.query.count()
        pending_withdrawals = Withdrawal.query.filter_by(status="pending").count()
        processing_withdrawals = Withdrawal.query.filter_by(status="processing").count()
        completed_withdrawals = Withdrawal.query.filter_by(status="completed").count()
        failed_withdrawals = Withdrawal.query.filter_by(status="failed").count()

        usdt_withdrawals = Withdrawal.query.filter_by(withdrawal_method="usdt").count()
        bank_withdrawals = Withdrawal.query.filter_by(withdrawal_method="bank").count()

        today = datetime.utcnow().date()
        today_withdrawals = Withdrawal.query.filter(
            func.date(Withdrawal.created_at) == today
        ).count()

        completed_amount = (
            db.session.query(db.func.sum(Withdrawal.amount)).filter_by(status="completed").scalar()
            or 0
        )

        return jsonify(
            {
                "success": True,
                "statistics": {
                    "by_status": {
                        "pending": pending_withdrawals,
                        "processing": processing_withdrawals,
                        "completed": completed_withdrawals,
                        "failed": failed_withdrawals,
                    },
                    "by_method": {
                        "usdt": usdt_withdrawals,
                        "bank": bank_withdrawals,
                    },
                    "by_time": {
                        "today": today_withdrawals,
                    },
                    "amount_by_status": {
                        "completed": float(completed_amount),
                    },
                },
            }
        )
    except Exception:
        import traceback

        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({"success": False, "message": "获取统计数据失败"}), 500
