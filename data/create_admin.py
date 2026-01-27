#!/usr/bin/env python3
"""
创建管理员用户脚本 - 确保能够成功登录
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User, Role, UserRoleRelation
from models.user import generate_unique_invite_code


def create_admin():
    """创建能够成功登录的管理员用户"""
    app = create_app()

    with app.app_context():
        print("开始创建管理员用户...")

        # 检查是否已存在管理员用户
        admin_user = (
            User.query.join(UserRoleRelation).join(Role).filter(Role.name == "admin").first()
        )

        if admin_user:
            print(f"管理员用户已存在: {admin_user.username}")
            print(f"登录信息:")
            print(f"  用户名: {admin_user.username}")
            print(f"  密码: admin123")
            return

        # 检查是否已有其他用户
        existing_users = User.query.count()
        if existing_users > 0:
            print("系统中已有其他用户，无法创建管理员用户")
            return

        # 创建管理员用户
        admin = User(
            username="admin",
            email="admin@example.com",
            phone="13800138000",
            status="active",
            invite_code=generate_unique_invite_code(),
        )

        # 设置密码和支付密码
        admin.set_password("admin123")
        admin.set_paypwd("123456")

        db.session.add(admin)
        db.session.flush()

        # 分配管理员角色
        admin_role = Role.query.filter_by(name="admin").first()
        if admin_role:
            user_role = UserRoleRelation(user_id=admin.id, role_id=admin_role.id)
            db.session.add(user_role)

        try:
            db.session.commit()
            print("管理员用户创建成功!")
            print("登录信息:")
            print("  用户名: admin")
            print("  密码: admin123")
            print("  支付密码: 123456")
            print("  邮箱: admin@example.com")
            print("  手机: 13800138000")
        except Exception as e:
            db.session.rollback()
            print(f"创建失败: {e}")


if __name__ == "__main__":
    create_admin()
