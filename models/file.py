from .user import db


class File(db.Model):
    __tablename__ = "file"
    __table_args__ = {"comment": "文件表"}

    id = db.Column(db.Integer, primary_key=True, comment="文件ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    filename = db.Column(db.String(255), nullable=False, comment="文件名")
    file_data = db.Column(db.LargeBinary(length=16777215), nullable=False, comment="文件数据")
    file_type = db.Column(db.String(50), nullable=True, comment="文件类型")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="创建时间")

    user = db.relationship("User", backref="files")
