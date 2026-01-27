#!/usr/bin/env python3
"""
初始化管理员用户脚本
"""

import sys
import os
import hashlib
import secrets
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User, Role, UserRoleRelation
from models.user import generate_unique_invite_code


def create_admin_user():
    """创建管理员用户"""
    app = create_app()

    with app.app_context():
        print("开始创建管理员用户...")

        # 检查是否已存在管理员用户
        admin_user = (
            User.query.join(UserRoleRelation).join(Role).filter(Role.name == "admin").first()
        )

        if admin_user:
            print(f"管理员用户已存在: {admin_user.username}")
            return

        # 创建管理员用户
        admin_username = "admin"
        admin_password = "admin123"  # 初始密码
        admin_paypwd = "123456"  # 支付密码

        # 使用bcrypt生成密码哈希
        admin_user = User(
            username=admin_username, email="admin@example.com", phone="13800138000", status="active"
        )
        admin_user.set_password(admin_password)
        admin_user.set_paypwd(admin_paypwd)
        admin_user.invite_code = generate_unique_invite_code()

        db.session.add(admin_user)
        db.session.flush()  # 获取用户ID

        # 获取管理员角色
        admin_role = Role.query.filter_by(name="admin").first()
        if not admin_role:
            print("错误: 未找到管理员角色")
            return

        # 分配管理员角色
        user_role_relation = UserRoleRelation(
            user_id=admin_user.id, role_id=admin_role.id, created_at=datetime.utcnow()
        )

        db.session.add(user_role_relation)

        try:
            db.session.commit()
            print(f"管理员用户创建成功:")
            print(f"  用户名: {admin_username}")
            print(f"  密码: {admin_password}")
            print(f"  角色: 管理员")
            print(f"  用户ID: {admin_user.id}")
        except Exception as e:
            db.session.rollback()
            print(f"创建管理员用户失败: {e}")


if __name__ == "__main__":
    create_admin_user()
