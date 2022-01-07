import os
from constant import config_mysql
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, abort, request, session
import pymysql
from collections import defaultdict
from constant import sessionExpirationTime,sessionRestart,classification,portNum,creditListForReleaseArticle,shufflingFigurePicture,shufflingFigureLink,indexLogoPicture,indexLogoPictureSize,indexAboveStr,whetherSaveShufflingFigure
# 链接数据库的一些设置，防止报错
pymysql.install_as_MySQLdb()

app = Flask(__name__)
# 设置
# 连接数据库
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://"+config_mysql+"/myBlog?charset=utf8"
# 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它。
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#  设置自动回收时间
app.config["SQLALCHEMY_POOL_RECYCLE"]=15
# 	数据库连接池的大小
app.config["SQLALCHEMY_POOL_SIZE"]=10
#  指定数据库连接池的超时时间
app.config["SQLALCHEMY_POOL_TIMEOUT"]=100
#  控制在连接池达到最大值后可以创建的连接数。当这些额外的 连接回收到连接池后将会被断开和抛弃。
app.config["SQLALCHEMY_MAX_OVERFLOW"]=100
# 是否在使用连接前先进行ping
app.config["pool_pre_ping"]=True
# 防止报错设置
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/flask-session'  # session类型为filesystem
# 随机指定的SCRET_KEY   也可设置为os.urandom(24)  不过每次服务器重启原来session就失效了
app.config['SECRET_KEY'] = "123456"  if sessionRestart is False else os.urandom(24)
#  sesssion过期的时间
app.config['PERMANENT_SESSION_LIFETIME'] = sessionExpirationTime

# 使用SQLAlchemy
db = SQLAlchemy(app)


# 主动抛出500异常
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

# 把文章的类别”注册“到全局函数中
@app.context_processor
def gettype():
    type={}
    for i,j in enumerate(classification):
        type[str(i+1)]=j
    # 传到前面一个字典
    return dict(article_type=type)

# 把发布文章作者的可选积分注册到全局函数中
@app.context_processor
def listOfCredit():
    type={}
    for i in creditListForReleaseArticle:
        type[i]=str(i)+"分"
    return dict(listOfCredit=type)

#  这里将logo、轮播图等传到前端
@app.context_processor
def manyParameter():
    type=defaultdict(list)
    for i in range(len(shufflingFigurePicture)):
        type["shufflingFigure"].append([shufflingFigurePicture[i],shufflingFigureLink[i]])

    type["indexLogoPicture"].append(indexLogoPicture)

    for i in indexLogoPictureSize:
        type["indexLogoPictureSize"].append(i)

    for i in indexAboveStr:
        type["indexAboveStr"].append(i)

    if whetherSaveShufflingFigure is True:
        type["display"].append("block")
    else:
        type["display"].append("none")
    return dict(manyParameter=type)

# 自定义过滤器函数，设置取的字的长度
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

# 将函数注册进去
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
            result = instanceUser.find_by_username(username)
            if len(result) == 1 and result[0].password == password:
                session["islogin"] = "true"
                session["username"] = username
                session["userid"] = result[0].userid
                nickname = username.split("@")[0]
                session["nickname"] = nickname
                session["role"] = result[0].role


#  用来释放没连接的dbsession 防止出现阻塞
@app.teardown_appcontext
def shutdown_session(exception=None):
    if exception is None:
        db.session.remove()



#  主运行程序
if __name__ == '__main__':
    # 导入实例化的数据库操作类
    from database.instanceDatabase import instanceUser

    # 注册flask蓝图
    from controler.index import index
    app.register_blueprint(index)

    from controler.user import user
    app.register_blueprint(user)

    from controler.article import article
    app.register_blueprint(article)

    from controler.favorite import favorite
    app.register_blueprint(favorite)

    from controler.comment import comment
    app.register_blueprint(comment)

    from controler.ueditor import ueditor
    app.register_blueprint(ueditor)

    from controler.userManage import userManage
    app.register_blueprint(userManage)

    #  以debug模式在指定端口启动
    app.run(debug=True, port=portNum)
