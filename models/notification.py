from .user import db


class Notification(db.Model):
    __tablename__ = "notification"
    __table_args__ = {"comment": "通知表"}

    id = db.Column(db.Integer, primary_key=True, comment="通知ID")
    title = db.Column(db.String(255), nullable=False, comment="通知标题")
    content = db.Column(db.Text, nullable=False, comment="通知内容")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="创建时间")
    is_read = db.Column(db.Boolean, default=False, nullable=False, comment="是否已读")

    user = db.relationship("User", backref="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "user_id": self.user_id,
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
            ),
            "is_read": self.is_read,
        }
