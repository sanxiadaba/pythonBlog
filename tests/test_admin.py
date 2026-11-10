"""后台：登录、文章读写、评论管理、图片上传。"""

from io import BytesIO

from models import Article, Comment, db
from tests.conftest import make_app


def test_admin_pages_require_login(client):
    for path in ("/admin/", "/admin/articles", "/admin/comments"):
        response = client.get(path)
        assert response.status_code == 302
        assert "/admin/login" in response.headers["Location"]


def test_login_page_renders(client):
    assert client.get("/admin/login").status_code == 200


def test_login_with_wrong_password_fails(client, admin_user):
    response = client.post("/admin/login", data={"username": "admin", "password": "wrong"})
    assert "密码不正确" in response.get_data(as_text=True)
    assert client.get("/admin/").status_code == 302


def test_login_then_dashboard(logged_in):
    assert "概览" in logged_in.get("/admin/").get_data(as_text=True)


def test_logout(logged_in):
    logged_in.post("/admin/logout")
    assert logged_in.get("/admin/").status_code == 302


def test_create_article_from_form(logged_in, app):
    response = logged_in.post(
        "/admin/articles/new",
        data={
            "title": "新文章",
            "category": "learning",
            "body": "## 小标题\n\n`code` 和 **重点**",
            "published": "on",
        },
    )
    assert response.status_code == 302
    with app.app_context():
        post = Article.query.one()
        assert post.title == "新文章"
        assert post.category == "learning"
        assert "<h2>小标题</h2>" in post.html
        assert post.summary  # 摘要自动生成


def test_markdown_escapes_raw_html(logged_in, app):
    logged_in.post(
        "/admin/articles/new",
        data={"title": "安全", "body": "<script>alert(1)</script>", "published": "on"},
    )
    page = logged_in.get("/").get_data(as_text=True)
    with app.app_context():
        post = Article.query.one()
    assert "<script>" not in post.html
    assert "&lt;script&gt;" in post.html
    assert "<script>alert(1)</script>" not in page


def test_edit_article(logged_in, app, article):
    logged_in.post(
        f"/admin/articles/{article}/edit",
        data={"title": "改过的标题", "body": "新正文", "category": "python"},
    )
    with app.app_context():
        post = db.session.get(Article, article)
        assert post.title == "改过的标题"
        assert post.published is False  # 没勾"发布"


def test_toggle_publish(logged_in, app, article):
    logged_in.post(f"/admin/articles/{article}/toggle")
    with app.app_context():
        assert db.session.get(Article, article).published is False


def test_delete_article_cascades_comments(logged_in, app, article):
    with app.app_context():
        db.session.add(Comment(article_id=article, nickname="路人", body="评论"))
        db.session.commit()

    logged_in.post(f"/admin/articles/{article}/delete")
    with app.app_context():
        assert Article.query.count() == 0
        assert Comment.query.count() == 0


def test_hide_and_delete_comment(logged_in, app, article):
    with app.app_context():
        comment = Comment(article_id=article, nickname="路人", body="评论")
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id

    logged_in.post(f"/admin/comments/{comment_id}/toggle")
    with app.app_context():
        assert db.session.get(Comment, comment_id).hidden is True

    logged_in.post(f"/admin/comments/{comment_id}/delete")
    with app.app_context():
        assert db.session.get(Comment, comment_id) is None


def test_upload_rejects_non_image(logged_in):
    response = logged_in.post(
        "/admin/upload",
        data={"image": (BytesIO(b"not an image"), "x.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "图片" in response.get_json()["error"]


def test_upload_accepts_image(logged_in, png_bytes):
    response = logged_in.post(
        "/admin/upload",
        data={"image": (BytesIO(png_bytes), "x.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.get_json()["url"].endswith(".jpg")


def test_upload_requires_login(client, png_bytes):
    response = client.post(
        "/admin/upload",
        data={"image": (BytesIO(png_bytes), "x.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 302


def test_csrf_blocks_post_without_token(tmp_path, admin_user):
    guarded = make_app(tmp_path, WTF_CSRF_ENABLED=True)
    with guarded.test_client() as client:
        response = client.post(
            "/admin/login", data={"username": "admin", "password": "password123"}
        )
    assert response.status_code == 400


def test_preview_returns_exactly_what_saving_would(logged_in, app):
    body = "## 小标题\n\n```python\nprint(1)\n```\n\n正文"
    preview = logged_in.post("/admin/preview", data={"body": body})
    assert preview.status_code == 200
    logged_in.post(
        "/admin/articles/new",
        data={"title": "同一份渲染", "body": body, "published": "on"},
    )
    with app.app_context():
        assert preview.get_json()["html"] == Article.query.one().html


def test_preview_requires_login(client):
    assert client.post("/admin/preview", data={"body": "x"}).status_code == 302


def test_code_block_is_highlighted_on_save(logged_in, app):
    logged_in.post(
        "/admin/articles/new",
        data={"title": "代码", "body": "```python\nprint(1)\n```", "published": "on"},
    )
    with app.app_context():
        html = Article.query.one().html
    assert '<div class="highlight">' in html
    assert '<span class="nb">print</span>' in html


def test_summary_follows_body_when_not_overridden(logged_in, app, article):
    logged_in.post(
        f"/admin/articles/{article}/edit",
        data={"title": "第一篇", "body": "换了正文内容", "category": "python", "published": "on"},
    )
    with app.app_context():
        assert "换了正文内容" in db.session.get(Article, article).summary


def test_summary_ignores_code_and_tables(logged_in, app):
    logged_in.post(
        "/admin/articles/new",
        data={
            "title": "摘要",
            "body": "正文第一段\n\n```python\nprint(1)\n```\n\n| 列 | 值 |\n| - | - |\n| a | 1 |",
            "published": "on",
        },
    )
    with app.app_context():
        assert Article.query.one().summary == "正文第一段"


def test_typed_summary_is_kept(logged_in, app, article):
    logged_in.post(
        f"/admin/articles/{article}/edit",
        data={
            "title": "第一篇",
            "body": "正文",
            "summary": "自己写的摘要",
            "category": "python",
            "published": "on",
        },
    )
    with app.app_context():
        assert db.session.get(Article, article).summary == "自己写的摘要"


def test_editor_no_longer_needs_browser_side_markdown(logged_in, article):
    page = logged_in.get(f"/admin/articles/{article}/edit").get_data(as_text=True)
    assert "/static/vendor/" not in page
    assert "marked" not in page
