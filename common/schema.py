from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
)


def define_schema(metadata: MetaData) -> None:
    if "users" in metadata.tables:
        return

    users = Table(
        "users",
        metadata,
        Column("userid", Integer, primary_key=True, autoincrement=True),
        Column("username", String(254), nullable=False, unique=True),
        Column("password", String(255), nullable=False),
        Column("nickname", String(50)),
        Column("avatar", String(200)),
        Column("qq", String(20)),
        Column("role", String(10), nullable=False, default="user", server_default="user"),
        Column("credit", Integer, nullable=False, default=50, server_default="50"),
        Column("createtime", DateTime),
        Column("apply", Integer, default=0, server_default="0"),
        Column("agreeEditor", Integer, default=0, server_default="0"),
        Column("forbidLogin", Integer, default=0, server_default="0"),
    )

    article = Table(
        "article",
        metadata,
        Column("articleid", Integer, primary_key=True, autoincrement=True),
        Column("userid", Integer, ForeignKey("users.userid", ondelete="CASCADE"), nullable=False),
        Column("type", Integer, nullable=False, default=1, server_default="1"),
        Column("headline", String(255), nullable=False),
        Column("content", Text, nullable=False),
        Column("thumbnail", String(255)),
        Column("credit", Integer, nullable=False, default=0, server_default="0"),
        Column("readcount", Integer, nullable=False, default=0, server_default="0"),
        Column("replycount", Integer, nullable=False, default=0, server_default="0"),
        Column("recommended", Integer, nullable=False, default=0, server_default="0"),
        Column("hide", Integer, nullable=False, default=0, server_default="0"),
        Column("drafted", Integer, nullable=False, default=0, server_default="0"),
        Column("checked", Integer, nullable=False, default=1, server_default="1"),
        Column("createtime", DateTime),
        Column("updatetime", DateTime),
        Column("delete", Integer, nullable=False, default=0, server_default="0"),
        Column("reject", Integer, nullable=False, default=0, server_default="0"),
        Index("ix_article_visible", "hide", "drafted", "checked", "articleid"),
        Index("ix_article_user", "userid", "delete"),
    )

    comment = Table(
        "comment",
        metadata,
        Column("commentid", Integer, primary_key=True, autoincrement=True),
        Column("userid", Integer, ForeignKey("users.userid", ondelete="CASCADE"), nullable=False),
        Column("articleid", Integer, ForeignKey("article.articleid", ondelete="CASCADE"), nullable=False),
        Column("content", Text),
        Column("ipaddr", String(64)),
        Column("replyid", Integer, default=0, server_default="0"),
        Column("agreecount", Integer, default=0, server_default="0"),
        Column("opposecount", Integer, default=0, server_default="0"),
        Column("hide", Integer, default=0, server_default="0"),
        Column("createtime", DateTime),
        Column("info", String(500)),
        Index("ix_comment_article", "articleid", "hide", "replyid"),
    )

    Table(
        "favorite",
        metadata,
        Column("favoriteid", Integer, primary_key=True, autoincrement=True),
        Column("articleid", Integer, ForeignKey("article.articleid", ondelete="CASCADE"), nullable=False),
        Column("userid", Integer, ForeignKey("users.userid", ondelete="CASCADE"), nullable=False),
        Column("canceled", Integer, default=0, server_default="0"),
        Column("createtime", DateTime),
        Column("updatetime", DateTime),
        UniqueConstraint("articleid", "userid", name="uq_favorite_article_user"),
    )

    Table(
        "credit",
        metadata,
        Column("creditid", Integer, primary_key=True, autoincrement=True),
        Column("userid", Integer, ForeignKey("users.userid", ondelete="CASCADE"), nullable=False),
        Column("category", String(255)),
        Column("target", Integer),
        Column("createtime", DateTime),
        Column("ipaddr", String(64)),
        Column("info", String(500)),
        Column("credit", Integer),
        Index("ix_credit_user_created", "userid", "createtime"),
    )

    Table(
        "log",
        metadata,
        Column("logid", Integer, primary_key=True, autoincrement=True),
        Column("userid", Integer, nullable=False, default=0, server_default="0"),
        Column("category", String(200), default="", server_default=""),
        Column("target", Integer, default=0, server_default="0"),
        Column("credit", Integer),
        Column("createtime", DateTime),
        Column("ipaddr", String(64)),
        Column("info", String(500)),
        Index("ix_log_user_created", "userid", "createtime"),
    )

    Table(
        "upload",
        metadata,
        Column("uploadid", Integer, primary_key=True, autoincrement=True),
        Column("userid", Integer, ForeignKey("users.userid", ondelete="CASCADE"), nullable=False),
        Column("imgname", String(255)),
        Column("ipaddr", String(64)),
        Column("info", String(500)),
        Column("createtime", DateTime),
        Index("ix_upload_user_created", "userid", "createtime"),
    )

    Table(
        "articleLog",
        metadata,
        Column("articleLogId", Integer, primary_key=True, autoincrement=True),
        Column("userid", Integer, ForeignKey("users.userid", ondelete="CASCADE")),
        Column("articleid", Integer, ForeignKey("article.articleid", ondelete="CASCADE")),
        Column("type", String(255)),
        Column("ipaddr", String(64)),
        Column("info", String(500)),
        Column("createtime", DateTime),
        Index("ix_article_log_user_created", "userid", "createtime"),
    )

    # Keep references alive for SQLAlchemy's dependency sorter.
    _ = users, article, comment

