import pytest
import json
import random
from decimal import Decimal
from flask import session
from models import db, User, CreditCard, Recharge, Config
import routes.recharge  # Import routes to register them


class TestRechargeCard:
    """Test cases for bank card recharge functionality."""

    def setup_method(self):
        """Set up test data for each test method."""
        # Create test user
        self.user = User(username="testuser")
        self.user.invite_code = "12345678"
        self.user.set_password("testpass123")
        self.user.balance = Decimal("0.00")
        db.session.add(self.user)

        # Create test credit card
        self.credit_card = CreditCard(
            cardholder_name="John Doe",
            card_number="1234567890123456",
            expiry_date="12/25",
            security_code="123",
            recharge_status=True,
            recharge_count=0,
        )
        db.session.add(self.credit_card)

        # Create configuration for max recharge amount
        self.max_recharge_config = Config(
            key="max_credit_card_recharge",
            value="10000.0",
            description="Maximum credit card recharge amount",
        )
        db.session.add(self.max_recharge_config)

        # Create success rate configurations
        self.first_success_config = Config(
            key="1_recharge_success_rate",
            value="1.0",  # 100% success for testing
            description="First recharge success rate",
        )
        db.session.add(self.first_success_config)

        self.second_success_config = Config(
            key="2_recharge_success_rate",
            value="0.0",  # 0% success for testing
            description="Second recharge success rate",
        )
        db.session.add(self.second_success_config)

        self.third_success_config = Config(
            key="3_recharge_success_rate",
            value="1.0",  # 100% success for testing
            description="Third recharge success rate",
        )
        db.session.add(self.third_success_config)

        self.fourth_success_config = Config(
            key="4_recharge_success_rate",
            value="0.0",  # 0% success for testing
            description="Fourth recharge success rate",
        )
        db.session.add(self.fourth_success_config)

        db.session.commit()

    def teardown_method(self):
        """Clean up test data after each test method."""
        db.session.remove()
        db.drop_all()
        db.create_all()

    def test_recharge_success_first_time(self, app):
        """Test successful recharge on first attempt."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first and get user_id from response
                login_response = client.post(
                    "/api/login", json={"username": "testuser", "password": "testpass123"}
                )
                assert login_response.status_code == 200
                login_data = json.loads(login_response.get_data(as_text=True))
                user_id = login_data.get("user_id")

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert response_data["message"] == "充值成功"
                assert "transaction_id" in response_data

                # Verify user balance was updated
                user = User.query.filter_by(username="testuser").first()
                assert user.balance == Decimal("100.0")

                # Verify credit card recharge count was updated
                card = CreditCard.query.filter_by(id=self.credit_card.id).first()
                assert card.recharge_count == 1

                # Verify recharge record was created
                recharge = Recharge.query.filter_by(user_id=self.user.id).first()
                assert recharge is not None
                assert recharge.amount == Decimal("100.0")
                assert recharge.method == "credit_card"
                assert recharge.status == "completed"
                assert recharge.bank_card_id == self.credit_card.id

    def test_recharge_failed_second_time(self, app):
        """Test failed recharge on second attempt."""
        with app.app_context():
            # Set up for second recharge attempt
            self.credit_card.recharge_count = 1
            db.session.commit()

            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "200.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值失敗 請聯繫發卡機構"

                # Verify user balance was NOT updated
                user = User.query.filter_by(username="testuser").first()
                assert user.balance == Decimal("0.00")

                # Verify credit card status was set to failed
                card = CreditCard.query.filter_by(id=self.credit_card.id).first()
                assert card.recharge_status == False
                assert card.recharge_count == 1  # Should remain unchanged

                # Verify recharge record was created with failed status
                recharge = Recharge.query.filter_by(user_id=self.user.id).first()
                assert recharge is not None
                assert recharge.amount == Decimal("200.0")
                assert recharge.method == "credit_card"
                assert recharge.status == "failed"
                assert recharge.bank_card_id == self.credit_card.id

    def test_recharge_amount_exceeds_limit(self, app):
        """Test recharge with amount exceeding maximum limit."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "15000.0",  # Exceeds max limit of 10000
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值失敗 請聯繫發卡機構"

                # Verify credit card status was set to failed
                card = CreditCard.query.filter_by(id=self.credit_card.id).first()
                assert card.recharge_status == False

                # Verify recharge record was created with failed status
                recharge = Recharge.query.filter_by(user_id=self.user.id).first()
                assert recharge is not None
                assert recharge.amount == Decimal("15000.0")
                assert recharge.status == "failed"

    def test_recharge_invalid_cardholder_name(self, app):
        """Test recharge with invalid cardholder name."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John123",  # Contains numbers
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "姓名格式不正確"

    def test_recharge_invalid_cardholder_name_special_chars(self, app):
        """Test recharge with cardholder name containing special characters."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John@Doe",  # Contains special characters
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "姓名格式不正確"

    def test_recharge_invalid_cardholder_name_empty(self, app):
        """Test recharge with empty cardholder name."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "",  # Empty name
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "姓名格式不正確"

    def test_recharge_invalid_card_number_too_short(self, app):
        """Test recharge with card number that is too short."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "123456789012345",  # 15 digits instead of 16
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "卡號需為16位數字"

    def test_recharge_invalid_card_number_too_long(self, app):
        """Test recharge with card number that is too long."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "12345678901234567",  # 17 digits instead of 16
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "卡號需為16位數字"

    def test_recharge_invalid_card_number_non_numeric(self, app):
        """Test recharge with non-numeric card number."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "123456789012345A",  # Contains letter
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "卡號需為16位數字"

    def test_recharge_invalid_cvv_too_short(self, app):
        """Test recharge with CVV that is too short."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "12",  # 2 digits instead of 3
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "安全码需為3位數字"

    def test_recharge_invalid_cvv_too_long(self, app):
        """Test recharge with CVV that is too long."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "1234",  # 4 digits instead of 3
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "安全码需為3位數字"

    def test_recharge_invalid_cvv_non_numeric(self, app):
        """Test recharge with non-numeric CVV."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "12A",  # Contains letter
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "安全码需為3位數字"

    def test_recharge_invalid_amount_negative(self, app):
        """Test recharge with negative amount."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "-100.0",  # Negative amount
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值金额必须大于0"

    def test_recharge_invalid_amount_zero(self, app):
        """Test recharge with zero amount."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "0.0",  # Zero amount
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值金额必须大于0"

    def test_recharge_invalid_amount_non_numeric(self, app):
        """Test recharge with non-numeric amount."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "abc",  # Non-numeric amount
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值金额格式不正确"

    def test_recharge_invalid_amount_empty(self, app):
        """Test recharge with empty amount."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "",  # Empty amount
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "请输入充值金额"

    def test_recharge_invalid_expiry_date(self, app):
        """Test recharge with invalid expiry date."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "invalid",  # Invalid expiry date
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "有效期格式不正确"

    def test_recharge_invalid_expiry_date_empty(self, app):
        """Test recharge with empty expiry date."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "",  # Empty expiry date
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "有效期格式不正确"

    def test_recharge_card_not_found(self, app):
        """Test recharge with non-existent credit card."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "Jane Doe",  # Different name
                    "card_number": "9999999999999999",  # Different card number
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值失敗 請聯繫發卡機構"

    def test_recharge_card_inactive(self, app):
        """Test recharge with inactive credit card."""
        with app.app_context():
            # Set credit card status to inactive
            self.credit_card.recharge_status = False
            db.session.commit()

            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值失敗 請聯繫發卡機構"

    def test_recharge_unauthenticated(self, app):
        """Test recharge without authentication."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 401
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "未登录"

    def test_recharge_fourth_attempt_always_fails(self, app):
        """Test that fourth recharge attempt always fails."""
        with app.app_context():
            # Set up for fourth recharge attempt
            self.credit_card.recharge_count = 3
            db.session.commit()

            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值失敗 請聯繫發卡機構"

                # Verify credit card status was set to failed
                card = CreditCard.query.filter_by(id=self.credit_card.id).first()
                assert card.recharge_status == False
                assert card.recharge_count == 3  # Should remain unchanged

    def test_recharge_fifth_attempt_always_fails(self, app):
        """Test that fifth and subsequent recharge attempts always fail."""
        with app.app_context():
            # Set up for fifth recharge attempt (card already failed)
            self.credit_card.recharge_count = 4
            self.credit_card.recharge_status = False
            db.session.commit()

            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值失敗 請聯繫發卡機構"

    def test_recharge_boundary_amount_max_limit(self, app):
        """Test recharge with amount exactly at maximum limit."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "10000.0",  # Exactly at max limit
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert response_data["message"] == "充值成功"

    def test_recharge_boundary_amount_just_under_max(self, app):
        """Test recharge with amount just under maximum limit."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "9999.99",  # Just under max limit
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert response_data["message"] == "充值成功"

    def test_recharge_boundary_amount_just_over_max(self, app):
        """Test recharge with amount just over maximum limit."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "10000.01",  # Just over max limit
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值失敗 請聯繫發卡機構"

    def test_recharge_boundary_amount_very_small(self, app):
        """Test recharge with very small amount."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "0.01",  # Very small amount
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert response_data["message"] == "充值成功"

    def test_recharge_missing_required_fields(self, app):
        """Test recharge with missing required fields."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                # Missing cardholder_name
                data = {
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "姓名格式不正確"

    def test_recharge_database_error_handling(self, app):
        """Test recharge with database error handling."""
        with app.app_context():
            from handlers.recharge import recharge_card
            from unittest.mock import patch

            # Mock database operations to raise an exception
            with patch("models.db.session.commit", side_effect=Exception("Database error")):
                with app.test_client() as client:
                    # Login first
                    client.post(
                        "/api/login", json={"username": "testuser", "password": "testpass123"}
                    )

                    data = {
                        "cardholder_name": "John Doe",
                        "card_number": "1234567890123456",
                        "expiry_date": "12/25",
                        "cvv": "123",
                        "amount": "100.0",
                    }

                    response = client.post("/api/recharge/card", data=data)

                    assert response.status_code == 500
                    response_data = json.loads(response.get_data(as_text=True))
                    assert response_data["success"] == False
                    assert response_data["message"] == "充值处理失败，请重试"

    def test_recharge_third_attempt_success(self, app):
        """Test successful recharge on third attempt."""
        with app.app_context():
            # Set up for third recharge attempt
            self.credit_card.recharge_count = 2
            db.session.commit()

            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "300.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert response_data["message"] == "充值成功"

                # Verify user balance was updated
                user = User.query.filter_by(username="testuser").first()
                assert user.balance == Decimal("300.0")

                # Verify credit card recharge count was updated
                card = CreditCard.query.filter_by(id=self.credit_card.id).first()
                assert card.recharge_count == 3

    def test_recharge_transaction_id_format(self, app):
        """Test that transaction ID is properly formatted."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True

                transaction_id = response_data["transaction_id"]
                assert transaction_id.startswith("TXN_")
                assert str(self.user.id) in transaction_id
                assert len(transaction_id) > 10  # Should be reasonably long

    def test_recharge_multiple_recharges_same_card(self, app):
        """Test multiple successful recharges on the same card."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                # First recharge
                data1 = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }
                response1 = client.post("/api/recharge/card", data=data1)
                assert response1.status_code == 200

                # Second recharge (should fail due to success rate)
                data2 = {
                    "cardholder_name": "John Doe",
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "200.0",
                }
                response2 = client.post("/api/recharge/card", data=data2)
                assert response2.status_code == 400

                # Verify final state
                user = User.query.filter_by(username="testuser").first()
                assert user.balance == Decimal("100.0")

                card = CreditCard.query.filter_by(id=self.credit_card.id).first()
                assert card.recharge_count == 1
                assert card.recharge_status == False

    def test_recharge_case_sensitive_cardholder_name(self, app):
        """Test that cardholder name matching is case sensitive."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "JOHN DOE",  # Different case
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 400
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == False
                assert response_data["message"] == "充值失敗 請聯繫發卡機構"

    def test_recharge_whitespace_in_cardholder_name(self, app):
        """Test recharge with whitespace in cardholder name."""
        with app.app_context():
            # Update credit card with name containing spaces
            self.credit_card.cardholder_name = "John  Doe"  # Multiple spaces
            db.session.commit()

            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "John  Doe",  # Multiple spaces
                    "card_number": "1234567890123456",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "amount": "100.0",
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert response_data["message"] == "充值成功"

    def test_recharge_whitespace_trimming(self, app):
        """Test that whitespace is properly trimmed from input fields."""
        with app.app_context():
            from handlers.recharge import recharge_card

            with app.test_client() as client:
                # Login first
                client.post("/api/login", json={"username": "testuser", "password": "testpass123"})

                data = {
                    "cardholder_name": "  John Doe  ",  # Whitespace around name
                    "card_number": "  1234567890123456  ",  # Whitespace around card number
                    "expiry_date": "  12/25  ",  # Whitespace around expiry date
                    "cvv": "  123  ",  # Whitespace around CVV
                    "amount": "  100.0  ",  # Whitespace around amount
                }

                response = client.post("/api/recharge/card", data=data)

                assert response.status_code == 200
                response_data = json.loads(response.get_data(as_text=True))
                assert response_data["success"] == True
                assert response_data["message"] == "充值成功"
