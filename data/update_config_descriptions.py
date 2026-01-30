import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Config


def update_config_descriptions():
    config_updates = {
        "1_recharge_success_rate": "第一次充值成功率",
        "2_recharge_success_rate": "第二次充值成功率",
        "3_recharge_success_rate": "第三次充值成功率",
        "4_recharge_success_rate": "第四次充值成功率",
    }

    with app.app_context():
        for key, description in config_updates.items():
            config = Config.query.filter_by(key=key).first()
            if config:
                config.description = description
                print(f"更新配置描述: {key}")
            else:
                print(f"配置不存在: {key}")

        db.session.commit()
        print("配置描述更新完成")


if __name__ == "__main__":
    update_config_descriptions()
