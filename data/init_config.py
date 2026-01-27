import sys
import os
import random
import string

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Config, SupportEmail


def generate_random_email():
    """生成随机邮箱地址"""
    # 生成随机用户名
    username_length = random.randint(6, 12)
    username = "".join(random.choices(string.ascii_lowercase + string.digits, k=username_length))

    # 随机选择邮箱域名
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "qq.com", "163.com"]
    domain = random.choice(domains)

    return f"{username}@{domain}"


def init_config():
    configs = [
        {"key": "max_credit_card_recharge", "value": "50", "description": "信用卡最大充值值"},
        {"key": "1_recharge_success_rate", "value": "0.8", "description": "第一次充值成功率"},
        {"key": "2_recharge_success_rate", "value": "0.5", "description": "第二次充值成功率"},
        {"key": "3_recharge_success_rate", "value": "0.2", "description": "第三次充值成功率"},
        {"key": "4_recharge_success_rate", "value": "0", "description": "第四次充值成功率"},
        {
            "key": "usdt_address",
            "value": "0x71c7656ec7183119391141ce915fe11679b240c8",
            "description": "USDT充值地址",
        },
        {
            "key": "mine_settlement_interval_minutes",
            "value": "10",
            "description": "矿场结算定时任务执行周期（分钟）",
        },
        {"key": "system_url", "value": "http://127.0.0.1:5001", "description": "系统基础地址"},
    ]

    with app.app_context():
        for config_data in configs:
            existing = Config.query.filter_by(key=config_data["key"]).first()
            if not existing:
                config = Config(**config_data)
                db.session.add(config)
                print(f"添加配置项: {config_data['key']}")
            else:
                print(f"配置项已存在: {config_data['key']}")

        # 初始化SupportEmail表
        support_emails_db = SupportEmail.query.all()
        if not support_emails_db:
            # 生成两个随机邮箱
            email1 = generate_random_email()
            email2 = generate_random_email()

            # 确保两个邮箱不相同
            while email1 == email2:
                email2 = generate_random_email()

            support_email1 = SupportEmail(email=email1, name="客服1", is_active=True)
            support_email2 = SupportEmail(email=email2, name="客服2", is_active=True)
            db.session.add(support_email1)
            db.session.add(support_email2)
            print(f"添加SupportEmail记录: {email1}, {email2}")
        else:
            print("SupportEmail表已存在记录")

        db.session.commit()
        print("配置项和客服邮箱初始化完成")


if __name__ == "__main__":
    init_config()
