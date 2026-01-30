from . import db


class MiningRule(db.Model):
    __tablename__ = "mining_rule"
    __table_args__ = {"comment": "挖矿规则表"}

    id = db.Column(db.Integer, primary_key=True, comment="规则ID")
    code = db.Column(db.String(50), unique=True, nullable=False, comment="矿场代码")
    name = db.Column(db.String(100), nullable=False, comment="矿场名称")
    miners_consumed = db.Column(db.Integer, nullable=False, comment="消耗矿工数")
    cycle_days = db.Column(db.Integer, nullable=False, comment="周期天数")
    energy_reward = db.Column(db.Numeric(10, 4), nullable=False, comment="能量奖励")
    background_image = db.Column(db.String(255), nullable=True, comment="背景图片")

    def __repr__(self):
        return f"<MiningRule {self.name}>"
