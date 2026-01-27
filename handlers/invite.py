import base64
import io

import qrcode
from flask import jsonify, send_file

from handlers.auth import get_current_user
from models import Config


def get_invite_code():
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    return jsonify({"success": True, "invite_code": user.invite_code})


def get_invite_stats():
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    invited_count = len(user.invited_users)
    return jsonify({"success": True, "invited_count": invited_count})


def get_invite_info():
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    return jsonify({"success": True, "mobile": user.username, "user_code": user.invite_code})


def get_invite_users():
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    invited_users = []
    for relation in user.invited_users:
        invitee = relation.invitee
        balance = invitee.balance if invitee.balance is not None else 0.0000

        if balance == 0:
            balance_str = "0.00"
        elif balance == int(balance):
            balance_str = f"{int(balance)}"
        else:
            balance_str = f"{balance:.2f}"

        invited_users.append(
            {
                "user_nickname": invitee.username,
                "mobile": invitee.username,
                "balance": balance_str,
                "add_time": (
                    invitee.created_at.strftime("%Y-%m-%d %H:%M:%S") if invitee.created_at else ""
                ),
            }
        )

    return jsonify({"success": True, "users": invited_users})


def get_invite_summary():
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    invited_count = len(user.invited_users)
    rate = invited_count * 1

    return jsonify(
        {
            "success": True,
            "today_reward": "0.0000",
            "total_reward": "0.0000",
            "team_income": "0.0000",
            "rate": rate,
            "invited_count": invited_count,
        }
    )


def generate_invite_qr():
    user = get_current_user()
    if not user:
        response = jsonify({"success": False, "message": "未登录"})
        response.status_code = 401
        return response

    system_url_config = Config.query.filter_by(key="system_url").first()
    system_url = system_url_config.value if system_url_config else "http://127.0.0.1:5001"
    invite_url = f"{system_url}/register?invite_code={user.invite_code}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(invite_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    return send_file(img_buffer, mimetype="image/png")
