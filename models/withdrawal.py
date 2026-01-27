from datetime import datetime

from . import db


class Withdrawal(db.Model):
    __tablename__ = "withdrawals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    withdrawal_method = db.Column(db.String(20), nullable=False, default="usdt")
    status = db.Column(db.String(20), nullable=False, default="pending")
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    bank_account = db.Column(db.String(50))
    bank_holder = db.Column(db.String(100))
    bank_name = db.Column(db.String(100))
    bank_code = db.Column(db.String(50))
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    user = db.relationship(
        "User", backref=db.backref("withdrawals", lazy=True), foreign_keys=[user_id]
    )
    reviewer = db.relationship(
        "User", backref=db.backref("reviewed_withdrawals", lazy=True), foreign_keys=[reviewer_id]
    )

    def __repr__(self):
        return f"<Withdrawal {self.order_number} - {self.status}>"
