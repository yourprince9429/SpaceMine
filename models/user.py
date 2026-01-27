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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    users = db.relationship("UserRoleRelation", backref="role", lazy=True)


class UserRoleRelation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    paypwd_hash = db.Column(db.String(128), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    real_name = db.Column(db.String(50), nullable=True)
    id_number = db.Column(db.String(20), nullable=True)
    id_front_image = db.Column(db.String(255), nullable=True)
    id_back_image = db.Column(db.String(255), nullable=True)
    invite_code = db.Column(db.String(8), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    balance = db.Column(db.Numeric(20, 4), default=0.0000)
    energy = db.Column(db.Numeric(10, 4), nullable=True, default=0.0000)
    status = db.Column(db.String(20), nullable=True, default="active")
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
    id = db.Column(db.Integer, primary_key=True)
    inviter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class SupportEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
