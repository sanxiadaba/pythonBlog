import os
from collections import defaultdict
from pathlib import Path

import click
from flask import Flask, abort, jsonify, render_template, request, session
from flask_wtf.csrf import CSRFError
from markupsafe import Markup
from sqlalchemy import event

from common.initDatabase import create_user, initialize_database
from common.myLog import ininLogDir
from common.schema import define_schema
from common.utility import sanitize_article_html
from constant import (
    classification,
    creditListForReleaseArticle,
    emailAccount,
    indexAboveStr,
    indexLogoPicture,
    indexLogoPictureSize,
    loginEvereDayCredit,
    portNum,
    postArticleCredit,
    regGiveCredit,
    replyAndAddCommentCredit,
    sessionExpirationTime,
    shufflingFigureLink,
    shufflingFigurePicture,
    whetherDebug,
    whetherSaveShufflingFigure,
)
from extensions import csrf, db, limiter, migrate


def _database_uri(app):
    configured = os.getenv("DATABASE_URL", "").strip()
    if configured:
        return configured
    database_file = Path(app.instance_path) / "pythonblog.db"
    return f"sqlite:///{database_file.as_posix()}"


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    database_uri = _database_uri(app)
    is_sqlite = database_uri.startswith("sqlite:")
    secret_key = os.getenv("SECRET_KEY", "dev-only-change-me")

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        DEBUG=whetherDebug,
        SQLALCHEMY_DATABASE_URI=database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS=(
            {"connect_args": {"check_same_thread": False}}
            if is_sqlite
            else {"pool_pre_ping": True, "pool_recycle": 1800, "pool_size": 10, "max_overflow": 20}
        ),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true",
        PERMANENT_SESSION_LIFETIME=sessionExpirationTime,
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH_MB", "8")) * 1024 * 1024,
        WTF_CSRF_TIME_LIMIT=3600,
        RATELIMIT_STORAGE_URI=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
        ALLOW_REMOTE_IMAGES=os.getenv("ALLOW_REMOTE_IMAGES", "False").lower() == "true",
        AUTO_INIT_DB=os.getenv("AUTO_INIT_DB", "True").lower() == "true",
    )
    if test_config:
        app.config.update(test_config)
    if not app.config.get("TESTING") and not app.config["DEBUG"] and secret_key == "dev-only-change-me":
        raise RuntimeError("SECRET_KEY must be configured outside development")

    db.init_app(app)
    define_schema(db.metadata)
    csrf.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    with app.app_context():
        if is_sqlite:
            def enable_sqlite_foreign_keys(connection, _record):
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            event.listen(db.engine, "connect", enable_sqlite_foreign_keys)
        if app.config["AUTO_INIT_DB"]:
            initialize_database()
        _register_blueprints(app)

    _register_handlers(app)
    _register_template_helpers(app)
    _register_cli(app)
    ininLogDir()
    return app


def _register_blueprints(app):
    from controler.adminManage import adminManage
    from controler.article import article
    from controler.comment import comment
    from controler.favorite import favorite
    from controler.index import index
    from controler.ueditor import ueditor
    from controler.user import user
    from controler.userManage import userManage

    for blueprint in (index, user, article, favorite, comment, ueditor, userManage, adminManage):
        app.register_blueprint(blueprint)


def _register_handlers(app):
    @app.errorhandler(404)
    def page_not_found(_error):
        return render_template("erroe-404.html", myemail=emailAccount), 404

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return render_template("error-500.html", myemail=emailAccount), 500

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return jsonify(error="csrf_failed", reason=error.description), 400

    @app.teardown_appcontext
    def shutdown_session(_exception=None):
        db.session.remove()

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; font-src 'self' data:; connect-src 'self'",
        )
        return response

    @app.before_request
    def reject_blocked_sessions():
        userid = session.get("userid")
        if not userid:
            return None
        from database.users import Users

        user = Users().searchUserByUserid(userid)
        if user is None or user.forbidLogin == 1:
            session.clear()
            if request.endpoint not in {"user.login", "index.home"}:
                abort(403)
        return None

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.get("/toTransmitParam")
    def transmit_parameters():
        return {
            "loginEvereDayCredit": loginEvereDayCredit,
            "replyAndAddCommentCredit": replyAndAddCommentCredit,
            "regGiveCredit": regGiveCredit,
            "postArticleCredit": postArticleCredit,
        }

    @app.get("/replyAndAddCommentCredit")
    def reply_credit():
        return str(replyAndAddCommentCredit)

    @app.get("/loginEvereDayCredit")
    def login_credit():
        return str(loginEvereDayCredit)

    @app.post("/judgeAutoLogin")
    def judge_auto_login():
        earned = session.pop("judgeLin", "0")
        return "1" if earned == "1" else "0"


def _register_template_helpers(app):
    @app.context_processor
    def article_types():
        return {"article_type": {str(index + 1): name for index, name in enumerate(classification)}}

    @app.context_processor
    def credits():
        return {"listOfCredit": {value: f"{value} points" for value in creditListForReleaseArticle}}

    @app.context_processor
    def page_parameters():
        values = defaultdict(list)
        values["shufflingFigure"] = list(zip(shufflingFigurePicture, shufflingFigureLink, strict=False))
        values["indexLogoPicture"].append(indexLogoPicture)
        values["indexLogoPictureSize"].extend(indexLogoPictureSize)
        values["indexAboveStr"].extend(indexAboveStr)
        values["display"].append("block" if whetherSaveShufflingFigure else "none")
        return {"manyParameter": values}

    def truncate_text(value, length, end="..."):
        value = value or ""
        return value if len(value) <= length else value[:length] + end

    app.jinja_env.filters["my_truncate"] = truncate_text
    app.jinja_env.filters["numAddNum"] = lambda number, amount: number + amount
    app.jinja_env.filters["safe_html"] = lambda value: Markup(sanitize_article_html(value or ""))


def _register_cli(app):
    @app.cli.command("init-db")
    def init_db_command():
        initialize_database()
        click.echo("Database initialized.")

    @app.cli.command("create-user")
    @click.option("--username", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option("--role", type=click.Choice(["user", "editor", "admin"]), default="user")
    @click.option("--nickname", default=None)
    def create_user_command(username, password, role, nickname):
        user_id = create_user(username, password, role=role, nickname=nickname)
        click.echo(f"Created {role} user {username} with id {user_id}.")


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=portNum, debug=whetherDebug)
