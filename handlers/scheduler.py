import threading
import traceback
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from models import Config, MineUserRelation, MiningRule, User, db

_app = None
_scheduler = None


def get_settlement_interval():
    """从数据库获取矿场结算周期配置（分钟）"""
    try:
        config = Config.query.filter_by(key="mine_settlement_interval_minutes").first()
        if config:
            interval = int(config.value)
            return max(1, interval)
        return 10
    except Exception:
        return 10


def settle_expired_mines():
    """结算所有到期的矿场"""
    thread_id = threading.current_thread().ident

    try:
        current_time = datetime.utcnow()

        expired_relations = (
            db.session.query(MineUserRelation, MiningRule, User)
            .join(MiningRule, MineUserRelation.mine_id == MiningRule.id)
            .join(User, MineUserRelation.user_id == User.id)
            .filter(MineUserRelation.is_active == True, MineUserRelation.created_at <= current_time)
            .all()
        )

        settled_count = 0
        total_energy_settled = 0.0

        for relation, mining_rule, user in expired_relations:
            cycle_seconds = mining_rule.cycle_days * 24 * 3600
            if cycle_seconds == 0:
                continue

            duration = current_time - relation.created_at
            duration_seconds = duration.total_seconds()

            if duration_seconds >= cycle_seconds:
                energy_per_second = float(mining_rule.energy_reward) / cycle_seconds
                total_generated_energy = energy_per_second * cycle_seconds

                user_energy = float(user.get_energy())
                user.energy = user_energy + total_generated_energy

                relation.is_active = False

                settled_count += 1
                total_energy_settled += total_generated_energy

        if settled_count > 0:
            db.session.commit()

        return settled_count, total_energy_settled

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return 0, 0.0


def check_and_settle_user_mines(user_id):
    """检查并结算指定用户的到期矿场"""
    try:
        current_time = datetime.utcnow()

        user_relations = (
            db.session.query(MineUserRelation, MiningRule, User)
            .join(MiningRule, MineUserRelation.mine_id == MiningRule.id)
            .join(User, MineUserRelation.user_id == User.id)
            .filter(MineUserRelation.user_id == user_id, MineUserRelation.is_active == True)
            .all()
        )

        settled_count = 0
        total_energy_settled = 0.0

        for relation, mining_rule, user in user_relations:
            cycle_seconds = mining_rule.cycle_days * 24 * 3600
            if cycle_seconds == 0:
                continue

            duration = current_time - relation.created_at
            duration_seconds = duration.total_seconds()

            if duration_seconds >= cycle_seconds:
                energy_per_second = float(mining_rule.energy_reward) / cycle_seconds
                total_generated_energy = energy_per_second * cycle_seconds

                user_energy = float(user.get_energy())
                user.energy = user_energy + total_generated_energy

                relation.is_active = False

                settled_count += 1
                total_energy_settled += total_generated_energy

        if settled_count > 0:
            db.session.commit()

        return settled_count, total_energy_settled

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return 0, 0.0


def create_scheduler(app):
    """创建并配置定时任务调度器"""
    global _app, _scheduler
    _app = app._get_current_object() if hasattr(app, "_get_current_object") else app

    if _scheduler is not None and _scheduler.running:
        return _scheduler

    old_scheduler = app.extensions.get("scheduler")
    if old_scheduler and old_scheduler.running:
        old_scheduler.shutdown(wait=False)

    _scheduler = BackgroundScheduler()

    interval_minutes = get_settlement_interval()

    _scheduler.add_job(
        func=settle_expired_mines_with_context,
        trigger="interval",
        minutes=interval_minutes,
        id="settle_expired_mines",
        name="结算到期矿场",
        replace_existing=True,
    )

    return _scheduler


def update_scheduler_interval(app):
    """更新调度器的执行间隔"""
    global _app, _scheduler
    _app = app._get_current_object() if hasattr(app, "_get_current_object") else app

    try:
        interval_minutes = get_settlement_interval()

        old_scheduler = app.extensions.get("scheduler")
        if old_scheduler and old_scheduler.running:
            old_scheduler.shutdown(wait=False)

        if _scheduler and _scheduler.running:
            _scheduler.shutdown(wait=False)

        _scheduler = BackgroundScheduler()
        _scheduler.add_job(
            func=settle_expired_mines_with_context,
            trigger="interval",
            minutes=interval_minutes,
            id="settle_expired_mines",
            name="结算到期矿场",
            replace_existing=True,
        )

        _scheduler.start()
        app.extensions["scheduler"] = _scheduler

        return _scheduler

    except Exception as e:
        traceback.print_exc()
        return None


def settle_expired_mines_with_context():
    """在应用上下文中结算到期矿场"""
    with _app.app_context():
        settle_expired_mines()
