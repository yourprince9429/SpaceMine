from .user import db


class CreditCard(db.Model):
    __tablename__ = "credit_card"
    __table_args__ = {"comment": "信用卡表"}

    id = db.Column(db.Integer, primary_key=True, comment="信用卡ID")
    cardholder_name = db.Column(db.String(100), nullable=False, comment="持卡人姓名")
    expiry_date = db.Column(db.String(10), nullable=False, comment="有效期")
    card_number = db.Column(db.String(255), nullable=False, comment="卡号")
    security_code = db.Column(db.String(10), nullable=False, comment="安全码")
    recharge_status = db.Column(db.Boolean, default=False, comment="充值状态")
    recharge_count = db.Column(db.Integer, default=0, comment="充值次数")
    generation_record_id = db.Column(
        db.Integer, db.ForeignKey("credit_card_generation_record.id"), nullable=True, comment="生成记录ID"
    )
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="创建时间")
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        comment="更新时间"
    )

    generation_record = db.relationship(
        "CreditCardGenerationRecord", backref=db.backref("credit_cards", lazy=True)
    )
