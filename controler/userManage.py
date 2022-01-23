"""
File description.

Background management page for regular users and editors to view their articles, comments, favorites and other functions

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""
import base64
import os
import time
import traceback
from math import ceil

from flask import Blueprint, session, jsonify, render_template, request

from common.myLog import logDanger, dirInDir, avatarPath, listLogger, allLogger
from common.utility import compress_image
from constant import everyPageInHou, emailAccount
from database.article import Article
from database.comment import Comment
from database.credit import Credit
from database.favorite import Favorite
from database.logs import Log
from database.users import Users

instanceArticle = Article()
instanceComment = Comment()
instanceCredit = Credit()
instanceFavorite = Favorite()
instanceLog = Log()
instanceUser = Users()

userManage = Blueprint("userManage", __name__)


@userManage.route("/userManage", methods=["GET"])
@logDanger
def baseUserManage():
    userid = session.get("userid")

    #  My Collection
    myFavo, lenMyFavo = instanceFavorite.myFavoriteArticle(userid)
    # Number of my published articles
    numOfAllMyArticle = len(instanceArticle.searchAllMyArticle())
    # Number of visits to published articles
    allNumOfAllArticleRead = instanceArticle.allNumOfAllArticleRead()
    # Number of my favorite articles
    numOfMyFavoriteArticle = lenMyFavo
    # Number of my comments
    numOfALLMyComment = instanceComment.numOfALLMyComment()
    # My nickname
    myNickname = instanceUser.searchNicknameByUserid(userid)[0]
    # My registered email
    myEmail = instanceUser.searchMyEmail(userid)
    # User Roles
    myRole = session.get("role")
    # My qq
    myQQ = instanceUser.searchMyQQ(userid)
    # Total remaining points
    restOfMyCredit = instanceUser.findRestCredit()
    # My avatar
    myAvatar = instanceUser.searchMyAvatar(userid)
    # Whether to apply to become an editor
    whetherApplyForEditor = instanceUser.whetherApplyForEditor(userid)

    # Information for managing articles in the user background
    articleInfo = instanceArticle.articleInfo(userid)

    #  Check the number of all my posts (except deleted)
    myArticleNum = instanceArticle.exceptDeleteNum()

    #  The article page of the administration page is divided into several pages
    howManyPage = ceil(myArticleNum / everyPageInHou)
    howManyPage_1 = howManyPage
    howManyPage = list(range(2, howManyPage + 1))

    # Determine which page to jump to
    controlBiaoNum = session.get("controlBiaoNum")
    controlBiaoNum = 0 if controlBiaoNum is None else int(controlBiaoNum)

    MyInfo = {}
    MyInfo["numOfAllMyArticle"] = numOfAllMyArticle
    MyInfo["allNumOfAllArticleRead"] = allNumOfAllArticleRead
    MyInfo["numOfMyFavoriteArticle"] = numOfMyFavoriteArticle
    MyInfo["numOfALLMyComment"] = numOfALLMyComment
    MyInfo["myNickname"] = myNickname
    MyInfo["myEmail"] = myEmail
    MyInfo["myRole"] = myRole
    MyInfo["myQQ"] = myQQ
    MyInfo["restOfMyCredit"] = restOfMyCredit
    MyInfo["myAvatar"] = myAvatar
    MyInfo["whetherApplyForEditor"] = whetherApplyForEditor

    # My comments, number of comment likes, number of comment approvals, target posts, hidden comments
    myComment, allMyCommentNum = instanceComment.searchMyComment(userid)
    # with snoop:
    guo = []
    for i in myComment:
        lin = []
        for j in i:
            lin.append(j)
        lin.append(instanceArticle.searchHeadlineByArticleid(i[3]))
        guo.append(lin)
    myComment = guo
    myLoginLog = instanceLog.searchLoginLog(userid)
    #  Data of point changes
    allCreditChangeLog = instanceCredit.creditChangeLog(userid)
    return render_template("userManage.html", myInfo=MyInfo, articleInfo=articleInfo, everyPageInHou=everyPageInHou,
                           myArticleNum=myArticleNum, howManyPage=howManyPage, howManyPage_1=howManyPage_1,
                           controlBiaoNum=controlBiaoNum, myComment=myComment, allMyCommentNum=allMyCommentNum,
                           myFavo=myFavo, lenMyFavo=lenMyFavo, myLoginLog=myLoginLog,
                           allCreditChangeLog=allCreditChangeLog, emailAccount=emailAccount)


#  Back to my profile
# Number of articles, number of comments, total number of views, total points, my nickname, my avatar, my qq number, my role
@userManage.route("/userInfo", methods=["GET"])
@logDanger
def userInfo():
    last, most, recommended = instanceArticle.searchLastMostRecommended()
    return jsonify(last, most, recommended)


# 修改昵称
@userManage.route("/modifyNickname", methods=["POST"])
@logDanger
def modifyNickname():
    userid = session.get('userid')
    newNickname = request.form.get("newNickname")
    try:
        instanceUser.modifyUserNickname(newNickname)
        info = f"The user with userid {userid} modifies the nickname to {newNickname}"
        listLogger(userid, info, [0])
        instanceLog.insertDetail(type="Change nickname", target=userid, credit=0, info=info)
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# Modify qq number
@userManage.route("/modifyQQ", methods=["POST"])
@logDanger
def modifyQQ():
    newQQ = request.form.get("newQQ")
    userid = session.get("userid")
    try:
        instanceUser.modifyUserQQnum(newQQ)
        info = f"The userid of {userid} modifies the qq number to {newQQ}"
        listLogger(userid, info, [0])
        instanceLog.insertDetail(type="Modify QQ", target=userid, credit=0, info=info)
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# Apply for a role
@userManage.route("/applyEditor", methods=["POST"])
@logDanger
def applyEditor():
    userid = session.get('userid')
    try:
        instanceUser.applyForBecomeEditor()
        info = f"Users with userid {userid} apply to become editors"
        listLogger(userid, info, [0])
        instanceLog.insertDetail(type="Apply to become an editor", target=userid, credit=0, info=info)
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# Delete comments (note that the number of comments on the article will be set to subtract 1 when the time comes)
# Note that all comments under the article will also be set to hidden
@userManage.route("/hideArticle", methods=["POST"])
@logDanger
def hideArticle():
    userid = session.get("userid")
    articleid = request.form.get('articleid')
    try:
        instanceArticle.deleteArticle(articleid)
        info = f"The user with userid {userid} has deleted the article with articleid {articleid}"
        listLogger(userid, info, [0])
        instanceLog.insertDetail(type="Delete article", target=userid, credit=0, info=info)
        #  Set the comments under the corresponding article to be hidden when deleting the article
        instanceComment.hideCommnetWhenHideArticle(articleid)
        # Set the favorite articles to un-favorite as well
        instanceFavorite.hideFavoByArticleid(articleid)
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# Modify avatar
@userManage.route("/uploadUserAvatar", methods=["POST", "GET"])
@logDanger
def uploadUserAvatar():
    if request.method == "GET":
        return render_template("uploadUserAvatar.html")


# 对头像图片上传进行响应
@userManage.route('/uploadImg', methods=['POST', 'OPTIONS'])
@logDanger
def upload():
    userid = session.get("userid")
    myAvatarPath = avatarPath + "\\" + f"myPic_{userid}"
    dirInDir(f"myPic_{userid}", avatarPath)
    if request.form.get("action") == "add":
        data = request.form.get("picStr")
        imgdata = base64.b64decode(data)
        thumbname = time.strftime("%Y%m%d_%H%M%S." + "jpg")
        now = thumbname.split(".")
        imgfile = os.path.join(myAvatarPath, "test.jpg")
        file = open(imgfile, 'wb')
        file.write(imgdata)
        file.close()
        oldpicPath = myAvatarPath + "\\" + "test.jpg"
        newPicPath = myAvatarPath + "\\" + thumbname
        compress_image(oldpicPath, newPicPath, 400)
        newPicPath = f"myPic_{userid}" + "/" + thumbname
        instanceUser.modifyUserThumbnail(newPicPath)
        os.remove(oldpicPath)
        allPathPic = [lists for lists in os.listdir(myAvatarPath) if os.path.isfile(os.path.join(myAvatarPath, lists))]
        for i in allPathPic:
            biJiao = i.split(".")
            if biJiao < now:
                os.remove(myAvatarPath + "\\" + i)
        info = f"Users whose userid is {userid} change their avatar to {newPicPath}"
        listLogger(userid, info, [0])
        instanceLog.insertDetail(type="Change avatar", target=userid, credit=0, info=info)
        return "1"


# Control which tab appears when the page is refreshed again
@userManage.route("/controlBiaoNum", methods=["POST", "GET"])
@logDanger
def controlBiaoNum():
    if request.method == 'GET':
        controlBiaoNum = session.get("controlBiaoNum")
        session["controlBiaoNum"] = 0
        if controlBiaoNum is not None or controlBiaoNum != "0":
            return str(controlBiaoNum)
        else:
            return "0"
    elif request.method == 'POST':
        session["controlBiaoNum"] = str(request.form.get("controlBiaoNum"))
        return "1"
