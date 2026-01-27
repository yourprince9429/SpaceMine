from flask import jsonify, request, session
from models import db, User, Withdrawal, Config
from handlers.auth import get_current_user
from handlers.security import verify_pay_password
from datetime import datetime
import uuid
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_withdrawal_history(limit=10):
    """获取用户提现记录"""
    user = get_current_user()
    if not user:
        logger.debug("用户未登录")
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        query = Withdrawal.query.filter_by(user_id=user.id).order_by(Withdrawal.created_at.desc())

        if limit:
            query = query.limit(limit)

        withdrawals = query.all()

        result = []
        for w in withdrawals:
            result.append(
                {
                    "id": w.id,
                    "amount": str(w.amount),
                    "address": w.address,
                    "status": w.status,
                    "created_at": w.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": (
                        w.updated_at.strftime("%Y-%m-%d %H:%M:%S") if w.updated_at else None
                    ),
                }
            )

        logger.debug(f"获取到用户 {user.id} 的提现记录: {len(result)} 条")
        return jsonify({"success": True, "list": result})

    except Exception as e:
        logger.error(f"获取提现记录失败: {str(e)}")
        return jsonify({"success": False, "error": "获取提现记录失败"}), 500


def apply_withdrawal():
    """申请提现"""
    user = get_current_user()
    if not user:
        logger.debug("用户未登录")
        return jsonify({"success": False, "message": "未登录"}), 401

    # 获取请求数据
    data = request.get_json()
    if not data:
        logger.debug("无效的请求数据")
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    amount = data.get("amount")
    withdrawal_method = data.get("withdrawal_method", "usdt")
    pay_password = data.get("pay_password")

    logger.debug(f"提现请求 - 用户ID: {user.id}, 金额: {amount}, 方式: {withdrawal_method}")

    # 验证基本参数
    if not amount or not pay_password:
        logger.debug("缺少必要参数")
        return jsonify({"success": False, "error": "缺少必要参数"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            logger.debug("提现金额必须大于0")
            return jsonify({"success": False, "error": "提现金额必须大于0"}), 400
    except ValueError:
        logger.debug("无效的提现金额")
        return jsonify({"success": False, "error": "无效的提现金额"}), 400

    # 检查最小提现金额
    min_withdrawal = 0.0001
    if amount < min_withdrawal:
        logger.debug(f"提现金额不能低于{min_withdrawal}能量")
        return (
            jsonify({"success": False, "error": f"提现金额不能低于{min_withdrawal}能量"}),
            400,
        )

    # 验证支付密码
    if not verify_pay_password(user.id, pay_password):
        logger.debug("支付密码错误")
        return jsonify({"success": False, "error": "支付密码错误"}), 400

    # 根据提现方式验证参数
    address = None
    bank_name = None
    bank_account = None
    bank_holder = None
    bank_code = None

    if withdrawal_method == "usdt":
        address = data.get("address")
        if not address:
            logger.debug("请输入提现地址")
            return jsonify({"success": False, "error": "请输入提现地址"}), 400
    elif withdrawal_method == "bank":
        bank_name = data.get("bank")
        bank_account = data.get("card")
        bank_holder = data.get("holder")
        bank_code = data.get("code")
        if not bank_name or not bank_account or not bank_holder or not bank_code:
            logger.debug("请填写完整的银行卡信息")
            return jsonify({"success": False, "error": "请填写完整的银行卡信息"}), 400
        # 银行卡提现时，将银行信息组合到address字段
        address = f"{bank_name}|{bank_account}|{bank_holder}"
    else:
        logger.debug("无效的提现方式")
        return jsonify({"success": False, "error": "无效的提现方式"}), 400

    # 检查用户余额
    try:
        logger.debug("开始检查用户余额")
        balance_response = get_user_balance()

        # 检查返回的是否为元组
        if isinstance(balance_response, tuple) and len(balance_response) == 2:
            response, status_code = balance_response
            logger.debug(f"余额响应状态码: {status_code}")

            if not status_code == 200:
                logger.debug(f"余额请求失败，响应: {response.get_json()}")
                return balance_response

            # 直接获取响应对象的JSON数据，避免双重解析
            if hasattr(response, "get_json"):
                balance_data = response.get_json()
            else:
                balance_data = response

            logger.debug(f"余额数据: {balance_data}")

            if not balance_data or not balance_data.get("success"):
                logger.debug("获取余额失败")
                return jsonify({"success": False, "error": "获取余额失败"}), 500

            available_balance = float(balance_data.get("balance", 0))
            logger.debug(f"可用余额: {available_balance}, 提现金额: {amount}")

            if available_balance < amount:
                logger.debug("余额不足")
                return jsonify({"success": False, "error": "余额不足"}), 400

            logger.debug("余额验证通过")
        else:
            # 如果不是元组，直接处理响应对象
            logger.debug(f"余额响应对象: {balance_response}")
            if hasattr(balance_response, "get_json"):
                balance_data = balance_response.get_json()
            else:
                balance_data = balance_response

            logger.debug(f"余额数据: {balance_data}")

            if not balance_data or not balance_data.get("success"):
                logger.debug("获取余额失败")
                return jsonify({"success": False, "error": "获取余额失败"}), 500

            available_balance = float(balance_data.get("balance", 0))
            logger.debug(f"可用余额: {available_balance}, 提现金额: {amount}")

            if available_balance < amount:
                logger.debug("余额不足")
                return jsonify({"success": False, "error": "余额不足"}), 400

            logger.debug("余额验证通过")

    except Exception as e:
        logger.error(f"余额验证失败: {str(e)}")
        return jsonify({"success": False, "error": "余额验证失败"}), 500

    # 创建提现记录
    try:
        logger.debug("开始创建提现记录")
        withdrawal = Withdrawal(
            user_id=user.id,
            amount=amount,
            address=address,
            withdrawal_method=withdrawal_method,
            status="pending",
            order_number=f"WD_{user.id}_{uuid.uuid4().hex[:8].upper()}",
            # 银行卡信息
            bank_name=bank_name,
            bank_account=bank_account,
            bank_holder=bank_holder,
            bank_code=bank_code,
        )

        db.session.add(withdrawal)
        db.session.commit()

        logger.debug(f"提现记录创建成功，ID: {withdrawal.id}")
        return jsonify(
            {
                "success": True,
                "message": "提现申请提交成功，请等待审核",
                "withdrawal_id": withdrawal.id,
            }
        )

    except Exception as e:
        logger.error(f"提现申请提交失败: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": "提现申请提交失败"}), 500


def get_user_balance():
    """获取用户余额"""
    user = get_current_user()
    if not user:
        logger.debug("用户未登录")
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        # 从数据库获取用户余额
        balance = user.get_balance()
        logger.debug(f"用户 {user.id} 余额: {balance}")

        return jsonify(
            {
                "success": True,
                "balance": str(balance),
                "usd_equivalent": str(balance),  # 1:1比例
            }
        )

    except Exception as e:
        logger.error(f"获取余额失败: {str(e)}")
        return jsonify({"success": False, "error": "获取余额失败"}), 500
