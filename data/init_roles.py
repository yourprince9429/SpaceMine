#!/usr/bin/env python3
"""
初始化角色数据脚本
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models.user import User, Role, UserRoleRelation


def init_roles():
    """初始化角色数据"""
    with app.app_context():
        # 检查是否已有角色数据
        if Role.query.count() > 0:
            print("角色数据已存在，跳过初始化")
            return

        # 创建普通用户角色
        user_role = Role(name="user", description="普通用户角色，拥有基本的用户权限")

        # 创建管理员角色
        admin_role = Role(name="admin", description="管理员角色，拥有系统管理权限")

        # 添加到数据库
        db.session.add(user_role)
        db.session.add(admin_role)
        db.session.commit()

        print("角色数据初始化完成:")
        print(f"- 普通用户 (user): {user_role.description}")
        print(f"- 管理员 (admin): {admin_role.description}")


def assign_admin_to_existing_users():
    """为现有的用户分配普通用户角色"""
    with app.app_context():
        # 获取所有用户
        users = User.query.all()

        if not users:
            print("没有找到用户，跳过用户角色分配")
            return

        # 获取普通用户角色
        user_role = Role.query.filter_by(name="user").first()
        if not user_role:
            print("未找到普通用户角色，跳过用户角色分配")
            return

        # 为每个用户分配普通用户角色
        for user in users:
            # 检查用户是否已有该角色
            existing_relation = UserRoleRelation.query.filter_by(
                user_id=user.id, role_id=user_role.id
            ).first()

            if not existing_relation:
                user_role_relation = UserRoleRelation(
                    user_id=user.id, role_id=user_role.id, created_at=datetime.utcnow()
                )
                db.session.add(user_role_relation)

        db.session.commit()
        print(f"已为 {len(users)} 个用户分配普通用户角色")


if __name__ == "__main__":
    print("开始初始化角色数据...")
    init_roles()
    assign_admin_to_existing_users()
    print("角色数据初始化完成!")
