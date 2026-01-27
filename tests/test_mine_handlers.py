import pytest
import json
from models import User, MiningRule, MineUserRelation, db


class TestMineHandlers:
    """Test cases for mine handlers."""

    def test_open_mine_success(self, app):
        """Test successful mine opening."""
        with app.app_context():
            # Create a test user with sufficient balance
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            test_user.balance = 500.0
            db.session.add(test_user)
            db.session.commit()

            # Create a mining rule
            mining_rule = MiningRule(
                code="basic",
                name="初始矿场",
                miners_consumed=100,
                cycle_days=5,
                energy_reward=110.0,
                background_image="k1.png",
            )
            db.session.add(mining_rule)
            db.session.commit()

            from handlers.mine import open_mine
            from flask import request

            data = {"type_code": "basic"}

            with app.test_request_context("/api/mine/open", method="POST", json=data):
                # Set up session to simulate logged in user
                from flask import session

                session["user_id"] = test_user.id

                response = open_mine()

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert response_data["message"] == "開啟成功"

                # Verify user balance was deducted
                db.session.refresh(test_user)
                assert float(test_user.balance) == 400.0

                # Verify mine user relation was created
                relation = MineUserRelation.query.filter_by(
                    user_id=test_user.id, mine_id=mining_rule.id
                ).first()
                assert relation is not None
                assert relation.is_active == True
                assert relation.mine_code == "basic"

    def test_open_mine_insufficient_balance(self, app):
        """Test mine opening with insufficient balance."""
        with app.app_context():
            # Create a test user with insufficient balance
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            test_user.balance = 50.0
            db.session.add(test_user)
            db.session.commit()

            # Create a mining rule
            mining_rule = MiningRule(
                code="basic",
                name="初始矿场",
                miners_consumed=100,
                cycle_days=5,
                energy_reward=110.0,
                background_image="k1.png",
            )
            db.session.add(mining_rule)
            db.session.commit()

            from handlers.mine import open_mine

            data = {"type_code": "basic"}

            with app.test_request_context("/api/mine/open", method="POST", json=data):
                # Set up session to simulate logged in user
                from flask import session

                session["user_id"] = test_user.id

                response = open_mine()

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert "礦工數不足" in response_data["message"]

                # Verify user balance was not changed
                db.session.refresh(test_user)
                assert float(test_user.balance) == 50.0

    def test_open_mine_already_activated(self, app):
        """Test opening a mine that's already activated."""
        with app.app_context():
            # Create a test user with sufficient balance
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            test_user.balance = 500.0
            db.session.add(test_user)
            db.session.commit()

            # Create a mining rule
            mining_rule = MiningRule(
                code="basic",
                name="初始矿场",
                miners_consumed=100,
                cycle_days=5,
                energy_reward=110.0,
                background_image="k1.png",
            )
            db.session.add(mining_rule)
            db.session.commit()

            # Create an existing mine user relation
            relation = MineUserRelation(
                user_id=test_user.id, mine_id=mining_rule.id, mine_code="basic", is_active=True
            )
            db.session.add(relation)
            db.session.commit()

            from handlers.mine import open_mine

            data = {"type_code": "basic"}

            with app.test_request_context("/api/mine/open", method="POST", json=data):
                # Set up session to simulate logged in user
                from flask import session

                session["user_id"] = test_user.id

                response = open_mine()

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert "该类型已在挖礦" in response_data["message"]

    def test_open_mine_inactive_relation(self, app):
        """Test opening a mine when relation exists but is inactive."""
        with app.app_context():
            # Create a test user with sufficient balance
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            test_user.balance = 500.0
            db.session.add(test_user)
            db.session.commit()

            # Create a mining rule
            mining_rule = MiningRule(
                code="basic",
                name="初始矿场",
                miners_consumed=100,
                cycle_days=5,
                energy_reward=110.0,
                background_image="k1.png",
            )
            db.session.add(mining_rule)
            db.session.commit()

            # Create an existing but inactive mine user relation
            relation = MineUserRelation(
                user_id=test_user.id, mine_id=mining_rule.id, mine_code="basic", is_active=False
            )
            db.session.add(relation)
            db.session.commit()

            from handlers.mine import open_mine

            data = {"type_code": "basic"}

            with app.test_request_context("/api/mine/open", method="POST", json=data):
                # Set up session to simulate logged in user
                from flask import session

                session["user_id"] = test_user.id

                response = open_mine()

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert response_data["message"] == "開啟成功"

                # Verify user balance was deducted
                db.session.refresh(test_user)
                assert float(test_user.balance) == 400.0

                # Verify a new active relation was created
                active_relations = MineUserRelation.query.filter_by(
                    user_id=test_user.id, mine_id=mining_rule.id, is_active=True
                ).all()
                assert len(active_relations) == 1

    def test_open_mine_invalid_type_code(self, app):
        """Test opening a mine with invalid type code."""
        with app.app_context():
            # Create a test user with sufficient balance
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            test_user.balance = 500.0
            db.session.add(test_user)
            db.session.commit()

            from handlers.mine import open_mine

            data = {"type_code": "invalid_code"}

            with app.test_request_context("/api/mine/open", method="POST", json=data):
                # Set up session to simulate logged in user
                from flask import session

                session["user_id"] = test_user.id

                response = open_mine()

                assert response.status_code == 404
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert "矿场类型不存在" in response_data["message"]

    def test_open_mine_missing_type_code(self, app):
        """Test opening a mine without type code."""
        with app.app_context():
            # Create a test user
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

            from handlers.mine import open_mine

            data = {}

            with app.test_request_context("/api/mine/open", method="POST", json=data):
                # Set up session to simulate logged in user
                from flask import session

                session["user_id"] = test_user.id

                response = open_mine()

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert "缺少矿场类型代码" in response_data["message"]

    def test_open_mine_unauthenticated(self, app):
        """Test opening a mine when not authenticated."""
        with app.app_context():
            from handlers.mine import open_mine

            data = {"type_code": "basic"}

            with app.test_request_context("/api/mine/open", method="POST", json=data):
                response = open_mine()

                assert response.status_code == 401
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "未登录"

    def test_get_user_mines(self, app):
        """Test getting user mines list."""
        with app.app_context():
            # Create a test user
            test_user = User(username="testuser")
            test_user.invite_code = "12345678"
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()

            # Create mining rules
            mining_rule1 = MiningRule(
                code="basic",
                name="初始矿场",
                miners_consumed=100,
                cycle_days=5,
                energy_reward=110.0,
                background_image="k1.png",
            )
            mining_rule2 = MiningRule(
                code="small",
                name="小型矿场",
                miners_consumed=500,
                cycle_days=9,
                energy_reward=600.0,
                background_image="k2.png",
            )
            db.session.add(mining_rule1)
            db.session.add(mining_rule2)
            db.session.commit()

            # Create a mine user relation for the first rule
            relation = MineUserRelation(
                user_id=test_user.id, mine_id=mining_rule1.id, mine_code="basic", is_active=True
            )
            db.session.add(relation)
            db.session.commit()

            from handlers.mine import get_user_mines

            with app.test_request_context("/api/user/mines"):
                # Set up session to simulate logged in user
                from flask import session

                session["user_id"] = test_user.id

                response = get_user_mines()

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert "mines" in response_data
                assert len(response_data["mines"]) == 2

                # Check first mine is activated
                mine1 = next((m for m in response_data["mines"] if m["code"] == "basic"), None)
                assert mine1 is not None
                assert mine1["is_activated"] == True

                # Check second mine is not activated
                mine2 = next((m for m in response_data["mines"] if m["code"] == "small"), None)
                assert mine2 is not None
                assert mine2["is_activated"] == False
