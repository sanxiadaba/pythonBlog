"""访客侧：文章列表、文章详情、评论。"""

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import or_
from sqlalchemy.orm import load_only

from config import CATEGORIES, COMMENT_MAX_LENGTH, NICKNAME_MAX_LENGTH, PAGE_SIZE
from extensions import limiter
from models import Article, Comment, db

blog = Blueprint("blog", __name__)

# 列表只要摘要，不需要把正文和渲染结果整篇读出来。
_LIST = load_only(
    Article.id, Article.title, Article.category, Article.summary, Article.views, Article.created
)
_NEIGHBOUR = load_only(Article.id, Article.title)
_DETAIL = load_only(
    Article.id,
    Article.title,
    Article.category,
    Article.html,
    Article.views,
    Article.published,
    Article.created,
)


def _like(keyword: str) -> str:
    """把用户输入当字面量匹配，`%` 和 `_` 不再当通配符。"""
    escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


@blog.get("/")
def index():
    page = request.args.get("page", 1, type=int)
    category = request.args.get("c", "").strip()
    keyword = request.args.get("q", "").strip()

    query = Article.query.filter_by(published=True)
    if category in CATEGORIES:
        query = query.filter_by(category=category)
    else:
        category = ""
    if keyword:
        pattern = _like(keyword)
        query = query.filter(
            or_(
                Article.title.like(pattern, escape="\\"),
                Article.body.like(pattern, escape="\\"),
            )
        )

    pagination = (
        query.options(_LIST)
        .order_by(Article.created.desc())
        .paginate(page=max(page, 1), per_page=PAGE_SIZE, error_out=False)
    )
    return render_template("index.html", pagination=pagination, category=category, keyword=keyword)


@blog.get("/article/<int:article_id>")
def article(article_id):
    article = db.session.get(Article, article_id, options=[_DETAIL])
    if article is None or (not article.published and not session.get("admin_id")):
        abort(404)
    # 自己预览不算阅读量。
    if article.published and not session.get("admin_id"):
        Article.query.filter_by(id=article.id).update({"views": Article.views + 1})
        db.session.commit()
    comments = (
        Comment.query.filter_by(article_id=article.id, hidden=False)
        .order_by(Comment.created.asc())
        .all()
    )
    older = (
        Article.query.options(_NEIGHBOUR)
        .filter(Article.published.is_(True), Article.created < article.created)
        .order_by(Article.created.desc())
        .first()
    )
    newer = (
        Article.query.options(_NEIGHBOUR)
        .filter(Article.published.is_(True), Article.created > article.created)
        .order_by(Article.created.asc())
        .first()
    )
    return render_template(
        "article.html", article=article, comments=comments, older=older, newer=newer
    )


@blog.post("/article/<int:article_id>/comment")
@limiter.limit("5/minute")
def add_comment(article_id):
    article = db.session.get(Article, article_id, options=[_NEIGHBOUR])
    if article is None or not article.published:
        abort(404)

    nickname = request.form.get("nickname", "").strip()
    body = request.form.get("body", "").strip()
    if not nickname or not body:
        flash("昵称和内容都不能为空", "error")
    elif len(nickname) > NICKNAME_MAX_LENGTH or len(body) > COMMENT_MAX_LENGTH:
        flash("昵称或内容超出长度限制", "error")
    else:
        db.session.add(
            Comment(
                article_id=article.id,
                nickname=nickname,
                body=body,
                ip=request.remote_addr,
            )
        )
        db.session.commit()
        flash("评论已发布", "ok")
    return redirect(url_for("blog.article", article_id=article_id) + "#comments")
