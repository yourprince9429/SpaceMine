from .user import db


class Recharge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    screenshot_file_id = db.Column(db.Integer, db.ForeignKey("file.id"), nullable=True)
    bank_card_id = db.Column(db.Integer, db.ForeignKey("credit_card.id"), nullable=True)
    order_number = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    user = db.relationship("User", backref="recharges", foreign_keys=[user_id])
    reviewer = db.relationship("User", backref="reviewed_recharges", foreign_keys=[reviewer_id])
    screenshot_file = db.relationship("File", backref="recharge_screenshots")
    bank_card = db.relationship("CreditCard", backref="recharges")
