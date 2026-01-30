from .user import db


class CreditCardGenerationRecord(db.Model):
    __tablename__ = "credit_card_generation_record"
    __table_args__ = {"comment": "信用卡生成记录表"}

    id = db.Column(db.Integer, primary_key=True, comment="记录ID")
    generated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="生成时间")
    generated_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="生成者ID")
    notes = db.Column(db.Text, nullable=True, comment="备注")

    user = db.relationship("User", backref=db.backref("credit_card_generations", lazy=True))
