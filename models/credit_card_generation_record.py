from .user import db


class CreditCardGenerationRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    generated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    generated_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    user = db.relationship("User", backref=db.backref("credit_card_generations", lazy=True))
