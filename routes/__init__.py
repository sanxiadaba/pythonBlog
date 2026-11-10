"""路由注册。"""

from flask import Flask


def register_routes(app: Flask) -> None:
    from routes.admin import admin
    from routes.blog import blog

    app.register_blueprint(blog)
    app.register_blueprint(admin)
