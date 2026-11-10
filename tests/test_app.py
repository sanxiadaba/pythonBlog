import hashlib
import re

from common.utility import sanitize_article_html, sanitize_plain_text
from constant import md5Salt
from extensions import db
from tests.conftest import login_as, seed_code


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
    seed_code(app, client, "captcha", "abcd")
    response = client.post(
        "/login",
        data={"username": "owner@example.com", "password": "password123", "logincode": "abcd"},
    )
    assert response.status_code == 200
    with app.app_context():
        users = db.metadata.tables["users"]
        password = db.session.execute(users.select().where(users.c.userid == 1)).one().password
        assert password.startswith("scrypt:")


def test_captcha_is_single_use(client, app):
    seed_code(app, client, "captcha", "abcd")
    first = client.post(
        "/login",
        data={"username": "owner@example.com", "password": "password123", "logincode": "abcd"},
    )
    assert first.status_code == 200
    # Re-arm the very same token: the row itself is gone, so it must not verify again.
    with client.session_transaction() as session:
        session["captcha_token"] = "test-captcha-abcd"
    second = client.post(
        "/login",
        data={"username": "owner@example.com", "password": "password123", "logincode": "abcd"},
    )
    assert second.text == "vcode-error"


def test_email_code_is_single_use(client, app):
    seed_code(app, client, "email", "abc123", subject="new@example.com")
    first = client.post(
        "/user", data={"username": "new@example.com", "password": "password123", "ecode": "abc123"}
    )
    assert first.text == "reg-pass"
    with client.session_transaction() as session:
        session["email_token"] = "test-email-abc123"
    second = client.post(
        "/user", data={"username": "new@example.com", "password": "password123", "ecode": "abc123"}
    )
    assert second.text == "ecode-error"


def test_password_reset_needs_the_code_that_was_mailed(client, app):
    seed_code(app, client, "email", "realcode", subject="owner@example.com")
    response = client.post(
        "/resetUserPassword",
        data={"username": "owner@example.com", "password": "Attack12345", "ecode": "guess"},
    )
    assert response.text == "ecode-error"
    seed_code(app, client, "email", "realcode2", subject="other@example.com")
    mixed = client.post(
        "/resetUserPassword",
        data={"username": "owner@example.com", "password": "Attack12345", "ecode": "realcode2"},
    )
    assert mixed.text == "ecode-error"


def test_session_cookie_never_carries_the_code(client, app, monkeypatch):
    import controler.user as user_module

    monkeypatch.setattr(user_module, "send_email", lambda *args, **kwargs: None)
    assert client.post("/ecode", data={"email": "owner@example.com", "n": 1}).text == "send-pass"
    with client.session_transaction() as session:
        assert not {"ecode", "ecode_email", "ecode_issued_at", "vcode"} & set(session.keys())
        assert session.get("email_token")


def test_password_reset_invalidates_existing_sessions(client, app):
    login_as(client, 1)
    assert client.get("/userManage").status_code == 200
    seed_code(app, client, "email", "reset1", subject="owner@example.com")
    response = client.post(
        "/resetUserPassword",
        data={"username": "owner@example.com", "password": "Newpass123", "ecode": "reset1"},
    )
    assert response.text == "fi-pass"
    assert client.get("/userManage").status_code == 403


def test_reply_is_stored_and_rendered(client, app, article_id):
    login_as(client, 1)
    assert client.post(
        "/comment", data={"articleid": article_id, "content": "a valid comment body"}
    ).text == "add-pass"
    with app.app_context():
        comments = db.metadata.tables["comment"]
        parent = db.session.execute(comments.select()).one()

    login_as(client, 2, nickname="other")
    reply = client.post(
        "/reply",
        data={"articleid": article_id, "commentid": parent.commentid, "content": "reply body text"},
    )
    assert reply.text == "reply-pass"
    with app.app_context():
        comments = db.metadata.tables["comment"]
        rows = db.session.execute(comments.select()).all()
        assert len(rows) == 2
        assert any(row.replyid == parent.commentid for row in rows)

    page = client.get(f"/article/{article_id}")
    assert page.status_code == 200
    assert "reply body text" in page.text


def test_unfavorite_actually_cancels(client, app, article_id):
    login_as(client, 1)
    assert client.post("/favorite", data={"articleid": article_id}).text == "favorite-pass"
    assert client.delete(f"/favorite/{article_id}").text == "cancel-pass"
    with app.app_context():
        favorites = db.metadata.tables["favorite"]
        assert db.session.execute(favorites.select()).one().canceled == 1


def test_user_manage_renders_with_favorites(client, app, article_id):
    login_as(client, 1)
    client.post("/favorite", data={"articleid": article_id})
    assert client.get("/userManage").status_code == 200


def test_admin_dashboard_keeps_paid_publishing_working(app, article_id):
    from constant import creditListForReleaseArticle

    admin = app.test_client()
    login_as(admin, 3, role="admin", nickname="admin")
    assert admin.get("/adminManage").status_code == 200
    assert creditListForReleaseArticle == [1, 2, 5, 10, 20, 50]

    author = app.test_client()
    login_as(author, 1)
    response = author.post(
        "/article",
        data={
            "headline": "A paid article title",
            "content": "<p>" + ("paid body " * 20) + "</p>",
            "type": 1,
            "credit": 1,
            "articleid": -1,
            "judgeType": 1,
        },
    )
    assert response.status_code == 200
    assert response.text.isdigit()


def test_csrf_is_enabled_by_default(tmp_path):
    from app import create_app

    database = tmp_path / "csrf.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database.as_posix()}",
            "RATELIMIT_ENABLED": False,
            "AUTO_INIT_DB": True,
        }
    )
    client = app.test_client()
    assert client.post("/login", data={}).status_code == 400
    page = client.get("/").text
    assert re.search(r'<meta name="csrf-token" content="[^"]+">', page)


def test_sanitizers_remove_active_markup():
    assert "script" not in sanitize_article_html('<script>alert(1)</script><p class="ok">text</p>')
    assert sanitize_plain_text("<b>Hello</b>") == "Hello"
    link = sanitize_article_html('<a href="https://example.com" target="_blank">x</a>')
    assert 'rel="noopener noreferrer"' in link
    assert sanitize_article_html('<a href="javascript:alert(1)">x</a>').find("javascript:") == -1
