from .user import db


class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cardholder_name = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.String(10), nullable=False)
    card_number = db.Column(db.String(255), nullable=False)
    security_code = db.Column(db.String(10), nullable=False)
    recharge_status = db.Column(db.Boolean, default=False)
    recharge_count = db.Column(db.Integer, default=0)
    generation_record_id = db.Column(
        db.Integer, db.ForeignKey("credit_card_generation_record.id"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    generation_record = db.relationship(
        "CreditCardGenerationRecord", backref=db.backref("credit_cards", lazy=True)
    )
