from datetime import datetime

import pytest

from app import create_app
from common.initDatabase import create_user
from extensions import db


@pytest.fixture()
def app(tmp_path):
    database = tmp_path / "test.db"
    app = create_app(
        {
            "TESTING": True,
            "DEBUG": False,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database.as_posix()}",
            "WTF_CSRF_ENABLED": False,
            "RATELIMIT_ENABLED": False,
        }
    )
    with app.app_context():
        create_user("owner@example.com", "password123", role="user", nickname="owner")
        create_user("other@example.com", "password123", role="user", nickname="other")
        create_user("admin@example.com", "password123", role="admin", nickname="admin")
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login_as(client, user_id, role="user", nickname="tester"):
    with client.session_transaction() as session:
        session.update(islogin="true", userid=user_id, role=role, nickname=nickname)


@pytest.fixture()
def article_id(app):
    with app.app_context():
        article = db.metadata.tables["article"]
        result = db.session.execute(
            article.insert().values(
                userid=1,
                type=1,
                headline="A test article",
                content="article body " * 20,
                thumbnail="default/1.jpg",
                credit=0,
                drafted=0,
                checked=1,
                createtime=datetime.now(),
                updatetime=datetime.now(),
            )
        )
        db.session.commit()
        return result.inserted_primary_key[0]
