from flask import Blueprint, jsonify, render_template, request

from handlers.recharge import get_recharges, recharge_card

recharge_bp = Blueprint("recharge", __name__)


@recharge_bp.route("/api/recharge/card", methods=["POST"])
def api_recharge_card():
    """信用卡充值API端点"""
    return recharge_card()


@recharge_bp.route("/api/user/recharges", methods=["GET"])
def api_get_recharges():
    """获取用户充值记录API端点"""
    return get_recharges()


@recharge_bp.route("/ui/recharge/history")
def recharge_history():
    """充值记录页面"""
    return render_template("recharge_history.html")
