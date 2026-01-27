import pytest
from flask import Flask
from config import config
from models import db, User, InviteRelation, MiningRule, MineUserRelation
import routes.user  # Import routes to register them
import routes.recharge  # Import recharge routes to register them
import routes.auth  # Import auth routes to register them
import routes.dashboard  # Import dashboard routes to register them


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    test_app = Flask(__name__, template_folder="../templates")
    test_app.config.from_object(config["testing"])

    db.init_app(test_app)

    # Register blueprints
    from routes.user import user_bp

    test_app.register_blueprint(user_bp)

    from routes.recharge import recharge_bp

    test_app.register_blueprint(recharge_bp)

    from routes.auth import auth_bp

    test_app.register_blueprint(auth_bp)

    from routes.dashboard import dashboard_bp

    test_app.register_blueprint(dashboard_bp)

    with test_app.app_context():
        db.create_all()

        yield test_app

        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
