from . import db


class MiningRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    miners_consumed = db.Column(db.Integer, nullable=False)
    cycle_days = db.Column(db.Integer, nullable=False)
    energy_reward = db.Column(db.Numeric(10, 4), nullable=False)
    background_image = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<MiningRule {self.name}>"
