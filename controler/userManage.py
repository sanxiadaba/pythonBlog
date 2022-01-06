from flask import Blueprint, request, session, jsonify
from database.instanceDatabase import instanceArticle,instanceCredit,instanceUser,instanceComment

userManage = Blueprint("userManage", __name__)


# 可以用拦截器
# 未登录的不能通过直接访问端口发送评论
@userManage.before_request
def beforeUserManage():
    if session.get("islogin") is None or session.get("islogin") != "true":
        return "not-login"
    else:
        pass

#  返回我的资料
@userManage.route("/userInfo")
def userInfo():
    last, most, recommended = instanceArticle.find_last_most_recommended()
    return jsonify(last, most, recommended)

