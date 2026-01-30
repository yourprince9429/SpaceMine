from .user import db


class Recharge(db.Model):
    __tablename__ = "recharge"
    __table_args__ = {"comment": "充值表"}

    id = db.Column(db.Integer, primary_key=True, comment="充值ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    amount = db.Column(db.Numeric(10, 2), nullable=False, comment="充值金额")
    method = db.Column(db.String(50), nullable=False, comment="充值方式")
    status = db.Column(db.String(20), nullable=False, default="pending", comment="充值状态")
    screenshot_file_id = db.Column(db.Integer, db.ForeignKey("file.id"), nullable=True, comment="截图文件ID")
    bank_card_id = db.Column(db.Integer, db.ForeignKey("credit_card.id"), nullable=True, comment="银行卡ID")
    order_number = db.Column(db.String(100), unique=True, nullable=False, comment="订单号")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="创建时间")
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, comment="审核人ID")

    user = db.relationship("User", backref="recharges", foreign_keys=[user_id])
    reviewer = db.relationship("User", backref="reviewed_recharges", foreign_keys=[reviewer_id])
    screenshot_file = db.relationship("File", backref="recharge_screenshots")
    bank_card = db.relationship("CreditCard", backref="recharges")
