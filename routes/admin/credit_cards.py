import csv
import io
import logging
import random
import traceback
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

from flask import Blueprint, jsonify, request, send_file

from handlers.auth import get_current_user
from models import CreditCard, CreditCardGenerationRecord, db

logger = logging.getLogger(__name__)

credit_card_bp = Blueprint("admin_credit_cards", __name__)


@credit_card_bp.route("/api/admin/credit-card-generations")
def get_credit_card_generations():
    """获取所有信用卡生成记录"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    from models import Role, UserRoleRelation

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    generations_query = CreditCardGenerationRecord.query.order_by(
        CreditCardGenerationRecord.generated_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    generations_data = []
    for generation in generations_query.items:
        db.session.refresh(generation)
        card_count = len(generation.credit_cards)

        logger.debug(f"生成记录ID: {generation.id}")
        logger.debug(f"生成记录备注: {generation.notes}")
        logger.debug(f"数据库中的卡片数量: {card_count}")

        if card_count == 0:
            logger.warning(f"生成记录 {generation.id} 没有关联的信用卡！")
            from models import CreditCard

            related_cards = CreditCard.query.filter_by(generation_record_id=generation.id).count()
            logger.debug(f"数据库查询到的信用卡数量: {related_cards}")

        generations_data.append(
            {
                "id": generation.id,
                "generation_record_id": generation.id,
                "generated_at": generation.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "generated_by": generation.generated_by,
                "username": generation.user.username,
                "notes": generation.notes,
                "card_count": card_count,
            }
        )

    return jsonify(
        {
            "success": True,
            "generations": generations_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": generations_query.total,
                "pages": generations_query.pages,
            },
        }
    )


@credit_card_bp.route("/api/admin/credit-cards")
def get_credit_cards():
    """获取所有信用卡"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    from models import Role, UserRoleRelation

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    username = request.args.get("username", "").strip()
    cardholder_name = request.args.get("cardholder_name", "").strip()
    card_number = request.args.get("card_number", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    from models import User

    query = CreditCard.query

    if username:
        query = (
            query.join(CreditCardGenerationRecord)
            .join(User)
            .filter(User.username.like(f"%{username}%"))
        )

    if cardholder_name:
        query = query.filter(CreditCard.cardholder_name.like(f"%{cardholder_name}%"))

    if card_number:
        query = query.filter(CreditCard.card_number.like(f"%{card_number}%"))

    if username:
        query = query.distinct()

    cards_query = query.order_by(CreditCard.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    cards_data = []
    for card in cards_query.items:
        username = card.generation_record.user.username if card.generation_record else "未知"
        generation_record_id = card.generation_record.id if card.generation_record else None

        logger.debug(f"信用卡ID: {card.id}")
        logger.debug(f"生成记录ID: {generation_record_id}")
        logger.debug(f"生成记录对象: {card.generation_record}")

        cards_data.append(
            {
                "id": card.id,
                "cardholder_name": card.cardholder_name,
                "expiry_date": card.expiry_date,
                "card_number": card.card_number,
                "security_code": card.security_code,
                "recharge_status": card.recharge_status,
                "recharge_count": card.recharge_count,
                "generation_record_id": generation_record_id,
                "generated_by": (
                    card.generation_record.generated_by if card.generation_record else None
                ),
                "username": username,
                "created_at": card.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    return jsonify(
        {
            "success": True,
            "cards": cards_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": cards_query.total,
                "pages": cards_query.pages,
            },
        }
    )


@credit_card_bp.route("/api/admin/credit-card-generations", methods=["POST"])
def generate_credit_cards():
    """生成信用卡"""
    logging.basicConfig(level=logging.DEBUG)

    try:
        logger.debug("开始处理信用卡生成请求")

        user = get_current_user()
        if not user:
            logger.error("用户未登录")
            return jsonify({"success": False, "message": "未登录"}), 401

        from models import Role, UserRoleRelation

        admin_role = Role.query.filter_by(name="admin").first()
        if not admin_role:
            logger.error("管理员角色未配置")
            return jsonify({"success": False, "message": "管理员角色未配置"}), 500

        user_role_relation = UserRoleRelation.query.filter_by(
            user_id=user.id, role_id=admin_role.id
        ).first()

        if not user_role_relation:
            logger.error("用户权限不足")
            return jsonify({"success": False, "message": "权限不足"}), 403

        data = request.get_json()
        logger.debug(f"请求数据: {data}")

        title = data.get("title", "")
        count = data.get("count", 0)

        if not title:
            logger.error("标题为空")
            return jsonify({"success": False, "message": "标题不能为空"}), 400

        if not count or count < 1 or count > 1000:
            logger.error(f"信用卡数量无效: {count}")
            return (
                jsonify({"success": False, "message": "信用卡数量必须在1-1000之间"}),
                400,
            )

        logger.debug(f"开始生成信用卡，标题: {title}, 数量: {count}")

        generation_record = CreditCardGenerationRecord(generated_by=user.id, notes=title)
        db.session.add(generation_record)

        db.session.flush()
        logger.debug("已添加生成记录到数据库")

        fake = Faker("en_US")
        logger.debug("Faker初始化成功")

        for i in range(count):
            try:
                card_number = fake.credit_card_number(card_type="visa")
                logger.debug(f"生成第{i+1}张信用卡号: {card_number}")

                cardholder_name = fake.name()
                logger.debug(f"生成第{i+1}张信用卡持卡人: {cardholder_name}")

                expiry_date = (
                    datetime.now() + timedelta(days=365 * random.randint(1, 5))
                ).strftime("%m/%y")
                logger.debug(f"生成第{i+1}张信用卡有效期: {expiry_date}")

                security_code = fake.credit_card_security_code(card_type="visa")
                logger.debug(f"生成第{i+1}张信用卡安全码: {security_code}")

                credit_card = CreditCard(
                    cardholder_name=cardholder_name,
                    expiry_date=expiry_date,
                    card_number=card_number,
                    security_code=security_code,
                    recharge_status=True,
                    generation_record_id=generation_record.id,
                )
                db.session.add(credit_card)

                if (i + 1) % 100 == 0:
                    logger.debug(f"已生成{i+1}张信用卡，正在提交...")
                    db.session.commit()
                    db.session.refresh(generation_record)
                    logger.debug(
                        f"当前生成记录的卡片数量: " f"{len(generation_record.credit_cards)}"
                    )

            except Exception as card_error:
                logger.error(f"生成第{i+1}张信用卡时出错: {str(card_error)}")
                db.session.rollback()
                raise card_error

        db.session.commit()
        db.session.refresh(generation_record)
        actual_card_count = len(generation_record.credit_cards)
        logger.debug(f"生成记录ID: {generation_record.id}")
        logger.debug(f"请求生成数量: {count}")
        logger.debug(f"实际生成数量: {actual_card_count}")
        logger.debug(f"成功生成{actual_card_count}张信用卡")

        if actual_card_count != count:
            logger.warning(f"生成的卡片数量与请求不符！请求: {count}, 实际: {actual_card_count}")
        return jsonify({"success": True, "message": f"成功生成{count}张信用卡"})

    except Exception as e:
        logger.error(f"生成信用卡时发生错误: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({"success": False, "message": f"生成失败: {str(e)}"}), 500


@credit_card_bp.route("/api/admin/credit-card-generations/<int:generation_id>")
def get_credit_card_generation_detail(generation_id):
    """获取信用卡生成记录详情"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    from models import Role, UserRoleRelation

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    generation = CreditCardGenerationRecord.query.get(generation_id)
    if not generation:
        return jsonify({"success": False, "message": "生成记录不存在"}), 404

    cards = CreditCard.query.filter_by(generation_record_id=generation_id).all()

    generation_data = {
        "id": generation.id,
        "generated_at": generation.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
        "generated_by": generation.generated_by,
        "username": generation.user.username,
        "notes": generation.notes,
        "card_count": len(cards),
    }

    cards_data = []
    for card in cards:
        cards_data.append(
            {
                "id": card.id,
                "cardholder_name": card.cardholder_name,
                "expiry_date": card.expiry_date,
                "card_number": card.card_number,
                "security_code": card.security_code,
                "recharge_status": card.recharge_status,
                "recharge_count": card.recharge_count,
                "created_at": card.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    return jsonify(
        {
            "success": True,
            "generation": generation_data,
            "cards": cards_data,
        }
    )


@credit_card_bp.route("/api/admin/credit-card-generations/<int:generation_id>/export")
def export_credit_cards(generation_id):
    """导出信用卡数据为CSV或Excel"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    from models import Role, UserRoleRelation

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    generation = CreditCardGenerationRecord.query.get(generation_id)
    if not generation:
        return jsonify({"success": False, "message": "生成记录不存在"}), 404

    cards = CreditCard.query.filter_by(generation_record_id=generation_id).all()

    export_format = request.args.get("format", "csv")

    if export_format == "excel":
        data = []
        for card in cards:
            data.append(
                {
                    "持卡人姓名": card.cardholder_name,
                    "有效期": card.expiry_date,
                    "卡号": card.card_number,
                    "安全码": card.security_code,
                }
            )

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="信用卡数据")
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name=f"credit_cards_{generation_id}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["持卡人姓名", "有效期", "卡号", "安全码"])
        for card in cards:
            writer.writerow(
                [
                    card.cardholder_name,
                    card.expiry_date,
                    card.card_number,
                    card.security_code,
                ]
            )

        output.seek(0)
        output_bytes = io.BytesIO(output.getvalue().encode("utf-8-sig"))

        return send_file(
            output_bytes,
            as_attachment=True,
            download_name=f"credit_cards_{generation_id}.csv",
            mimetype="text/csv",
        )


@credit_card_bp.route("/api/admin/credit-cards/<int:card_id>/status", methods=["PUT"])
def update_credit_card_status(card_id):
    """更新信用卡状态"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "未登录"}), 401

    from models import Role, UserRoleRelation

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "message": "管理员角色未配置"}), 500

    user_role_relation = UserRoleRelation.query.filter_by(
        user_id=user.id, role_id=admin_role.id
    ).first()

    if not user_role_relation:
        return jsonify({"success": False, "message": "权限不足"}), 403

    card = CreditCard.query.get_or_404(card_id)
    data = request.get_json()
    action = data.get("action")

    if action == "invalidate":
        card.recharge_status = False
    elif action == "reset":
        card.recharge_status = True
        card.recharge_count = 0
    else:
        return jsonify({"success": False, "message": "无效的操作"}), 400

    try:
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "message": "操作成功",
                "card": {
                    "id": card.id,
                    "recharge_status": card.recharge_status,
                    "recharge_count": card.recharge_count,
                },
            }
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新信用卡状态时发生错误: {str(e)}")
        return jsonify({"success": False, "message": "操作失败"}), 500
