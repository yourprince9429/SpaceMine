from . import db


class MineUserRelation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mine_id = db.Column(db.Integer, db.ForeignKey("mining_rule.id"), nullable=False)
    mine_code = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    mine = db.relationship("MiningRule", backref="user_relations")
    user = db.relationship("User", backref="mine_relations")

    def __repr__(self):
        return f"<MineUserRelation user_id={self.user_id} mine_code={self.mine_code}>"
