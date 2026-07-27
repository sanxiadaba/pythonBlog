import hashlib
import re

from common.utility import sanitize_article_html, sanitize_plain_text
from constant import md5Salt
from extensions import db
from tests.conftest import login_as


def test_public_pages_and_security_headers(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert client.get("/healthz").json == {"status": "ok"}


def test_anonymous_and_role_access(client):
    assert client.get("/adminManage").status_code == 401
    assert client.get("/prepost").status_code == 302
    login_as(client, 1)
    assert client.get("/adminManage").status_code == 403
    login_as(client, 3, role="admin", nickname="admin")
    assert client.get("/adminManage").status_code == 200


def test_only_owner_or_admin_can_delete_article(client, app, article_id):
    login_as(client, 2)
    assert client.post("/deleteArticle", data={"articleid": article_id}).status_code == 403

    login_as(client, 1)
    assert client.post("/deleteArticle", data={"articleid": article_id}).data == b"1"
    with app.app_context():
        article = db.metadata.tables["article"]
        row = db.session.execute(article.select().where(article.c.articleid == article_id)).one()
        assert row.hide == 1 and row.delete == 1


def test_article_state_and_html_are_server_controlled(client, app):
    login_as(client, 1)
    content = "<p>" + ("safe text " * 15) + "</p><script>alert(1)</script>"
    response = client.post(
        "/article",
        data={
            "headline": "Valid article title",
            "content": content,
            "type": 1,
            "credit": 0,
            "drafted": 0,
            "checked": 1,
            "articleid": -1,
            "judgeType": 3,
        },
    )
    assert response.status_code == 200
    article_id = int(response.text)
    with app.app_context():
        article = db.metadata.tables["article"]
        row = db.session.execute(article.select().where(article.c.articleid == article_id)).one()
        assert row.checked == 0 and row.drafted == 0
        assert "<script" not in row.content


def test_legacy_password_is_migrated_on_login(client, app):
    legacy = hashlib.md5(("password123" + md5Salt).encode()).hexdigest()
    with app.app_context():
        users = db.metadata.tables["users"]
        db.session.execute(users.update().where(users.c.userid == 1).values(password=legacy))
        db.session.commit()
    with client.session_transaction() as session:
        session["vcode"] = "abcd"
    response = client.post(
        "/login",
        data={"username": "owner@example.com", "password": "password123", "logincode": "abcd"},
    )
    assert response.status_code == 200
    with app.app_context():
        users = db.metadata.tables["users"]
        password = db.session.execute(users.select().where(users.c.userid == 1)).one().password
        assert password.startswith("scrypt:")


def test_csrf_is_enabled_by_default(tmp_path):
    from app import create_app

    database = tmp_path / "csrf.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database.as_posix()}",
            "RATELIMIT_ENABLED": False,
        }
    )
    client = app.test_client()
    assert client.post("/login", data={}).status_code == 400
    page = client.get("/").text
    assert re.search(r'<meta name="csrf-token" content="[^"]+">', page)


def test_sanitizers_remove_active_markup():
    assert "script" not in sanitize_article_html('<script>alert(1)</script><p class="ok">text</p>')
    assert sanitize_plain_text("<b>Hello</b>") == "Hello"
