from datetime import datetime

from models import db


class Notice(db.Model):
    __tablename__ = "notices"
    __table_args__ = {"comment": "公告表"}

    id = db.Column(db.Integer, primary_key=True, comment="公告ID")
    title = db.Column(db.String(200), nullable=False, comment="公告标题")
    content = db.Column(db.Text, nullable=False, comment="公告内容")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="创建用户ID")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.user_id,
        }
