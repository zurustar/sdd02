import itertools
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app, db
from app.models import User
from config import TestConfig


@pytest.fixture()
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture()
def user_factory(app):
    """Factory fixture to create users for tests."""
    counter = itertools.count()

    def factory(*, username=None, password="Password123"):
        generated_username = username or f"user-{next(counter)}"
        user = User.query.filter_by(username=generated_username).one_or_none()
        if user is None:
            user = User(username=generated_username)
            db.session.add(user)
        user.set_password(password)
        db.session.commit()
        return user

    return factory
