import pytest
import json
from flask import session
from models import User, InviteRelation, db


class TestUserHandlers:
    """Test cases for user handlers."""

    def test_register_user_success(self, app):
        """Test successful user registration."""
        with app.app_context():
            # Create an existing user first
            existing_user = User(username="inviter")
            existing_user.invite_code = "12345678"
            existing_user.set_password("inviterpass")
            db.session.add(existing_user)
            db.session.commit()

            from handlers.auth import register_user

            data = {
                "username": "newuser",
                "password": "newpass123",
                "invite_code": existing_user.invite_code,
            }

            response = register_user(data)

            assert response.status_code == 200
            response_data = json.loads(response.get_data(as_text=True))
            assert response_data["success"] == True
            assert response_data["message"] == "注册成功"

            # Verify user was created
            new_user = User.query.filter_by(username="newuser").first()
            assert new_user is not None
            assert new_user.check_password("newpass123")

            # Verify invite relation was created
            relation = InviteRelation.query.filter_by(
                inviter_id=existing_user.id, invitee_id=new_user.id
            ).first()
            assert relation is not None

    def test_register_user_missing_fields(self, app):
        """Test registration with missing fields."""
        with app.app_context():
            from handlers.auth import register_user

            data = {"username": "testuser2"}  # Missing password and invite_code

            response = register_user(data)

            assert response.status_code == 400
            response_data = json.loads(response.get_data(as_text=True))
            assert response_data["success"] == False
            assert "请填写所有必填字段" in response_data["message"]

    def test_register_user_invalid_invite_code(self, app):
        """Test registration with invalid invite code."""
        with app.app_context():
            from handlers.auth import register_user

            data = {
                "username": "testuser2",
                "password": "testpass123",
                "invite_code": "invalid-code",
            }

            response = register_user(data)

            assert response.status_code == 400
            response_data = json.loads(response.get_data(as_text=True))
            assert response_data["success"] == False
            assert response_data["message"] == "邀请码不存在"

    def test_register_user_duplicate_username(self, app):
        """Test registration with existing username."""
        with app.app_context():
            # Create an existing user
            existing_user = User(username="testuser")
            existing_user.invite_code = "12345678"
            existing_user.set_password("testpass123")
            db.session.add(existing_user)
            db.session.commit()

            from handlers.auth import register_user

            data = {
                "username": "testuser",  # Duplicate username
                "password": "newpass123",
                "invite_code": existing_user.invite_code,
            }

            response = register_user(data)

            assert response.status_code == 400
            response_data = json.loads(response.get_data(as_text=True))
            assert response_data["success"] == False
            assert response_data["message"] == "用户名已存在"

    def test_login_user_success(self, app):
        """Test successful user login."""
        with app.app_context():
            # Create a test user
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

            from handlers.auth import login_user

            data = {"username": "testuser", "password": "testpass123"}

            response = login_user(data)

            assert response.status_code == 200
            response_data = json.loads(response.get_data(as_text=True))
            assert response_data["success"] == True
            assert response_data["message"] == "登录成功"

    def test_login_user_wrong_credentials(self, app):
        """Test login with wrong credentials."""
        with app.app_context():
            # Create a test user
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

            from handlers.auth import login_user

            data = {"username": "testuser", "password": "wrongpassword"}

            response = login_user(data)

            assert response.status_code == 401
            response_data = json.loads(response.get_data(as_text=True))
            assert response_data["success"] == False
            assert response_data["message"] == "密钥不存在或用户未注册"

    def test_login_user_missing_fields(self, app):
        """Test login with missing fields."""
        with app.app_context():
            from handlers.auth import login_user

            data = {"username": "testuser"}  # Missing password

            response = login_user(data)

            assert response.status_code == 400
            response_data = json.loads(response.get_data(as_text=True))
            assert response_data["success"] == False
            assert "请输入用户名和密码" in response_data["message"]

    def test_logout_user(self, app):
        """Test user logout."""
        with app.app_context():
            # Create a test user
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

            from handlers.auth import logout_user

            # First login to set session
            with app.test_client() as client:
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                response = logout_user()

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True

    def test_get_invite_code_authenticated(self, app):
        """Test getting invite code when authenticated."""
        with app.app_context():
            # Create a test user
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

            from handlers.auth import get_current_user
            from flask import jsonify

            def get_invite_code():
                user = get_current_user()
                if not user:
                    response = jsonify({"success": False, "message": "未登录"})
                    response.status_code = 401
                    return response

                return jsonify({"success": True, "invite_code": user.invite_code})

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                response = get_invite_code()

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert "invite_code" in response_data

    def test_get_invite_code_unauthenticated(self, app):
        """Test getting invite code when not authenticated."""
        with app.app_context():
            from handlers.auth import get_current_user
            from flask import jsonify

            def get_invite_code():
                user = get_current_user()
                if not user:
                    response = jsonify({"success": False, "message": "未登录"})
                    response.status_code = 401
                    return response

                return jsonify({"success": True, "invite_code": user.invite_code})

            response = get_invite_code()

            assert response.status_code == 401
            response_data = json.loads(response.get_data(as_text=True))
            assert response_data["success"] == False
            assert response_data["message"] == "未登录"

    def test_get_invite_stats_authenticated(self, app):
        """Test getting invite stats when authenticated."""
        with app.app_context():
            # Create a test user
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

            from handlers.auth import get_current_user
            from flask import jsonify

            def get_invite_stats():
                user = get_current_user()
                if not user:
                    response = jsonify({"success": False, "message": "未登录"})
                    response.status_code = 401
                    return response

                invited_count = InviteRelation.query.filter_by(inviter_id=user.id).count()

                return jsonify({"success": True, "invited_count": invited_count})

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                response = get_invite_stats()

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert "invited_count" in response_data

    def test_get_invite_stats_unauthenticated(self, app):
        """Test getting invite stats when not authenticated."""
        with app.app_context():
            from handlers.auth import get_current_user
            from flask import jsonify

            def get_invite_stats():
                user = get_current_user()
                if not user:
                    response = jsonify({"success": False, "message": "未登录"})
                    response.status_code = 401
                    return response

                invited_count = InviteRelation.query.filter_by(inviter_id=user.id).count()

                return jsonify({"success": True, "invited_count": invited_count})

            response = get_invite_stats()

            assert response.status_code == 401
            response_data = json.loads(response.get_data(as_text=True))
            assert response_data["success"] == False
            assert response_data["message"] == "未登录"
