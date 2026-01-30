import random

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()


def generate_unique_invite_code():
    while True:
        code = str(random.randint(10000000, 99999999))
        if not User.query.filter_by(invite_code=code).first():
            return code


class Role(db.Model):
    __tablename__ = "role"
    __table_args__ = {"comment": "角色表"}

    id = db.Column(db.Integer, primary_key=True, comment="角色ID")
    name = db.Column(db.String(50), unique=True, nullable=False, comment="角色名称")
    description = db.Column(db.String(200), nullable=True, comment="角色描述")
    users = db.relationship("UserRoleRelation", backref="role", lazy=True)


class UserRoleRelation(db.Model):
    __tablename__ = "user_role_relation"
    __table_args__ = {"comment": "用户角色关联表"}

    id = db.Column(db.Integer, primary_key=True, comment="关联ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False, comment="角色ID")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="创建时间")


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"comment": "用户表"}

    id = db.Column(db.Integer, primary_key=True, comment="用户ID")
    username = db.Column(db.String(80), unique=True, nullable=False, comment="用户名")
    password_hash = db.Column(db.String(128), nullable=False, comment="密码哈希")
    paypwd_hash = db.Column(db.String(128), nullable=True, comment="支付密码哈希")
    email = db.Column(db.String(120), unique=True, nullable=True, comment="邮箱")
    phone = db.Column(db.String(20), nullable=True, comment="手机号")
    real_name = db.Column(db.String(50), nullable=True, comment="真实姓名")
    id_number = db.Column(db.String(20), nullable=True, comment="身份证号")
    id_front_image = db.Column(db.String(255), nullable=True, comment="身份证正面图片")
    id_back_image = db.Column(db.String(255), nullable=True, comment="身份证背面图片")
    invite_code = db.Column(db.String(8), unique=True, nullable=False, comment="邀请码")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="创建时间")
    balance = db.Column(db.Numeric(20, 4), default=0.0000, comment="余额")
    energy = db.Column(db.Numeric(10, 4), nullable=True, default=0.0000, comment="能量值")
    status = db.Column(db.String(20), nullable=True, default="active", comment="状态")
    invited_users = db.relationship(
        "InviteRelation", backref="inviter", foreign_keys="InviteRelation.inviter_id"
    )
    invited_by = db.relationship(
        "InviteRelation", backref="invitee", foreign_keys="InviteRelation.invitee_id"
    )
    roles = db.relationship("UserRoleRelation", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_paypwd(self, paypwd):
        self.paypwd_hash = bcrypt.generate_password_hash(paypwd).decode("utf-8")

    def check_paypwd(self, paypwd):
        return bcrypt.check_password_hash(self.paypwd_hash, paypwd)

    def get_balance(self):
        """获取余额"""
        return self.balance or 0.0000

    def get_energy(self):
        """获取能量值"""
        return self.energy or 0.0000


class InviteRelation(db.Model):
    __tablename__ = "invite_relation"
    __table_args__ = {"comment": "邀请关系表"}

    id = db.Column(db.Integer, primary_key=True, comment="关系ID")
    inviter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="邀请人ID")
    invitee_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="被邀请人ID")


class SupportEmail(db.Model):
    __tablename__ = "support_email"
    __table_args__ = {"comment": "支持邮箱表"}

    id = db.Column(db.Integer, primary_key=True, comment="邮箱ID")
    email = db.Column(db.String(120), unique=True, nullable=False, comment="邮箱地址")
    name = db.Column(db.String(50), nullable=True, comment="联系人姓名")
    is_active = db.Column(db.Boolean, default=True, comment="是否启用")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="创建时间")
