from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    request,
    jsonify,
)
from models import Config, User, Recharge, File, db, Role, UserRoleRelation
from handlers.auth import get_current_user
from handlers.recharge import recharge_card
import uuid
import os
import time

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.index"))
    return render_template("dashboard.html")


@dashboard_bp.route("/recharge")
def recharge():
    if "user_id" not in session:
        return redirect(url_for("auth.index"))
    return render_template("recharge.html")


@dashboard_bp.route("/recharge/usdt")
def recharge_usdt():
    if "user_id" not in session:
        return redirect(url_for("auth.index"))

    # 从配置表获取USDT地址
    usdt_config = Config.query.filter_by(key="usdt_address").first()
    usdt_address = (
        usdt_config.value if usdt_config else "0x71c7656ec7183119391141ce915fe11679b240c8"
    )

    return render_template("recharge_usdt.html", usdt_address=usdt_address)


@dashboard_bp.route("/recharge/card")
def recharge_card_page():
    if "user_id" not in session:
        return redirect(url_for("auth.index"))
    return render_template("recharge_card.html")


@dashboard_bp.route("/api/recharge/usdt", methods=["POST"])
def api_recharge_usdt():
    """USDT充值接口"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    # 获取表单数据
    amount = request.form.get("amount", "").strip()
    voucher = request.files.get("voucher")

    # 验证金额
    if not amount:
        return jsonify({"success": False, "message": "请输入充值金额"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"success": False, "message": "充值金额必须大于0"}), 400
    except ValueError:
        return jsonify({"success": False, "message": "充值金额格式不正确"}), 400

    # 验证图片
    if not voucher:
        return jsonify({"success": False, "message": "请上传充值凭证"}), 400

    # 验证文件类型
    allowed_extensions = {"png", "jpg", "jpeg", "gif"}
    if not voucher.filename or voucher.filename.split(".")[-1].lower() not in allowed_extensions:
        return jsonify({"success": False, "message": "只允许上传图片文件"}), 400

    # 验证文件大小（限制为5MB）
    voucher.seek(0, 2)  # 移动到文件末尾
    file_size = voucher.tell()
    voucher.seek(0)  # 回到文件开头

    max_size = 5 * 1024 * 1024  # 5MB
    if file_size > max_size:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"文件大小不能超过5MB，当前文件大小：{file_size/1024/1024:.1f}MB",
                }
            ),
            400,
        )

    try:
        # 保存图片文件
        file_data = voucher.read()
        file_extension = voucher.filename.split(".")[-1].lower()
        filename = f"recharge_{user.id}_{uuid.uuid4().hex}.{file_extension}"

        # 保存到文件表
        file_record = File(
            user_id=user.id,
            filename=filename,
            file_data=file_data,
            file_type="recharge_voucher",
        )
        db.session.add(file_record)
        db.session.flush()  # 获取file_id

        # 生成订单号
        order_number = f"USDT_{user.id}_{int(time.time())}"

        # 创建充值记录
        recharge = Recharge(
            user_id=user.id,
            amount=amount,
            method="usdt",
            status="pending",
            screenshot_file_id=file_record.id,
            order_number=order_number,
        )
        db.session.add(recharge)
        db.session.commit()

        return jsonify({"success": True, "message": "USDT充值提交成功，等待审核"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "充值提交失败，请重试"}), 500


@dashboard_bp.route("/api/recharge/card", methods=["POST"])
def api_recharge_card():
    """信用卡充值接口"""
    return recharge_card()


# 新增API用于获取用户角色信息
@dashboard_bp.route("/api/user/role")
def get_user_role():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    is_admin = False
    admin_role = Role.query.filter_by(name="admin").first()
    if admin_role:
        user_role_relation = UserRoleRelation.query.filter_by(
            user_id=user.id, role_id=admin_role.id
        ).first()
        is_admin = user_role_relation is not None

    return jsonify({"success": True, "is_admin": is_admin})
