"""后台：登录、文章增删改、评论管理、图片上传。"""

import functools
from datetime import datetime

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from config import CATEGORIES
from extensions import limiter
from models import Admin, Article, Comment, db
from utils import make_summary, render_markdown, save_image, verify_password

admin = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("admin.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@admin.route("/login", methods=["GET", "POST"])
@limiter.limit("10/minute", methods=["POST"])
def login():
    if session.get("admin_id"):
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        account = Admin.query.filter_by(username=username).first()
        if account and verify_password(password, account.password_hash):
            session.clear()
            session["admin_id"] = account.id
            target = request.args.get("next", "")
            # 只接受站内后台路径，避免登录页变成开放重定向的跳板。
            if not target.startswith("/admin"):
                target = url_for("admin.dashboard")
            return redirect(target)
        flash("用户名或密码不正确", "error")
    return render_template("login.html")


@admin.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("blog.index"))


@admin.get("/")
@login_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        article_count=Article.query.count(),
        published_count=Article.query.filter_by(published=True).count(),
        comment_count=Comment.query.count(),
        pending_comments=Comment.query.filter_by(hidden=True).count(),
        recent_comments=Comment.query.order_by(Comment.created.desc()).limit(8).all(),
        recent_articles=Article.query.order_by(Article.created.desc()).limit(8).all(),
    )


@admin.get("/articles")
@login_required
def articles():
    items = Article.query.order_by(Article.created.desc()).all()
    return render_template("admin/articles.html", articles=items)


@admin.route("/articles/new", methods=["GET", "POST"])
@login_required
def article_new():
    return _edit_article(None)


@admin.route("/articles/<int:article_id>/edit", methods=["GET", "POST"])
@login_required
def article_edit(article_id):
    return _edit_article(article_id)


def _edit_article(article_id):
    article = db.session.get(Article, article_id) if article_id else None
    if article_id and article is None:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "")
        category = request.form.get("category", "python")
        if category not in CATEGORIES:
            category = "python"
        published = request.form.get("published") == "on"

        if not title:
            flash("标题不能为空", "error")
        else:
            html = render_markdown(body)
            if article is None:
                article = Article(published=published)
                db.session.add(article)
            article.title = title
            article.body = body
            article.html = html
            article.category = category
            article.published = published
            article.summary = request.form.get("summary", "").strip() or make_summary(html)
            article.updated = datetime.now()
            db.session.commit()
            flash("已保存", "ok")
            return redirect(url_for("admin.articles"))

    return render_template(
        "admin/article_form.html", article=article, categories=CATEGORIES
    )


@admin.post("/articles/<int:article_id>/toggle")
@login_required
def article_toggle(article_id):
    article = db.session.get(Article, article_id) or abort(404)
    article.published = not article.published
    db.session.commit()
    flash("已隐藏" if not article.published else "已发布", "ok")
    return redirect(url_for("admin.articles"))


@admin.post("/articles/<int:article_id>/delete")
@login_required
def article_delete(article_id):
    article = db.session.get(Article, article_id) or abort(404)
    db.session.delete(article)
    db.session.commit()
    flash("文章已删除", "ok")
    return redirect(url_for("admin.articles"))


@admin.get("/comments")
@login_required
def comments():
    items = Comment.query.order_by(Comment.created.desc()).all()
    titles = {
        article.id: article.title
        for article in Article.query.filter(Article.id.in_({c.article_id for c in items})).all()
    }
    return render_template("admin/comments.html", comments=items, titles=titles)


@admin.post("/comments/<int:comment_id>/toggle")
@login_required
def comment_toggle(comment_id):
    comment = db.session.get(Comment, comment_id) or abort(404)
    comment.hidden = not comment.hidden
    db.session.commit()
    flash("已隐藏" if comment.hidden else "已恢复", "ok")
    return redirect(url_for("admin.comments"))


@admin.post("/comments/<int:comment_id>/delete")
@login_required
def comment_delete(comment_id):
    comment = db.session.get(Comment, comment_id) or abort(404)
    db.session.delete(comment)
    db.session.commit()
    flash("评论已删除", "ok")
    return redirect(url_for("admin.comments"))


@admin.post("/upload")
@login_required
def upload():
    file = request.files.get("image")
    if file is None or not file.filename:
        return jsonify(error="没有收到文件"), 400
    folder = datetime.now().strftime("%Y%m")
    limit = current_app.config["MAX_UPLOAD_BYTES"]
    try:
        name = save_image(
            file.read(limit + 1), current_app.config["UPLOAD_DIR"] / folder, limit
        )
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(url=url_for("static", filename=f"img/upload/{folder}/{name}"))
