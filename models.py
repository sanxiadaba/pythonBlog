"""三张表：文章、评论、管理员。单人博客不需要更多。"""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Article(db.Model):
    __tablename__ = "article"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(32), nullable=False, default="python", index=True)
    summary = db.Column(db.String(300), nullable=False, default="")
    body = db.Column(db.Text, nullable=False, default="")  # Markdown 原文，编辑时回填
    html = db.Column(db.Text, nullable=False, default="")  # 渲染结果，列表和详情直接用
    views = db.Column(db.Integer, nullable=False, default=0)
    published = db.Column(db.Boolean, nullable=False, default=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (db.Index("ix_article_feed", "published", "created"),)

    def __repr__(self):
        return f"<Article {self.id} {self.title!r}>"


class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(
        db.Integer, db.ForeignKey("article.id", ondelete="CASCADE"), nullable=False
    )
    nickname = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(1000), nullable=False)
    ip = db.Column(db.String(45))
    hidden = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)

    article = db.relationship(
        "Article",
        backref=db.backref(
            "comments", lazy="dynamic", cascade="all, delete-orphan", passive_deletes=True
        ),
    )

    __table_args__ = (db.Index("ix_comment_thread", "article_id", "hidden", "created"),)


class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
