from datetime import datetime

from flask import jsonify, request
from sqlalchemy import func

from handlers.auth import get_current_user
from handlers.scheduler import check_and_settle_user_mines
from models import MineUserRelation, MiningRule, db


def get_user_mines():
    """获取用户矿场列表"""
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    check_and_settle_user_mines(user.id)

    active_mines = MineUserRelation.query.filter(
        MineUserRelation.user_id == user.id, MineUserRelation.is_active == True
    ).subquery()

    query = (
        db.session.query(
            MiningRule.id,
            MiningRule.code,
            MiningRule.name,
            MiningRule.miners_consumed,
            MiningRule.cycle_days,
            MiningRule.energy_reward,
            MiningRule.background_image,
            active_mines.c.id.label("relation_id"),
            active_mines.c.created_at.label("activated_at"),
        )
        .outerjoin(
            active_mines,
            MiningRule.id == active_mines.c.mine_id,
        )
        .all()
    )

    mines = []
    current_time = datetime.utcnow()

    for row in query:
        is_activated = row.relation_id is not None
        activated_duration = None
        energy_per_second = 0.0
        total_generated_energy = 0.0

        if is_activated and row.activated_at:
            duration = current_time - row.activated_at
            activated_duration = int(duration.total_seconds())

            cycle_seconds = row.cycle_days * 24 * 3600
            if cycle_seconds > 0:
                energy_per_second = float(row.energy_reward) / cycle_seconds

            total_generated_energy = energy_per_second * activated_duration
        else:
            activated_duration = 0
            energy_per_second = 0.0
            total_generated_energy = 0.0

        mine_data = {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "miners_consumed": row.miners_consumed,
            "cycle_days": row.cycle_days,
            "energy_reward": f"{row.energy_reward:.4f}",
            "background_image": row.background_image,
            "is_activated": is_activated,
            "activated_duration": activated_duration,
            "energy_per_second": f"{energy_per_second:.8f}",
            "total_generated_energy": f"{total_generated_energy:.4f}",
        }
        mines.append(mine_data)

    return jsonify({"success": True, "mines": mines})


def open_mine():
    """开放矿场"""
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    try:
        data = request.get_json()
        type_code = data.get("type_code")

        if not type_code:
            response = jsonify({"success": False, "message": "缺少矿场类型代码"})
            response.status_code = 400
            return response

        mining_rule = MiningRule.query.filter_by(code=type_code).first()
        if not mining_rule:
            response = jsonify({"success": False, "message": "矿场类型不存在"})
            response.status_code = 404
            return response

        existing_relation = MineUserRelation.query.filter_by(
            user_id=user.id, mine_id=mining_rule.id, is_active=True
        ).first()

        if existing_relation:
            response = jsonify({"success": False, "message": "该类型已在挖礦"})
            response.status_code = 400
            return response

        user_balance = float(user.get_balance())
        miners_consumed = float(mining_rule.miners_consumed)

        if user_balance < miners_consumed:
            response = jsonify({"success": False, "message": "礦工數不足"})
            response.status_code = 400
            return response

        user.balance = user_balance - miners_consumed

        relation = MineUserRelation(
            user_id=user.id, mine_id=mining_rule.id, mine_code=mining_rule.code, is_active=True
        )

        db.session.add(relation)
        db.session.commit()

        return jsonify({"success": True, "message": "開啟成功"})
    except Exception as e:
        db.session.rollback()
        response = jsonify({"success": False, "message": f"操作失敗: {str(e)}"})
        response.status_code = 500
        return response
