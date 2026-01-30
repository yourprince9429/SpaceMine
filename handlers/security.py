import base64
import binascii
import functools
import hashlib
import traceback

from flask import jsonify, request, session

from models import File, User, db


def token_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "未登录"}), 401

        user_id = session.get("user_id")
        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        if user.status != "active":
            return jsonify({"success": False, "message": "账户已被停用，请联系管理员"}), 403

        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    """获取当前用户"""
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = User.query.get(user_id)
    if user and user.status != "active":
        return None
    return user


@token_required
def get_user_security():
    """获取用户安全信息"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        # 判断实名认证状态
        is_verified = bool(user.real_name and user.id_number)

        # 获取身份证图片
        id_front_base64 = None
        id_back_base64 = None

        if user.id_front_image:
            try:
                front_file_id = int(user.id_front_image)
                front_file = File.query.get(front_file_id)
                if front_file and front_file.file_data:
                    file_extension = (
                        front_file.filename.split(".")[-1].lower()
                        if "." in front_file.filename
                        else "png"
                    )
                    id_front_base64 = f"data:image/{file_extension};base64,{base64.b64encode(front_file.file_data).decode('utf-8')}"
                else:
                    pass
            except Exception as e:
                pass

        if user.id_back_image:
            try:
                back_file_id = int(user.id_back_image)
                back_file = File.query.get(back_file_id)
                if back_file and back_file.file_data:
                    file_extension = (
                        back_file.filename.split(".")[-1].lower()
                        if "." in back_file.filename
                        else "png"
                    )
                    id_back_base64 = f"data:image/{file_extension};base64,{base64.b64encode(back_file.file_data).decode('utf-8')}"
                else:
                    pass
            except Exception as e:
                pass

        security_info = {
            "success": True,
            "has_password": bool(user.password_hash),
            "has_pay_password": bool(user.paypwd_hash),
            "phone": user.phone,
            "email": user.email,
            "verified": is_verified,
            "real_name": user.real_name,
            "id_number": user.id_number,
            "id_front_image": id_front_base64,
            "id_back_image": id_back_base64,
        }

        return jsonify(security_info)

    except Exception as e:
        return jsonify({"success": False, "message": "获取安全信息失败"}), 500


@token_required
def verify_real_name():
    """实名认证"""
    try:
        # 检查是否有文件上传
        if "id_front" in request.files and "id_back" in request.files:
            # 文件上传模式
            id_front = request.files["id_front"]
            id_back = request.files["id_back"]
            real_name = request.form.get("real_name", "").strip()
            id_number = request.form.get("id_number", "").strip()
            phone = request.form.get("phone", "").strip()

            if not real_name or not id_number or not phone:
                return (
                    jsonify({"success": False, "message": "姓名、身份证号和手机号不能为空"}),
                    400,
                )

            if not id_front or not id_back:
                return (
                    jsonify({"success": False, "message": "请上传身份证正反面照片"}),
                    400,
                )

            # 验证文件类型
            allowed_extensions = {"png", "jpg", "jpeg", "gif"}
            if not (
                id_front.filename.split(".")[-1].lower() in allowed_extensions
                and id_back.filename.split(".")[-1].lower() in allowed_extensions
            ):
                return jsonify({"success": False, "message": "只允许上传图片文件"}), 400

            # 简单的身份证验证
            if len(id_number) != 18:
                return jsonify({"success": False, "message": "身份证号格式不正确"}), 400

            user = get_current_user()
            if not user:
                return jsonify({"success": False, "message": "用户不存在"}), 404

            # 检查文件大小（限制为5MB）
            id_front.seek(0, 2)  # 移动到文件末尾
            front_size = id_front.tell()
            id_front.seek(0)  # 回到文件开头

            id_back.seek(0, 2)  # 移动到文件末尾
            back_size = id_back.tell()
            id_back.seek(0)  # 回到文件开头

            max_size = 5 * 1024 * 1024  # 5MB
            if front_size > max_size or back_size > max_size:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"文件大小不能超过5MB，当前正面照片大小：{front_size/1024/1024:.1f}MB，反面照片大小：{back_size/1024/1024:.1f}MB",
                        }
                    ),
                    400,
                )

            # 读取文件内容
            id_front_data = id_front.read()
            id_back_data = id_back.read()

            # 保存身份证正面照片到文件表
            id_front_file = File(
                user_id=user.id,
                filename=id_front.filename,
                file_data=id_front_data,
                file_type="id_front",
            )
            db.session.add(id_front_file)

            # 保存身份证反面照片到文件表
            id_back_file = File(
                user_id=user.id,
                filename=id_back.filename,
                file_data=id_back_data,
                file_type="id_back",
            )
            db.session.add(id_back_file)

            # 先flush以生成文件ID
            db.session.flush()

            # 更新用户信息
            user.real_name = real_name
            user.id_number = id_number
            user.phone = phone
            # 保存文件ID到用户表（可选，用于快速关联）
            user.id_front_image = str(id_front_file.id)
            user.id_back_image = str(id_back_file.id)

            db.session.commit()

            return jsonify({"success": True, "message": "实名认证提交成功，等待审核"})

        else:
            # JSON模式（兼容旧版本）
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "无效的请求数据"}), 400

            real_name = data.get("real_name", "").strip()
            id_number = data.get("id_number", "").strip()

            if not real_name or not id_number:
                return (
                    jsonify({"success": False, "message": "姓名和身份证号不能为空"}),
                    400,
                )

            # 简单的身份证验证
            if len(id_number) != 18:
                return jsonify({"success": False, "message": "身份证号格式不正确"}), 400

            user = get_current_user()
            if not user:
                return jsonify({"success": False, "message": "用户不存在"}), 404

            user.real_name = real_name
            user.id_number = id_number
            db.session.commit()

            return jsonify({"success": True, "message": "实名认证成功"})

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"success": False, "message": "实名认证失败"}), 500


@token_required
def set_pay_password():
    """设置交易密码"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "无效的请求数据"}), 400

        password = data.get("password", "").strip()
        confirm_password = data.get("confirm_password", "").strip()

        if not password or not confirm_password:
            return jsonify({"success": False, "message": "密码不能为空"}), 400

        if password != confirm_password:
            return jsonify({"success": False, "message": "两次密码输入不一致"}), 400

        if len(password) < 6:
            return jsonify({"success": False, "message": "密码长度至少6位"}), 400

        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        # 设置交易密码
        user.set_paypwd(password)
        db.session.commit()

        return jsonify({"success": True, "message": "交易密码设置成功"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "设置交易密码失败"}), 500


@token_required
def change_pay_password():
    """修改交易密码（不需要验证当前密码）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "无效的请求数据"}), 400

        new_password = data.get("new_password", "").strip()
        confirm_password = data.get("confirm_password", "").strip()

        if not new_password or not confirm_password:
            return jsonify({"success": False, "message": "密码字段不能为空"}), 400

        if new_password != confirm_password:
            return jsonify({"success": False, "message": "新密码和确认密码不一致"}), 400

        if len(new_password) < 6:
            return jsonify({"success": False, "message": "新密码长度至少6位"}), 400

        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        # 检查是否已设置交易密码（修改模式需要已设置）
        if not user.paypwd_hash:
            return (
                jsonify({"success": False, "message": "尚未设置交易密码，请先设置"}),
                400,
            )

        # 更新交易密码
        user.set_paypwd(new_password)
        db.session.commit()

        return jsonify({"success": True, "message": "交易密码修改成功"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "修改交易密码失败"}), 500


@token_required
def change_login_password():
    """修改登录密码"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "无效的请求数据"}), 400

        old_password = data.get("old_password", "").strip()
        new_password = data.get("new_password", "").strip()
        confirm_password = data.get("confirm_password", "").strip()

        if not old_password or not new_password or not confirm_password:
            return jsonify({"success": False, "message": "所有密码字段都不能为空"}), 400

        if new_password != confirm_password:
            return jsonify({"success": False, "message": "新密码和确认密码不一致"}), 400

        if len(new_password) < 6:
            return jsonify({"success": False, "message": "新密码长度至少6位"}), 400

        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        # 验证旧密码
        if not user.check_password(old_password):
            return jsonify({"success": False, "message": "旧密码不正确"}), 400

        # 检查新密码是否与旧密码相同
        if new_password == old_password:
            return jsonify({"success": False, "message": "新密码不能与旧密码相同"}), 400

        # 更新密码
        user.set_password(new_password)
        db.session.commit()

        return jsonify({"success": True, "message": "登录密码修改成功"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "修改登录密码失败"}), 500


@token_required
def bind_email():
    """绑定邮箱"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "无效的请求数据"}), 400

        email = data.get("email", "").strip()

        if not email:
            return jsonify({"success": False, "message": "邮箱不能为空"}), 400

        # 简单的邮箱格式验证
        if "@" not in email or "." not in email:
            return jsonify({"success": False, "message": "邮箱格式不正确"}), 400

        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        user.email = email
        db.session.commit()

        return jsonify({"success": True, "message": "邮箱绑定成功"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "绑定邮箱失败"}), 500


def verify_pay_password(user_id, password):
    """验证支付密码"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False

        if not user.paypwd_hash:
            return False

        return user.check_paypwd(password)

    except Exception as e:
        return False
