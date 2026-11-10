"""应用入口：create_app() 组装配置、扩展、路由和 CLI。"""

import os
import secrets
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_wtf.csrf import CSRFError
from sqlalchemy import event

from config import (
    AUTHOR,
    CATEGORIES,
    EMAIL,
    MAX_UPLOAD_BYTES,
    SITE_DESCRIPTION,
    SITE_NAME,
    UPLOAD_DIR,
)
from extensions import csrf, limiter
from models import Admin, db
from utils import hash_password, setup_logging

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def _secret_key(instance_path: Path) -> str:
    """优先用环境变量；本机自用没配时，生成一次存盘，重启后登录态不会丢。"""
    key = os.getenv("SECRET_KEY", "").strip()
    if key:
        return key
    key_file = instance_path / "secret_key"
    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()
    key = secrets.token_urlsafe(48)
    key_file.write_text(key, encoding="utf-8")
    return key


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    instance = Path(app.instance_path)
    instance.mkdir(parents=True, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=_secret_key(instance),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{(instance / 'blog.db').as_posix()}",
        SQLALCHEMY_ENGINE_OPTIONS={"connect_args": {"check_same_thread": False, "timeout": 30}},
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=12 * 1024 * 1024,
        UPLOAD_DIR=UPLOAD_DIR,
        MAX_UPLOAD_BYTES=MAX_UPLOAD_BYTES,
        RATELIMIT_STORAGE_URI="memory://",
        DEBUG=os.getenv("DEBUG_MODE", "True").lower() == "true",
        SITE_NAME=SITE_NAME,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    with app.app_context():
        event.listen(db.engine, "connect", _configure_sqlite)
        db.create_all()

    from routes import register_routes

    register_routes(app)
    _register_handlers(app)
    _register_cli(app)

    @app.context_processor
    def inject_site():
        return {
            "site": {
                "name": SITE_NAME,
                "description": SITE_DESCRIPTION,
                "author": AUTHOR,
                "email": EMAIL,
            },
            "categories": CATEGORIES,
        }

    setup_logging(BASE_DIR / "logs")
    return app


def _configure_sqlite(connection, _record):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


def _register_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, message="页面不存在"), 404

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("error.html", code=403, message="没有权限"), 403

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("error.html", code=500, message="服务器出错了"), 500

    @app.errorhandler(413)
    def too_large(_error):
        if request.path.startswith("/admin/upload"):
            return jsonify(error="图片太大"), 413
        return render_template("error.html", code=413, message="提交的内容太大"), 413

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        if request.path.startswith("/admin/upload"):
            return jsonify(error="表单已过期，请刷新页面后重试"), 400
        return render_template("error.html", code=400, message="表单已过期，请刷新页面后重试"), 400

    @app.teardown_appcontext
    def remove_session(_exception=None):
        db.session.remove()

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'",
        )
        return response

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}


def _register_cli(app: Flask) -> None:
    @app.cli.command("create-admin")
    @click.option("--username", prompt=True, default="admin")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(username, password):
        """创建或重置管理员账号。"""
        if len(password) < 8:
            raise click.ClickException("密码至少 8 位")
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            admin.password_hash = hash_password(password)
            click.echo(f"已重置 {username} 的密码")
        else:
            db.session.add(Admin(username=username, password_hash=hash_password(password)))
            click.echo(f"已创建管理员 {username}")
        db.session.commit()


if __name__ == "__main__":
    create_app().run(
        host="127.0.0.1",
        port=int(os.getenv("PORT_NUM", "5000")),
        debug=os.getenv("DEBUG_MODE", "True").lower() == "true",
    )
