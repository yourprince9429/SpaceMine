from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from models import MineUserRelation, MiningRule, User, Config, db

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
    import threading

    thread_id = threading.current_thread().ident
    print(f"[DEBUG] settle_expired_mines 被调用，线程ID: {thread_id}")

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
            print(
                f"[{current_time}] 成功结算 {settled_count} 个到期矿场，总能量: {total_energy_settled:.4f}"
            )
        else:
            print(f"[{current_time}] 没有到期的矿场需要结算")

        return settled_count, total_energy_settled

    except Exception as e:
        db.session.rollback()
        print(f"结算矿场时发生错误: {str(e)}")
        import traceback

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
            print(
                f"[{current_time}] 用户 {user_id} 成功结算 {settled_count} 个到期矿场，总能量: {total_energy_settled:.4f}"
            )

        return settled_count, total_energy_settled

    except Exception as e:
        db.session.rollback()
        print(f"结算用户 {user_id} 的矿场时发生错误: {str(e)}")
        return 0, 0.0


def create_scheduler(app):
    """创建并配置定时任务调度器"""
    global _app, _scheduler
    _app = app._get_current_object() if hasattr(app, "_get_current_object") else app

    if _scheduler is not None and _scheduler.running:
        print(f"[DEBUG] 调度器已在运行，跳过创建")
        return _scheduler

    old_scheduler = app.extensions.get("scheduler")
    if old_scheduler and old_scheduler.running:
        print(f"[DEBUG] 发现旧的调度器在运行，正在关闭...")
        old_scheduler.shutdown(wait=False)
        print(f"[DEBUG] 旧调度器已关闭")

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

    print(f"定时任务调度器配置完成，矿场结算周期: {interval_minutes} 分钟")
    print(f"当前调度器中的任务: {_scheduler.get_jobs()}")

    return _scheduler


def update_scheduler_interval(app):
    """更新调度器的执行间隔"""
    global _app, _scheduler
    _app = app._get_current_object() if hasattr(app, "_get_current_object") else app

    try:
        interval_minutes = get_settlement_interval()

        print(f"[DEBUG] update_scheduler_interval 被调用")
        print(f"[DEBUG] 当前全局调度器: {_scheduler}")
        print(f"[DEBUG] app.extensions['scheduler']: {app.extensions.get('scheduler')}")

        old_scheduler = app.extensions.get("scheduler")
        if old_scheduler and old_scheduler.running:
            print(f"[DEBUG] 关闭 app.extensions 中的旧调度器...")
            old_scheduler.shutdown(wait=False)
            print(f"[DEBUG] app.extensions 中的旧调度器已关闭")

        if _scheduler and _scheduler.running:
            print(f"[DEBUG] 关闭全局变量中的旧调度器...")
            _scheduler.shutdown(wait=False)
            print(f"[DEBUG] 全局变量中的旧调度器已关闭")

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
        print(f"[DEBUG] 新调度器已启动")
        print(f"[DEBUG] 新任务已添加，间隔: {interval_minutes} 分钟")

        updated_job = _scheduler.get_job("settle_expired_mines")
        print(f"[DEBUG] 新任务触发器: {updated_job.trigger}")
        print(f"[DEBUG] 当前调度器中的所有任务: {_scheduler.get_jobs()}")

        app.extensions["scheduler"] = _scheduler
        print(f"[DEBUG] app.extensions['scheduler'] 已更新")

        return _scheduler

    except Exception as e:
        print(f"更新调度器间隔失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


def settle_expired_mines_with_context():
    """在应用上下文中结算到期矿场"""
    with _app.app_context():
        settle_expired_mines()
