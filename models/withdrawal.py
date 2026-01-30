from datetime import datetime

from . import db


class Withdrawal(db.Model):
    __tablename__ = "withdrawals"
    __table_args__ = {"comment": "提现表"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="提现ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    address = db.Column(db.String(100), nullable=False, comment="提现地址")
    amount = db.Column(db.Float, nullable=False, comment="提现金额")
    withdrawal_method = db.Column(db.String(20), nullable=False, default="usdt", comment="提现方式")
    status = db.Column(db.String(20), nullable=False, default="pending", comment="提现状态")
    order_number = db.Column(db.String(50), unique=True, nullable=False, comment="订单号")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow, comment="更新时间")
    notes = db.Column(db.Text, comment="备注")
    bank_account = db.Column(db.String(50), comment="银行账号")
    bank_holder = db.Column(db.String(100), comment="持卡人姓名")
    bank_name = db.Column(db.String(100), comment="银行名称")
    bank_code = db.Column(db.String(50), comment="银行代码")
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, comment="审核人ID")

    user = db.relationship(
        "User", backref=db.backref("withdrawals", lazy=True), foreign_keys=[user_id]
    )
    reviewer = db.relationship(
        "User", backref=db.backref("reviewed_withdrawals", lazy=True), foreign_keys=[reviewer_id]
    )

    def __repr__(self):
        return f"<Withdrawal {self.order_number} - {self.status}>"
