from datetime import datetime

from flask import jsonify

from handlers.auth import get_current_user
from handlers.scheduler import check_and_settle_user_mines
from models import MineUserRelation, MiningRule, db


def get_user_balance():
    """获取用户余额和总能量"""
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    check_and_settle_user_mines(user.id)

    try:
        user_energy = float(user.get_energy())

        query = (
            db.session.query(
                MiningRule.id,
                MiningRule.cycle_days,
                MiningRule.energy_reward,
                MineUserRelation.created_at.label("activated_at"),
                MineUserRelation.is_active,
            )
            .join(
                MineUserRelation,
                (MiningRule.id == MineUserRelation.mine_id)
                & (MineUserRelation.user_id == user.id)
                & (MineUserRelation.is_active == True),
            )
            .all()
        )

        current_time = datetime.utcnow()
        mine_energy = 0.0

        for row in query:
            if row.activated_at and row.is_active:
                duration = current_time - row.activated_at
                activated_duration = int(duration.total_seconds())

                cycle_seconds = row.cycle_days * 24 * 3600
                if cycle_seconds > 0:
                    energy_per_second = float(row.energy_reward) / cycle_seconds
                    total_generated_energy = energy_per_second * activated_duration
                    mine_energy += total_generated_energy

        total_energy = user_energy + mine_energy

        return jsonify(
            {
                "success": True,
                "balance": f"{user.get_balance():.4f}",
                "energy": f"{total_energy:.4f}",
                "user_energy": f"{user_energy:.4f}",
                "mine_energy": f"{mine_energy:.4f}",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"获取余额失败: {str(e)}"}), 500
