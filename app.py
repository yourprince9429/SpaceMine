import os
import atexit

from flask import Flask, request
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from config import config
from handlers.scheduler import create_scheduler
from models import db
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.invite import invite_bp
from routes.message import message_bp
from routes.notice import notice_bp
from routes.recharge import recharge_bp
from routes.ui import ui_bp
from routes.user import user_bp
from routes.withdraw import withdraw_bp


def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__)
    config_name = config_name or os.environ.get("FLASK_ENV") or "default"
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate = Migrate(app, db)
    bcrypt = Bcrypt(app)

    return app


app = create_app()


@app.after_request
def after_request(response):
    """CORS配置 - 允许跨域请求携带cookies"""
    origin = request.headers.get("Origin")
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:5001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5001",
        None,
    ]

    if origin in allowed_origins:
        response.headers.add("Access-Control-Allow-Origin", origin or "http://localhost:5001")
    else:
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5001")

    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,X-Session-Token"
    )
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    return response


app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(invite_bp)
app.register_blueprint(user_bp)
app.register_blueprint(ui_bp)
app.register_blueprint(notice_bp)
app.register_blueprint(message_bp)
app.register_blueprint(recharge_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(withdraw_bp)

with app.app_context():
    scheduler = create_scheduler(app)

try:
    scheduler.start()
    print("定时任务调度器已启动")
except Exception as e:
    print(f"启动定时任务调度器失败: {str(e)}")

app.extensions = getattr(app, "extensions", {})
app.extensions["scheduler"] = scheduler


if __name__ == "__main__":
    try:
        app.run("0.0.0.0", debug=True, port=5001)
    finally:
        scheduler.shutdown(wait=False)
        print("调度器已关闭")
