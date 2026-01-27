from flask import Blueprint
from handlers.balance import get_user_balance
from handlers.support import get_support_info
from handlers.messages import get_unread_messages
from handlers.mine import get_user_mines, open_mine
from handlers.security import (
    get_user_security,
    verify_real_name,
    set_pay_password,
    change_pay_password,
    change_login_password,
    bind_email,
)

user_bp = Blueprint("user", __name__)


@user_bp.route("/api/user/balance")
def user_balance():
    return get_user_balance()


@user_bp.route("/api/support/info")
def support_info():
    return get_support_info()


@user_bp.route("/api/messages/unread")
def messages_unread():
    return get_unread_messages()


@user_bp.route("/api/user/mines")
def user_mines():
    return get_user_mines()


@user_bp.route("/api/mine/open", methods=["POST"])
def mine_open():
    return open_mine()


@user_bp.route("/api/user/security")
def user_security():
    return get_user_security()


@user_bp.route("/api/user/security/verify", methods=["POST"])
def user_verify_real_name():
    # 支持文件上传，所以不需要JSON解析
    return verify_real_name()


@user_bp.route("/api/user/security/pay-password", methods=["POST"])
def user_set_pay_password():
    return set_pay_password()


@user_bp.route("/api/user/security/change-pay-password", methods=["POST"])
def user_change_pay_password():
    return change_pay_password()


@user_bp.route("/api/user/security/password", methods=["POST"])
def user_change_password():
    return change_login_password()


@user_bp.route("/api/user/security/email", methods=["POST"])
def user_bind_email():
    return bind_email()
