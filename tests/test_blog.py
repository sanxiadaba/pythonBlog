"""访客侧行为：列表、详情、搜索、评论。"""

from models import Article, Comment, db
from tests.conftest import make_app


def test_home_on_empty_site(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "还没有文章" in response.get_data(as_text=True)


def test_article_listed_with_summary(client, article):
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert "第一篇" in body
    assert "摘要" in body


def test_article_detail_renders_html(client, article):
    response = client.get(f"/article/{article}")
    assert response.status_code == 200
    assert "<strong>粗体</strong>" in response.get_data(as_text=True)


def test_reading_article_increases_views(client, app, article):
    client.get(f"/article/{article}")
    client.get(f"/article/{article}")
    with app.app_context():
        assert db.session.get(Article, article).views == 2


def test_unpublished_article_is_hidden_from_guests(client, app, admin_user):
    with app.app_context():
        post = Article(title="草稿", body="x", html="<p>x</p>", published=False)
        db.session.add(post)
        db.session.commit()
        draft_id = post.id

    assert client.get(f"/article/{draft_id}").status_code == 404
    assert client.get("/").get_data(as_text=True).find("草稿") == -1


def test_unpublished_article_visible_to_admin(logged_in, app, admin_user):
    with app.app_context():
        post = Article(title="草稿", body="x", html="<p>x</p>", published=False)
        db.session.add(post)
        db.session.commit()
        draft_id = post.id

    assert logged_in.get(f"/article/{draft_id}").status_code == 200


def test_search_matches_title(client, article):
    assert "第一篇" in client.get("/?q=第一篇").get_data(as_text=True)
    assert "没有找到" in client.get("/?q=不存在").get_data(as_text=True)


def test_category_filter(client, app, admin_user):
    with app.app_context():
        db.session.add_all(
            [
                Article(title="Python 文", category="python", body="a", html="<p>a</p>"),
                Article(title="算法文", category="leetcode", body="b", html="<p>b</p>"),
            ]
        )
        db.session.commit()

    body = client.get("/?c=leetcode").get_data(as_text=True)
    assert "算法文" in body
    assert "Python 文" not in body


def test_comment_is_posted_and_shown(client, app, article):
    response = client.post(
        f"/article/{article}/comment",
        data={"nickname": "路人", "body": "写得不错"},
    )
    assert response.status_code == 302
    assert "写得不错" in client.get(f"/article/{article}").get_data(as_text=True)
    with app.app_context():
        assert Comment.query.count() == 1


def test_comment_needs_nickname_and_body(client, app, article):
    client.post(f"/article/{article}/comment", data={"nickname": "", "body": "有内容"})
    client.post(f"/article/{article}/comment", data={"nickname": "路人", "body": "  "})
    with app.app_context():
        assert Comment.query.count() == 0


def test_comment_too_long_is_rejected(client, app, article):
    client.post(f"/article/{article}/comment", data={"nickname": "路人", "body": "x" * 1001})
    with app.app_context():
        assert Comment.query.count() == 0


def test_hidden_comment_not_shown(client, app, article):
    with app.app_context():
        db.session.add(
            Comment(article_id=article, nickname="刷屏", body="广告", hidden=True)
        )
        db.session.commit()
    assert "广告" not in client.get(f"/article/{article}").get_data(as_text=True)


def test_comment_rate_limit(tmp_path):
    limited = make_app(tmp_path, RATELIMIT_ENABLED=True)
    with limited.app_context():
        post = Article(title="限流", body="x", html="<p>x</p>")
        db.session.add(post)
        db.session.commit()
        article_id = post.id

    with limited.test_client() as client:
        for _ in range(5):
            assert client.post(
                f"/article/{article_id}/comment", data={"nickname": "路人", "body": "hi"}
            ).status_code == 302
        response = client.post(
            f"/article/{article_id}/comment", data={"nickname": "路人", "body": "hi"}
        )
        assert response.status_code == 429
