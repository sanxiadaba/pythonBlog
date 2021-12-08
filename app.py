import os
from datetime import timedelta
from config import config_mysql
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, abort
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
# 设置

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://"+config_mysql+"/myBlog?charset=utf8"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 防止报错设置
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/flask-session'  # session类型为filesystem
app.config['SECRET_KEY'] = "123456"  # 随机指定的SCRET_KEY   也可设置为os.urandom(24)  不过每次服务器重启原来session就失效了
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# 使用SQLAlchemy
db = SQLAlchemy(app)


# 抛出500
# @app.route("/error-500")
# def error_500():    # 这里不要传参
#     return abort(500)

# 404处理
@app.errorhandler(404)
def page_not_find(e):
    return render_template("erroe-404.html")


# 500处理
@app.errorhandler(500)
def page_not_find(e):
    return render_template("error-500.html")


@app.route("/artical")
def sqd():
    return render_template("artical.html")


@app.context_processor
def gettype():
    type = {
        "1": "Python技巧",
        "2": "LeetCode刷题",
        "3": "项目开发",
        "4": "综合学习",
        "5": "技巧"
    }
    return dict(article_type=type)


# 自定义过滤器函数
def my_truncate(s, length, end="..."):
    count = 0
    new = ""
    for c in s:
        new += c
        if ord(c) <= 128:
            count += 0.5
        else:
            count += 1
        if count > length:
            break
    return new + end


# 注册自定义函数
app.jinja_env.filters.update(my_truncate=my_truncate)


# 定义全局拦截器,实现自动登录
@app.before_request
def before():
    url = request.path
    pass_list = ["/user", "/login", "logout"]
    if url in pass_list or url.endswith(".js") or url.endswith(".png") or url.endswith(".jpg"):
        pass
    elif session.get("islogin") is None:
        username = request.cookies.get("username")
        password = request.cookies.get("password")
        if username != None and password != None:
            user = Users()
            result = user.find_by_username(username)
            if len(result) == 1 and result[0].password == password:
                session["islogin"] = "true"
                session["username"] = username
                session["userid"] = result[0].userid
                nickname = username.split("@")[0]
                session["nickname"] = nickname
                session["role"] = result[0].role


if __name__ == '__main__':
    from controler.index import *

    app.register_blueprint(index)

    from controler.user import *

    app.register_blueprint(user)

    from controler.article import *

    app.register_blueprint(article)

    from controler.favorite import *

    app.register_blueprint(favorite)

    from controler.comment import *

    app.register_blueprint(comment)

    from controler.ueditor import *

    app.register_blueprint(ueditor)

    app.run(debug=True, port=1234)
