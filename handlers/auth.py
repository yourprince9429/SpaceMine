import re

from flask import jsonify, request, session
from flask_bcrypt import Bcrypt

from models import InviteRelation, Role, UserRoleRelation, User, db


def get_current_user():
    """获取当前用户，支持session和header两种方式"""
    user_id = None

    if "user_id" in session:
        user_id = session["user_id"]
    else:
        token = request.headers.get("X-Session-Token")
        if token and token.isdigit():
            user_id = int(token)

    if not user_id:
        return None

    user = db.session.get(User, user_id)
    if user and user.status != "active":
        return None
    return user


bcrypt = Bcrypt()


def register_user(data):
    """用户注册"""
    from models.user import generate_unique_invite_code
    from sqlalchemy.exc import IntegrityError

    username = data.get("username")
    password = data.get("password")
    paypwd = data.get("paypwd")
    email = data.get("email")
    invite_code = data.get("invite_code")

    if not username or not password or not paypwd or not invite_code:
        response = jsonify({"success": False, "message": "请填写所有必填字段"})
        response.status_code = 400
        return response

    if len(password) < 6:
        response = jsonify({"success": False, "message": "密码至少6位"})
        response.status_code = 400
        return response

    if len(paypwd) != 6 or not paypwd.isdigit():
        response = jsonify({"success": False, "message": "支付密码必须是6位数字"})
        response.status_code = 400
        return response

    if email and not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        response = jsonify({"success": False, "message": "邮箱格式不正确"})
        response.status_code = 400
        return response

    if User.query.filter_by(username=username).first():
        response = jsonify({"success": False, "message": "用户名已存在"})
        response.status_code = 400
        return response

    inviter = User.query.filter_by(invite_code=invite_code).first()
    if not inviter:
        response = jsonify({"success": False, "message": "邀请码不存在"})
        response.status_code = 400
        return response

    max_retries = 5
    for attempt in range(max_retries):
        new_user = User(username=username, email=email)
        new_user.invite_code = generate_unique_invite_code()
        new_user.set_password(password)
        new_user.set_paypwd(paypwd)

        try:
            db.session.add(new_user)
            db.session.flush()

            relation = InviteRelation(inviter_id=inviter.id, invitee_id=new_user.id)
            db.session.add(relation)

            user_role = Role.query.filter_by(name="user").first()
            if user_role:
                user_role_relation = UserRoleRelation(user_id=new_user.id, role_id=user_role.id)
                db.session.add(user_role_relation)

            db.session.commit()

            return jsonify({"success": True, "message": "注册成功"})
        except IntegrityError as e:
            db.session.rollback()
            if "invite_code" in str(e):
                continue
            else:
                response = jsonify({"success": False, "message": "注册失败，用户名可能已被使用"})
                response.status_code = 400
                return response
        except Exception:
            db.session.rollback()
            response = jsonify({"success": False, "message": "注册失败，请重试"})
            response.status_code = 500
            return response

    response = jsonify({"success": False, "message": "注册失败，无法生成唯一邀请码"})
    response.status_code = 500
    return response


def login_user(data):
    """用户登录"""
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        response = jsonify({"success": False, "message": "请输入用户名和密码"})
        response.status_code = 400
        return response

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        if user.status != "active":
            response = jsonify({"success": False, "message": "账户已被停用，请联系管理员"})
            response.status_code = 403
            return response
        session["user_id"] = user.id
        return jsonify({"success": True, "message": "登录成功", "user_id": str(user.id)})
    else:
        response = jsonify({"success": False, "message": "密钥不存在或用户未注册"})
        response.status_code = 401
        return response


def logout_user():
    """用户登出"""
    session.pop("user_id", None)
    return jsonify({"success": True})
