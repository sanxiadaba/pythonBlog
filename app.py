"""
File description.

This file is the main program to run the project, just run it directly

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/14
@gituhb: sanxiadaba/pythonBlog
"""

import os
import time
import traceback
from collections import defaultdict

import pymysql
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

from common.initDatabase import ininDatabase
from common.myLog import ininLogDir, logDanger, allLogger
from constant import config_mysql, replyAndAddCommentCredit, regGiveCredit, postArticleCredit
from constant import sessionExpirationTime, sessionRestart, classification, portNum, creditListForReleaseArticle, \
    shufflingFigurePicture, shufflingFigureLink, indexLogoPicture, indexLogoPictureSize, indexAboveStr, \
    whetherSaveShufflingFigure, databaseName, emailAccount, loginEvereDayCredit, whetherDebug

# Some settings of the linked database to prevent error reporting
pymysql.install_as_MySQLdb()

# Initialize flask
app = Flask(__name__, template_folder='templates')

# Some settings for flask connections

# Connecting to the database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://" + config_mysql + f"/{databaseName}?charset=utf8"
# If set to True (the default), Flask-SQLAlchemy will track object modifications and send signals. This requires extra memory and is normally disabled.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Set auto-recycle time (in seconds)
app.config["SQLALCHEMY_POOL_RECYCLE"] = 10
# 	Size of the database connection pool
app.config["SQLALCHEMY_POOL_SIZE"] = 200
#  Specify the timeout for the database connection pool
app.config["SQLALCHEMY_POOL_TIMEOUT"] = 20
# controls the number of connections that can be created after the connection pool reaches its maximum. These additional connections will be disconnected and discarded when they are recycled to the connection pool.
app.config["SQLALCHEMY_MAX_OVERFLOW"] = 100
# Whether to ping before using the connection (see official website for detailed parameters)
app.config["pool_pre_ping"] = True
# Error prevention settings
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/flask-session'  # session type is filesystem
app.config['SECRET_KEY'] = "123456" if sessionRestart is False else os.urandom(24)
# sesssion expiration time
app.config['PERMANENT_SESSION_LIFETIME'] = sessionExpirationTime

# Using SQLAlchemy
db = SQLAlchemy(app)


# 404 processing
@app.errorhandler(404)
@logDanger
def page_not_find(e):
    return render_template("erroe-404.html", myemail=emailAccount)


# 500 processing
@app.errorhandler(500)
@logDanger
def page_not_find(e):
    return render_template("error-500.html", myemail=emailAccount)


# "Register" the category of the article into the global function
@app.context_processor
@logDanger
def gettype():
    type = {}
    for i, j in enumerate(classification):
        type[str(i + 1)] = j
    # Transfer to a previous dictionary
    return dict(article_type=type)


# Register the optional points of the author of the published article to the global function
@app.context_processor
@logDanger
def listOfCredit():
    type = {}
    for i in creditListForReleaseArticle:
        type[i] = str(i) + "points"
    return dict(listOfCredit=type)


# Here the logo, rotating images, etc. are passed to the front end
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


# Custom filter function to set the length of the fetched word
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


# Customize a function that adds one to the number to prevent flashing errors in the html (although it does not affect the operation, but OCD look uncomfortable)
def numAddNum(n, a):
    return n + a


# Register the function in
app.jinja_env.filters.update(my_truncate=my_truncate, numAddNum=numAddNum)


# Define global interceptor to achieve automatic login
@app.before_request
@logDanger
def before():
    url = request.path
    passList = ["/user", "/login", "logout"]
    if url in passList or url.endswith(".js") or url.endswith(".png") or url.endswith(".jpg") or url.endswith(".css"):
        pass
    elif session.get("islogin") is None:
        username = request.cookies.get("username")
        password = request.cookies.get("password")
        if username != None and password != None:
            result = instanceUser.searchUserByUsername(username)
            if len(result) == 1 and result[0].password == password:
                session["islogin"] = "true"
                session["username"] = username
                session["userid"] = result[0].userid
                islogin = session.get("islogin")
                userid = session.get("userid")
                nickname = instanceUser.searchNicknameByUserid(userid)
                session["nickname"] = nickname
                session["role"] = result[0].role
                if islogin == "true":
                    if instanceCredit.whetherFirstLoginThisDay(userid) is True:
                        info = f"Users with userid {userid} and nickname {nickname} log in successfully every day and receive {loginEvereDayCredit} points, which is an automatic login."
                        instanceCredit.insertDetail(type="Daily Login", target=0, credit=loginEvereDayCredit, info=info)
                        listLogger(userid, info, [0])
                        # Used to determine whether to automatically log in every day, and then collect the points themselves
                        session["judgeLin"] = "1"
                    else:
                        pass



# The interface to determine automatic daily login, which is accessed by the front-end inherited baseArticle template file when the page is loaded
# Determine whether to automatically log in to receive points
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


# An interface for passing parameters
@app.route("/toTransmitParam", methods=["GET"])
@logDanger
def toTransmitParam():
    param = {"loginEvereDayCredit": loginEvereDayCredit, "replyAndAddCommentCredit": replyAndAddCommentCredit,
             "regGiveCredit": regGiveCredit, "postArticleCredit": postArticleCredit}
    return param


# Used to release unconnected dbsessions to prevent blocking
@app.teardown_appcontext
def shutdown_session(exception=None):
    if exception is None:
        db.session.remove()


# Change some parameters of the site, for example, how many times a day no one can comment
# How many points are given for login, registration, etc.
@app.route("/changeBlogParams", methods=["POST"])
def changeBlogParams():
    pass
    return "1"


# Main runner
if __name__ == '__main__':
    # Initialize logs (check some necessary directories for logs to work)
    ininLogDir()
    # Initializing the database
    ininDatabase()
    # Importing instantiated database operation classes
    from database.credit import Credit
    from database.users import Users
    from database.logs import Log

    instanceCredit = Credit()
    instanceUser = Users()
    instanceLog = Log()
    from common.myLog import listLogger
    # Register flask blueprint
    from controler.index import index
    from controler.user import user
    from controler.article import article
    from controler.favorite import favorite
    from controler.comment import comment
    from controler.ueditor import ueditor
    from controler.userManage import userManage
    from controler.adminManage import adminManage

    app.register_blueprint(index)
    app.register_blueprint(user)
    app.register_blueprint(article)
    app.register_blueprint(favorite)
    app.register_blueprint(comment)
    app.register_blueprint(ueditor)
    app.register_blueprint(userManage)
    app.register_blueprint(adminManage)

    # Add logs for each server startup

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    if instanceLog.judgeStartServe() is False:
        instanceLog.insertDetail(type="Start the server", target=0, credit=0, userid=0,
                                 info=f"The server was started in {now}")
        allLogger(1, f"The server was started in {now}")
    else:
        pass
    #  Start in debug mode on the specified port
    app.run(debug=whetherDebug, port=portNum)
