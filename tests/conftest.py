"""测试夹具：每个测试一个临时 SQLite 库。"""

import pytest
from PIL import Image

from app import create_app
from models import Admin, Article, db
from utils import hash_password


def make_app(tmp_path, **overrides):
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,
        "RATELIMIT_ENABLED": False,
        "UPLOAD_DIR": tmp_path / "upload",
    }
    config.update(overrides)
    return create_app(config)


@pytest.fixture
def app(tmp_path):
    return make_app(tmp_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_user(app):
    with app.app_context():
        account = Admin(username="admin", password_hash=hash_password("password123"))
        db.session.add(account)
        db.session.commit()
        return account.id


@pytest.fixture
def logged_in(client, admin_user):
    client.post("/admin/login", data={"username": "admin", "password": "password123"})
    return client


@pytest.fixture
def article(app):
    with app.app_context():
        post = Article(
            title="第一篇",
            category="python",
            summary="摘要",
            body="**粗体**正文",
            html="<p><strong>粗体</strong>正文</p>",
        )
        db.session.add(post)
        db.session.commit()
        return post.id


@pytest.fixture
def png_bytes():
    from io import BytesIO

    buffer = BytesIO()
    Image.new("RGB", (32, 32), (10, 20, 30)).save(buffer, format="PNG")
    return buffer.getvalue()
