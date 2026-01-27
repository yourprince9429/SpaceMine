import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, MiningRule


def init_mining_rules():
    rules = [
        {
            "code": "basic",
            "name": "初始矿场",
            "miners_consumed": 100,
            "cycle_days": 5,
            "energy_reward": 110.0,
            "background_image": "k1.png",
        },
        {
            "code": "small",
            "name": "小型矿场",
            "miners_consumed": 500,
            "cycle_days": 9,
            "energy_reward": 600.0,
            "background_image": "k2.png",
        },
        {
            "code": "medium",
            "name": "中型矿场",
            "miners_consumed": 6000,
            "cycle_days": 21,
            "energy_reward": 8900.0,
            "background_image": "k3.png",
        },
        {
            "code": "large",
            "name": "大型矿场",
            "miners_consumed": 21000,
            "cycle_days": 45,
            "energy_reward": 41900.0,
            "background_image": "k4.png",
        },
        {
            "code": "xlarge",
            "name": "超大型矿场",
            "miners_consumed": 60000,
            "cycle_days": 60,
            "energy_reward": 186000.0,
            "background_image": "k5.png",
        },
    ]

    with app.app_context():
        for rule_data in rules:
            existing = MiningRule.query.filter_by(code=rule_data["code"]).first()
            if not existing:
                rule = MiningRule(**rule_data)
                db.session.add(rule)
                print(f"添加矿场规则: {rule_data['name']}")
            else:
                print(f"矿场规则已存在: {rule_data['name']}")
        db.session.commit()
        print("矿场规则初始化完成")


if __name__ == "__main__":
    init_mining_rules()
