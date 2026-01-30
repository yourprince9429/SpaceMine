from .user import db


class Config(db.Model):
    __tablename__ = "config"
    __table_args__ = {"comment": "配置表"}

    id = db.Column(db.Integer, primary_key=True, comment="配置ID")
    key = db.Column(db.String(255), unique=True, nullable=False, comment="配置键")
    value = db.Column(db.Text, nullable=False, comment="配置值")
    description = db.Column(db.Text, nullable=True, comment="配置描述")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, comment="关联用户ID")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="创建时间")
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        comment="更新时间"
    )
    user = db.relationship("User", backref="configs", lazy=True)
