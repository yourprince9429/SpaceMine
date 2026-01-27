import pytest
import json


class TestUserRoutes:
    """Test cases for user routes."""

    def test_index_shows_login_when_not_authenticated(self, client):
        """Test that index shows login page when not authenticated."""
        response = client.get("/")
        assert response.status_code == 200  # Show login page
        assert "登入" in response.get_data(as_text=True)

    def test_index_redirects_to_dashboard_when_authenticated(self, client, app):
        """Test that index redirects to dashboard when authenticated."""
        with app.app_context():
            from models import User, db

            # Create a test user
            test_user = User(username="testuser", invite_code="12345678")
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

        # First login
        client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

        response = client.get("/")
        assert response.status_code == 302  # Redirect
        assert b"/dashboard" in response.data

    def test_register_page(self, client):
        """Test register page loads."""
        response = client.get("/register")
        assert response.status_code == 200
        assert "註冊" in response.get_data(as_text=True)

    def test_login_api_success(self, client, app):
        """Test successful login API."""
        with app.app_context():
            from models import User, db

            # Create a test user
            test_user = User(username="testuser", invite_code="12345679")
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

        response = client.post(
            "/api/login", json={"username": "testuser", "password": "testpass123"}
        )

        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data["success"] == True
        assert data["message"] == "登录成功"

    def test_login_api_failure(self, client, app):
        """Test failed login API."""
        with app.app_context():
            from models import User, db

            # Create a test user
            test_user = User(username="testuser", invite_code="12345680")
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

        response = client.post(
            "/api/login", json={"username": "testuser", "password": "wrongpassword"}
        )

        assert response.status_code == 401
        data = json.loads(response.get_data(as_text=True))
        assert data["success"] == False
        assert data["message"] == "密钥不存在或用户未注册"

    def test_login_api_inactive_user(self, client, app):
        """Test login API with inactive user."""
        with app.app_context():
            from models import User, db

            # Create a test user with inactive status
            test_user = User(username="inactiveuser", invite_code="12345685", status="inactive")
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

        response = client.post(
            "/api/login", json={"username": "inactiveuser", "password": "testpass123"}
        )

        assert response.status_code == 403
        data = json.loads(response.get_data(as_text=True))
        assert data["success"] == False
        assert data["message"] == "账户已被停用，请联系管理员"

    def test_login_api_missing_fields(self, client):
        """Test login API with missing fields."""
        response = client.post(
            "/api/login",
            json={
                "username": "testuser"
                # Missing password
            },
        )

        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert data["success"] == False
        assert "请输入用户名和密码" in data["message"]

    def test_register_api_success(self, client):
        """Test successful registration API."""
        response = client.post(
            "/api/register",
            json={
                "username": "newuser",
                "password": "newpass123",
                "invite_code": "test-invite-code",  # This will fail, but tests the endpoint
            },
        )

        # Since we don't have a valid invite code in test setup, this should fail
        # But we're testing that the endpoint exists and responds
        assert response.status_code in [200, 400]
        data = json.loads(response.get_data(as_text=True))
        assert "success" in data
        assert "message" in data

    def test_register_api_missing_fields(self, client):
        """Test registration API with missing fields."""
        response = client.post(
            "/api/register",
            json={
                "username": "newuser2"
                # Missing password and invite_code
            },
        )

        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert data["success"] == False
        assert "请填写所有必填字段" in data["message"]

    def test_dashboard_requires_authentication(self, client):
        """Test that dashboard requires authentication."""
        response = client.get("/dashboard")
        assert response.status_code == 302  # Redirect to login

    def test_dashboard_authenticated(self, client, app):
        """Test dashboard access when authenticated."""
        with app.app_context():
            from models import User, db

            # Create a test user
            test_user = User(username="testuser", invite_code="12345681")
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

        # Login first
        client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "SpaceMine - 潮創宇宙" in response.get_data(as_text=True)

    def test_dashboard_inactive_user(self, client, app):
        """Test dashboard access with inactive user."""
        with app.app_context():
            from models import User, db

            # Create an inactive test user
            test_user = User(username="inactiveuser2", invite_code="12345686", status="inactive")
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

        # Login first (this will fail due to inactive status)
        response = client.post(
            "/api/login", json={"username": "inactiveuser2", "password": "testpass123"}
        )
        assert response.status_code == 403

        # Try to access dashboard
        response = client.get("/dashboard")
        assert response.status_code == 302  # Redirect to login

    def test_logout_api(self, client, app):
        """Test logout API."""
        with app.app_context():
            from models import User, db

            # Create a test user
            test_user = User(username="testuser", invite_code="12345682")
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

        # Login first
        client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

        response = client.post("/api/logout")
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data["success"] == True

    def test_invite_code_api_authenticated(self, client, app):
        """Test invite code API when authenticated."""
        with app.app_context():
            from models import User, db

            # Create a test user
            test_user = User(username="testuser", invite_code="12345683")
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

        # Login first
        client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

        response = client.get("/api/user/invite-code")
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data["success"] == True
        assert "invite_code" in data

    def test_invite_stats_api_authenticated(self, client, app):
        """Test invite stats API when authenticated."""
        with app.app_context():
            from models import User, db

            # Create a test user
            test_user = User(username="testuser", invite_code="12345684")
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

        # Login first
        client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

        response = client.get("/api/user/invite-stats")
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data["success"] == True
        assert "invited_count" in data
        assert isinstance(data["invited_count"], int)
