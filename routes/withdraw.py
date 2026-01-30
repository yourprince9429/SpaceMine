import traceback

from flask import Blueprint, jsonify, request

from handlers.auth import get_current_user
from handlers.withdraw import apply_withdrawal, get_user_balance, get_withdrawal_history
from models import Withdrawal

withdraw_bp = Blueprint("withdraw", __name__)


@withdraw_bp.route("/api/withdraw/history")
def withdrawal_history():
    """获取提现记录"""
    limit = int(request.args.get("limit", 10))
    return get_withdrawal_history(limit)


@withdraw_bp.route("/api/withdraw/apply", methods=["POST"])
def apply_withdraw():
    """申请提现"""
    return apply_withdrawal()


@withdraw_bp.route("/api/user/balance")
def user_balance():
    """获取用户余额"""
    return get_user_balance()


@withdraw_bp.route("/ui/api/withdraw/info")
def withdraw_info():
    """获取提现信息（用于前端页面）"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        # 获取用户能量
        available_food = user.get_energy()

        # 获取待审核提现数量
        pending_count = Withdrawal.query.filter_by(user_id=user.id, status="pending").count()

        return jsonify(
            {
                "success": True,
                "available_food": available_food,
                "mobile": user.phone or "",
                "pending_count": pending_count,
            }
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": "获取提现信息失败"}), 500


@withdraw_bp.route("/ui/api/withdraw/list")
def withdraw_list():
    """获取提现记录列表（用于前端页面）"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        status = request.args.get("status", "all")

        status_mapping = {"pending": "pending", "success": "completed", "fail": "failed"}

        query = Withdrawal.query.filter_by(user_id=user.id)

        if status != "all" and status in status_mapping:
            query = query.filter_by(status=status_mapping[status])

        withdrawals = query.order_by(Withdrawal.created_at.desc()).all()

        result = []
        for w in withdrawals:
            status_text = {
                "pending": "待审核",
                "processing": "处理中",
                "completed": "已完成",
                "failed": "失败",
            }.get(w.status, w.status)

            type_name = "USDT提现" if w.withdrawal_method == "usdt" else "银行卡提现"

            # 银行卡提现时，显示银行卡信息
            if w.withdrawal_method == "bank" and w.bank_name:
                address_display = f"{w.bank_name} ({w.bank_account})"
            else:
                address_display = w.address or ""

            result.append(
                {
                    "id": w.id,
                    "amount": str(w.amount),
                    "type_name": type_name,
                    "status": w.status,
                    "status_text": status_text,
                    "created_at": w.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": (
                        w.updated_at.strftime("%Y-%m-%d %H:%M:%S") if w.updated_at else None
                    ),
                    "address": address_display,
                }
            )

        return jsonify({"success": True, "list": result})

    except Exception as e:
        return jsonify({"success": False, "error": "获取提现记录失败"}), 500


@withdraw_bp.route("/ui/withdraw/usdt", methods=["POST"])
def withdraw_usdt():
    """提交USDT提现申请"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    address = data.get("address")
    network = data.get("network", "TRC20")
    amount = data.get("amount")
    pay_password = data.get("pay_password")

    if not address or not amount or not pay_password:
        return jsonify({"success": False, "error": "缺少必要参数"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"success": False, "error": "提现金额必须大于0"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "无效的提现金额"}), 400

    # 构造请求数据
    request_data = {
        "amount": amount,
        "withdrawal_method": "usdt",
        "pay_password": pay_password,
        "address": address,
    }

    # 使用现有的apply_withdrawal函数处理
    from flask import request as flask_request

    flask_request._get_data_string = lambda: str(request_data)
    flask_request.get_json = lambda: request_data

    return apply_withdrawal()


@withdraw_bp.route("/ui/withdraw/bank", methods=["POST"])
def withdraw_bank():
    """提交银行卡提现申请"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    holder = data.get("holder")
    card = data.get("card")
    bank = data.get("bank")
    code = data.get("code")
    amount = data.get("amount")
    pay_password = data.get("pay_password")

    if not holder or not card or not bank or not code or not amount or not pay_password:
        return jsonify({"success": False, "error": "缺少必要参数"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"success": False, "error": "提现金额必须大于0"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "无效的提现金额"}), 400

    # 构造请求数据
    request_data = {
        "amount": amount,
        "withdrawal_method": "bank",
        "pay_password": pay_password,
        "holder": holder,
        "card": card,
        "bank": bank,
        "code": code,
    }

    # 使用现有的apply_withdrawal函数处理
    from flask import request as flask_request

    flask_request._get_data_string = lambda: str(request_data)
    flask_request.get_json = lambda: request_data

    return apply_withdrawal()
