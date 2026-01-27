from flask import Blueprint, redirect, render_template, request, url_for

ui_bp = Blueprint("ui", __name__)


@ui_bp.route("/ui/login")
def ui_login():
    return redirect(url_for("auth.index"))


@ui_bp.route("/ui/invite")
def ui_invite():
    query_string = "?" + request.query_string.decode() if request.query_string else ""
    return redirect(url_for("invite.invite_page") + query_string)


@ui_bp.route("/ui/withdraw")
def ui_withdraw():
    return render_template("withdraw.html")


@ui_bp.route("/ui/security")
def ui_security():
    return render_template("security.html")


@ui_bp.route("/ui/intro")
def ui_intro():
    return render_template("intro.html")


@ui_bp.route("/ui/notices")
def ui_notices():
    return render_template("notices.html")


@ui_bp.route("/ui/messages")
def ui_messages():
    return render_template("messages.html")


@ui_bp.route("/ui/message/<int:message_id>")
def ui_message_detail(message_id):
    return render_template("dashboard.html")
