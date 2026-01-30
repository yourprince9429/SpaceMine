from . import db


class MineUserRelation(db.Model):
    __tablename__ = "mine_user_relation"
    __table_args__ = {"comment": "矿场用户关联表"}

    id = db.Column(db.Integer, primary_key=True, comment="关联ID")
    mine_id = db.Column(db.Integer, db.ForeignKey("mining_rule.id"), nullable=False, comment="矿场ID")
    mine_code = db.Column(db.String(50), nullable=False, comment="矿场代码")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="创建时间")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    is_active = db.Column(db.Boolean, default=True, nullable=False, comment="是否激活")

    mine = db.relationship("MiningRule", backref="user_relations")
    user = db.relationship("User", backref="mine_relations")

    def __repr__(self):
        return f"<MineUserRelation user_id={self.user_id} mine_code={self.mine_code}>"
