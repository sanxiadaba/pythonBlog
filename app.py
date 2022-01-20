"""
文件说明：

此文件为运行该项目的主程序，直接运行即可

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/14
@gituhb: sanxiadaba/pythonBlog
"""

import os
import traceback
from collections import defaultdict

import pymysql
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

from common.myLog import ininLogDir, logDanger, allLogger
from constant import config_mysql, replyAndAddCommentCredit, regGiveCredit, postArticleCredit
from constant import sessionExpirationTime, sessionRestart, classification, portNum, creditListForReleaseArticle, \
    shufflingFigurePicture, shufflingFigureLink, indexLogoPicture, indexLogoPictureSize, indexAboveStr, \
    whetherSaveShufflingFigure, databaseName, emailAccount, loginEvereDayCredit, whetherDebug

# 链接数据库的一些设置，防止报错
pymysql.install_as_MySQLdb()

# 初始化flask
app = Flask(__name__)

# 如果用到了github第三方登录功能，进行github第三方登录的初始化
# if whetherUseGithubLogin is True:
#     from flask_github import GitHub
#     githubApp = GitHub(app)

# 对flask连接的一些设置

# 连接数据库
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://" + config_mysql + f"/{databaseName}?charset=utf8"
# 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存，一般情况下是禁用的。
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#  设置自动回收时间（单位：秒）
app.config["SQLALCHEMY_POOL_RECYCLE"] = 10
# 	数据库连接池的大小
app.config["SQLALCHEMY_POOL_SIZE"] = 100
#  指定数据库连接池的超时时间
app.config["SQLALCHEMY_POOL_TIMEOUT"] = 20
#  控制在连接池达到最大值后可以创建的连接数。当这些额外的 连接回收到连接池后将会被断开和抛弃。
app.config["SQLALCHEMY_MAX_OVERFLOW"] = 100
# 是否在使用连接前先进行ping（详情参数见官网）
app.config["pool_pre_ping"] = True
# 防止报错设置
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/flask-session'  # session类型为filesystem
# 随机指定的SCRET_KEY   也可设置为os.urandom(24)  不过每次服务器重启原来session就失效了
app.config['SECRET_KEY'] = "123456" if sessionRestart is False else os.urandom(24)
#  sesssion过期的时间
app.config['PERMANENT_SESSION_LIFETIME'] = sessionExpirationTime

# 使用SQLAlchemy
db = SQLAlchemy(app)


# 404处理
@app.errorhandler(404)
@logDanger
def page_not_find(e):
    return render_template("erroe-404.html", myemail=emailAccount)


# 500处理
@app.errorhandler(500)
@logDanger
def page_not_find(e):
    return render_template("error-500.html", myemail=emailAccount)


# 把文章的类别”注册“到全局函数中
@app.context_processor
@logDanger
def gettype():
    type = {}
    for i, j in enumerate(classification):
        type[str(i + 1)] = j
    # 传到前面一个字典
    return dict(article_type=type)


# 把发布文章作者的可选积分注册到全局函数中
@app.context_processor
@logDanger
def listOfCredit():
    type = {}
    for i in creditListForReleaseArticle:
        type[i] = str(i) + "分"
    return dict(listOfCredit=type)


#  这里将logo、轮播图等传到前端
@app.context_processor
@logDanger
def manyParameter():
    type = defaultdict(list)
    for i in range(len(shufflingFigurePicture)):
        type["shufflingFigure"].append([shufflingFigurePicture[i], shufflingFigureLink[i]])

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


# 自定义一个将数字加一的函数，防止html里闪烁错误（虽说不影响运行，但是强迫症看着难受）
def numAddNum(n, a):
    return n + a


# 将函数注册进去
app.jinja_env.filters.update(my_truncate=my_truncate, numAddNum=numAddNum)


# 定义全局拦截器,实现自动登录
@app.before_request
@logDanger
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
                islogin = session.get("islogin")
                userid = session.get("userid")
                nickname = instanceUser.searchNicknameByUserid(userid)[0]
                session["nickname"] = nickname
                session["role"] = result[0].role
                if islogin == "true":
                    if instanceCredit.check_limit_login_per_day(userid) is True:
                        info = f"userid为{userid} 昵称为{nickname}的用户每天登录成功,并且领取{loginEvereDayCredit}积分，这是自动登录"
                        instanceCredit.insert_detail(type="每日登录", target=0, credit=loginEvereDayCredit, info=info)
                        listLogger(userid, info, [0])
                        # 用来判定是否每天自动登录，然后自己领积分
                        session["judgeLin"] = "1"
                    else:
                        pass


# 判断每天自动登录的接口，前端继承baseArticle模板的文件在加载页面的时候会访问该接口
#  判断是否自动登录领取积分
@app.route("/judgeAutoLogin", methods=["POST"])
@logDanger
def judgeAutoLogin():
    try:
        if session.get("judgeLin") == "1":
            return "1"
        else:
            return "0"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
    finally:
        session["judgeLin"] = "0"


# 一个传递参数的接口
@app.route("/toTransmitParam", methods=["GET"])
@logDanger
def toTransmitParam():
    param = {}
    param["loginEvereDayCredit"] = loginEvereDayCredit
    param["replyAndAddCommentCredit"] = replyAndAddCommentCredit
    param["regGiveCredit"] = regGiveCredit
    param["postArticleCredit"] = postArticleCredit
    return param


#  用来释放没连接的dbsession 防止出现阻塞
@app.teardown_appcontext
def shutdown_session(exception=None):
    if exception is None:
        db.session.remove()


# 改变网站的一些参数设置，比如，没人每天可评论几次
# 登录、注册送多少积分等
@app.route("/changeBlogParams", methods=["POST"])
def changeBlogParams():
    pass
    return "1"


#  主运行程序
if __name__ == '__main__':
    # 导入实例化的数据库操作类
    from database.instanceDatabase import instanceUser, instanceCredit
    from common.myLog import listLogger
    # 注册flask蓝图
    from controler.index import index
    from controler.user import user
    from controler.article import article
    from controler.favorite import favorite
    from controler.comment import comment
    from controler.ueditor import ueditor
    from controler.userManage import userManage
    from controler.adminManage import adminManage
    # 导入测试用的蓝图（仅供测试时使用）
    from controler.test import test

    app.register_blueprint(index)
    app.register_blueprint(user)
    app.register_blueprint(article)
    app.register_blueprint(favorite)
    app.register_blueprint(comment)
    app.register_blueprint(ueditor)
    app.register_blueprint(userManage)
    app.register_blueprint(adminManage)
    # 注册测试用的蓝图（仅供测试时使用）
    app.register_blueprint(test)

    # 初始化logs（检查log能工作的一些必要目录）
    ininLogDir()

    #  以debug模式在指定端口启动
    app.run(debug=whetherDebug, port=portNum)
