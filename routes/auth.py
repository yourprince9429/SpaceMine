from flask import Blueprint, request, render_template, redirect, url_for, session
from handlers.auth import login_user, register_user, logout_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("login.html")


@auth_bp.route("/register")
def register():
    return render_template("register.html")


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    return login_user(data)


@auth_bp.route("/api/register", methods=["POST"])
def register_api():
    data = request.get_json()
    return register_user(data)


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    return logout_user()


@auth_bp.route("/ui/login")
def ui_login():
    return render_template("login.html")
