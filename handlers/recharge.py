import random
import re
import time
import traceback
import uuid

from flask import jsonify, request
from sqlalchemy import func

from handlers.auth import get_current_user
from models import Config, CreditCard, Notification, Recharge, User, db


def recharge_card():
    """信用卡充值接口"""
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    # 获取表单数据
    cardholder_name = request.form.get("cardholder_name", "").strip()
    card_number = request.form.get("card_number", "").strip()
    expiry_date = request.form.get("expiry_date", "").strip()
    cvv = request.form.get("cvv", "").strip()
    amount = request.form.get("amount", "").strip()

    # 1. 数据格式校验
    if not cardholder_name:
        return jsonify({"success": False, "message": "姓名格式不正確"}), 400

    # 检查姓名是否只包含英文字母
    if not cardholder_name.replace(" ", "").isalpha():
        return jsonify({"success": False, "message": "姓名格式不正確"}), 400

    if not card_number or not card_number.isdigit() or len(card_number) != 16:
        return jsonify({"success": False, "message": "卡號需為16位數字"}), 400

    if not expiry_date or not re.match(r"^\d{2}/\d{2}$", expiry_date):
        return jsonify({"success": False, "message": "有效期格式不正确"}), 400

    if not cvv or not cvv.isdigit() or len(cvv) != 3:
        return jsonify({"success": False, "message": "安全码需為3位數字"}), 400

    # 验证金额
    if not amount:
        return jsonify({"success": False, "message": "请输入充值金额"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"success": False, "message": "充值金额必须大于0"}), 400
    except ValueError:
        return jsonify({"success": False, "message": "充值金额格式不正确"}), 400

    try:
        # 2. 信用卡信息匹配
        credit_card = CreditCard.query.filter(
            CreditCard.cardholder_name == cardholder_name,
            CreditCard.card_number == card_number,
            CreditCard.expiry_date == expiry_date,
            CreditCard.security_code == cvv,
        ).first()
        if not credit_card:
            return (
                jsonify({"success": False, "message": "充值失敗 請聯繫發卡機構"}),
                400,
            )

        # 3. 状态校验
        if not credit_card.recharge_status:
            return (
                jsonify({"success": False, "message": "充值失敗 請聯繫發卡機構"}),
                400,
            )

        # 4. 充值金额校验
        max_recharge_config = Config.query.filter_by(key="max_credit_card_recharge").first()
        max_recharge_amount = float(max_recharge_config.value) if max_recharge_config else 10000.0
        if amount > max_recharge_amount:
            # 充值金额超限：更新信用卡状态为失败，创建充值记录
            credit_card.recharge_status = False
            transaction_id = f"TXN_{user.id}_{int(time.time())}_{uuid.uuid4().hex[:8].upper()}"
            recharge = Recharge(
                user_id=user.id,
                amount=amount,
                method="credit_card",
                status="failed",
                order_number=transaction_id,
                bank_card_id=credit_card.id,
            )
            db.session.add(recharge)
            db.session.commit()
            return (
                jsonify({"success": False, "message": "充值失敗 請聯繫發卡機構"}),
                400,
            )

        # 5. 充值次数与成功率控制
        recharge_count = credit_card.recharge_count

        # 根据充值次数确定使用哪次的成功率（次数+1）
        # 第1次(recharge_count=0) -> '1_recharge_success_rate'
        # 第2次(recharge_count=1) -> '2_recharge_success_rate'
        # 第3次(recharge_count=2) -> '3_recharge_success_rate'
        # 第4次(recharge_count=3) -> '4_recharge_success_rate'
        # 超过4次后信用卡状态会被设为失败，不会再次进入此逻辑

        if recharge_count < 4:
            # 动态拼接配置key：次数+1
            config_key = f"{recharge_count + 1}_recharge_success_rate"
            success_rate_config = Config.query.filter_by(key=config_key).first()
            success_rate = float(success_rate_config.value) if success_rate_config else 0.0
        else:
            # 理论上不会走到这里，因为超过4次后信用卡状态会被设为失败
            # 但为了安全起见，直接返回失败
            return (
                jsonify({"success": False, "message": "充值失敗 請聯繫發卡機構"}),
                400,
            )

        # 生成随机数进行概率判断
        random_num = random.random()
        is_success = random_num < success_rate

        # 生成交易流水号
        transaction_id = f"TXN_{user.id}_{int(time.time())}_{uuid.uuid4().hex[:8].upper()}"

        # 创建充值记录
        recharge = Recharge(
            user_id=user.id,
            amount=amount,
            method="credit_card",
            status="completed" if is_success else "failed",
            order_number=transaction_id,
            bank_card_id=credit_card.id,
        )
        db.session.add(recharge)

        if is_success:
            # 充值成功：更新用户余额和信用卡充值次数
            # 将 float 转换为 Decimal 以避免类型错误
            from decimal import Decimal

            user.balance += Decimal(str(amount))
            credit_card.recharge_count += 1
            db.session.commit()

            # 添加充值成功通知
            order_id = f"CARD{transaction_id}"
            card_number = credit_card.card_number
            notification = Notification(
                title="充值成功",
                content=f"訂單號：{order_id}\n金額：{amount:.2f}\n結果：充值成功到賬 {amount:.2f}\n卡號：{card_number}",
                user_id=user.id,
            )
            db.session.add(notification)
            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": "充值成功",
                    "transaction_id": transaction_id,
                }
            )
        else:
            # 充值失败：更新信用卡状态为失败，充值次数不变
            credit_card.recharge_status = False
            db.session.commit()

            # 添加充值失败通知
            order_id = f"CARD{transaction_id}"
            card_number = credit_card.card_number
            notification = Notification(
                title="充值審核不通過",
                content=f"訂單號：{order_id}\n金額：{amount:.2f}\n結果：充值失敗 請聯繫發卡機構\n卡號：{card_number}",
                user_id=user.id,
            )
            db.session.add(notification)
            db.session.commit()

            return (
                jsonify({"success": False, "message": "充值失敗 請聯繫發卡機構"}),
                400,
            )

    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"success": False, "message": "充值处理失败，请重试"}), 500


def get_recharges():
    """获取用户充值记录"""
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    # 获取查询参数
    status = request.args.get("status", "all")

    try:
        # 构建查询
        query = Recharge.query.filter_by(user_id=user.id)

        # 根据状态筛选
        if status != "all":
            query = query.filter_by(status=status)

        # 按创建时间倒序排列
        query = query.order_by(Recharge.created_at.desc())

        # 获取总数
        total_count = query.count()

        # 计算总金额（只计算成功的充值）
        total_amount = (
            db.session.query(func.sum(Recharge.amount))
            .filter(Recharge.user_id == user.id, Recharge.status == "completed")
            .scalar()
            or 0
        )

        # 获取分页数据（这里先获取所有数据，后续可以添加分页）
        recharges = query.all()

        # 格式化数据
        recharge_list = []
        for recharge in recharges:
            # 获取银行卡信息
            bank_card = recharge.bank_card
            type_name = "銀行卡充值" if bank_card else "充值"
            recharge_type = "CARD" if bank_card else "OTHER"

            recharge_list.append(
                {
                    "id": recharge.id,
                    "order_id": recharge.order_number,
                    "type": recharge_type,
                    "type_name": type_name,
                    "amount": str(recharge.amount),
                    "actual_amount": str(recharge.amount),  # 实际到账金额与充值金额相同
                    "status": recharge.status,
                    "status_text": (
                        "成功"
                        if recharge.status == "completed"
                        else ("失败" if recharge.status == "failed" else "待處理")
                    ),
                    "created_at": (
                        recharge.created_at.strftime("%Y-%m-%d %H:%M:%S")
                        if recharge.created_at
                        else ""
                    ),
                    "method": recharge.method,
                }
            )

        return jsonify(
            {
                "success": True,
                "total_amount": float(total_amount),
                "total_count": total_count,
                "list": recharge_list,
            }
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": "获取充值记录失败"}), 500
