from flask import Blueprint, redirect, render_template, session, url_for

from handlers.invite import (
    generate_invite_qr,
    get_invite_code,
    get_invite_info,
    get_invite_stats,
    get_invite_summary,
    get_invite_users,
)

invite_bp = Blueprint("invite", __name__)


@invite_bp.route("/api/user/invite-code")
def invite_code():
    return get_invite_code()


@invite_bp.route("/api/user/invite-stats")
def invite_stats():
    return get_invite_stats()


@invite_bp.route("/ui/invite")
def invite_page():
    if "user_id" not in session:
        return redirect(url_for("auth.index"))
    return render_template("invite.html")


@invite_bp.route("/api/invite/info")
def invite_info():
    return get_invite_info()


@invite_bp.route("/api/invite/summary")
def invite_summary():
    return get_invite_summary()


@invite_bp.route("/api/invite/users")
def invite_users():
    return get_invite_users()


@invite_bp.route("/ui/invite/qr")
def invite_qr():
    return generate_invite_qr()
