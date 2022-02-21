"""

File Description

This file is mainly about the administrator backend control page

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/14
@gituhb: sanxiadaba/pythonBlog
"""
import platform
import sys
import time

from flask import Blueprint, render_template, request, session

from common.initDatabase import watchVersionOfMysql
from common.myLog import logDanger, adminLog, listLogger
from constant import classification, commentNum, regGiveCredit, loginEvereDayCredit, postArticleCredit, \
    replyAndAddCommentCredit, rateCreditForArticle, creditListForReleaseArticle, howArticleInWeb, howCommentInArticle, \
    maxUserPostArticleNum, maxUserPostArticleNumOfEditor, maxModifyArticleNum, maxUploadPicNum, blogLanguage, \
    recommendedNumOfSide
from database.article import Article
from database.comment import Comment
from database.logs import Log
from database.users import Users

adminManage = Blueprint("adminManage", __name__)

instanceArticle = Article()
instanceUser = Users()
instanceLog = Log()
instanceComment = Comment()


@adminManage.route("/adminManage", methods=["GET"])
@logDanger
def baseAdminManage():
    start = time.time()
    webInfo = {}
    webInfo["allNumOfArticle"] = instanceArticle.searchAllArticleNum()
    webInfo["allArticleReply"], webInfo["allArticleRead"] = instanceArticle.searchALLNumberOfComment()
    webInfo["allUserNum"] = instanceUser.searchAllNumOfUser()
    webInfo["numOfAdmin"] = instanceUser.searchNumOfAdmin()
    webInfo["numOfEditor"] = instanceUser.searchNumOfEditor()
    webInfo["numOfUser"] = instanceUser.searchNumOfUser()
    webInfo["numOfUserAndEditor"] = int(webInfo["numOfUser"]) + int(webInfo["numOfEditor"])
    webInfo["pythonVersion"] = sys.version.split("(")[0]
    webInfo["platForm"] = platform.platform()
    webInfo["mysqlVersion"] = watchVersionOfMysql()
    webInfo["lastServeTime"] = instanceLog.searchTimeOfLastTimeServe().split("in")[-1].strip()

    # First convert the data type in the list to str otherwise, because join can only splice strings
    for i in range(len(creditListForReleaseArticle)):
        creditListForReleaseArticle[i] = str(creditListForReleaseArticle[i])
    for i in range(len(recommendedNumOfSide)):
        recommendedNumOfSide[i] = str(recommendedNumOfSide[i])
    webInfo["classification"] = " ".join(classification)
    webInfo["commentNum"] = commentNum
    webInfo["regGiveCredit"] = regGiveCredit
    webInfo["loginEvereDayCredit"] = loginEvereDayCredit
    webInfo["postArticleCredit"] = postArticleCredit
    webInfo["replyAndAddCommentCredit"] = replyAndAddCommentCredit
    webInfo["rateCreditForArticle"] = rateCreditForArticle
    webInfo["creditListForReleaseArticle"] = " ".join(creditListForReleaseArticle)
    webInfo["howArticleInWeb"] = howArticleInWeb
    webInfo["howCommentInArticle"] = howCommentInArticle
    webInfo["maxUserPostArticleNum"] = maxUserPostArticleNum
    webInfo["maxUserPostArticleNumOfEditor"] = maxUserPostArticleNumOfEditor
    webInfo["maxModifyArticleNum"] = maxModifyArticleNum
    webInfo["recommendedNumOfSide"] = " ".join(recommendedNumOfSide)
    webInfo["maxUploadPicNum"] = maxUploadPicNum
    webInfo["language"] = blogLanguage

    usersInfo = instanceUser.searchInfoOfUserAndEditor()
    commentInfo = instanceComment.searchCommentInfo()
    end = time.time()
    loadTime = end - start
    webInfo["loadTime"] = loadTime
    webNumOfDraft = instanceArticle.searchNumOfDraft()
    webDraft = instanceArticle.searchDraft()
    webArticles=instanceArticle.searchAllArtice()
    return render_template("adminManage.html", webInfo=webInfo, usersInfo=usersInfo, commentInfo=commentInfo,
                           webDraft=webDraft, webNumOfDraft=webNumOfDraft,allArticles=webArticles)


# Jumping options for "memory" admin pages
@adminManage.route("/adminTiaoNum", methods=["GET", "POST"])
@logDanger
def adminTiaoNum():
    if request.method == 'GET':
        adminTiaoNum = session.get("adminTiaoNum")
        session["adminTiaoNum"] = adminTiaoNum if adminTiaoNum != 0 and adminTiaoNum != "0" else "0"
        if adminTiaoNum is not None and adminTiaoNum != "0" and adminTiaoNum != 0:
            return str(adminTiaoNum)
        else:
            return "1"
    elif request.method == 'POST':
        session["adminTiaoNum"] = str(request.form.get("adminTiaoNum"))
        return "1"


# Agree to the article being reviewed
@adminManage.route("/passDraft", methods=["POST"])
@logDanger
def passDraft():
    articleid = int(request.form.get("articleid"))
    userid = instanceArticle.searchUseridByArticleid(articleid)
    username = instanceUser.searchUsernameByUserd(userid)
    nickname = instanceUser.searchNicknameByUserid(userid)
    headline = instanceArticle.searchHeadlineByArticleid(articleid)
    info = f"userid is {userid},nickname is {username},nickname is {nickname} Administrators pass articleid is {articleid},headline is {headline} draft"
    listLogger(userid, info, [3])
    adminLog(info)
    authorUserid = instanceArticle.searchUseridByArticleid(articleid)
    authorUsername = instanceUser.searchUsernameByUserd(authorUserid)
    authorNickname = instanceUser.searchNicknameByUserid(authorUserid)
    info = f"userid is {authorUserid},nickname is {authorUsername},nickname is {authorNickname} Administrators pass articleid is {articleid},headline is {headline} draft"
    listLogger(authorUserid, info, [3])
    instanceArticle.passDraft(articleid)
    return "1"


# Rejecting articles from review
@adminManage.route("/rejectDraft", methods=["POST"])
@logDanger
def rejectDraft():
    articleid = int(request.form.get("articleid"))
    userid = instanceArticle.searchUseridByArticleid(articleid)
    username = instanceUser.searchUsernameByUserd(userid)
    nickname = instanceUser.searchNicknameByUserid(userid)
    headline = instanceArticle.searchHeadlineByArticleid(articleid)
    info = f"userid is {userid},nickname is {username},nickname is {nickname} Administrators reject articleid is {articleid},headline is {headline} draft"
    listLogger(userid, info, [3])
    adminLog(info)
    authorUserid = instanceArticle.searchUseridByArticleid(articleid)
    authorUsername = instanceUser.searchUsernameByUserd(authorUserid)
    authorNickname = instanceUser.searchNicknameByUserid(authorUserid)
    info = f"userid is {authorUserid},nickname is {authorUsername},nickname is {authorNickname} Administrators reject articleid is {articleid},headline is {headline} draft"
    listLogger(authorUserid, info, [3])
    instanceArticle.passDraft(articleid)
    return "1"


# Preview of draft articles
@adminManage.route("/reviewDraft/<int:articleid>")
@logDanger
def reviewDraft(articleid):
    articleid = int(articleid)
    article = instanceArticle.reviewDraft(articleid)
    return render_template("reviewDraft.html", article=article)

# hide article
@adminManage.route("/hideArticle",methods=["POST"])
@logDanger
def hideArticle():
    userid=session.get("userid")
    username=instanceUser.searchUsernameByUserd(userid)
    articleid = request.form.get('articleid')
    instanceArticle.hideArticle(articleid)
    info=f"userid is {userid}, username is {username} of the administrator, hidden articleid is {articleid} of the article"
    listLogger(userid, info, [3])
    adminLog(info)
    return "1"

# cancle hide article
@adminManage.route("/cancleHideArticle",methods=["POST"])
@logDanger
def cancleHideArticle():
    userid=session.get("userid")
    username=instanceUser.searchUsernameByUserd(userid)
    articleid = request.form.get('articleid')
    instanceArticle.cancleHideArticle(articleid)
    info=f"userid is {userid}, username is {username} of the administrator, cancle hide articleid is {articleid} of the article"
    listLogger(userid, info, [3])
    adminLog(info)
    return "1"

# recommended the article
@adminManage.route("/recommendedArticle",methods=["POST"])
@logDanger
def recommendedArticle():
    userid = session.get("userid")
    username = instanceUser.searchUsernameByUserd(userid)
    articleid = request.form.get('articleid')
    instanceArticle.recommendedArticle(articleid)
    info=f"userid is {userid},username is {username} of the administrator,recommended articleid is {articleid} of the article"
    listLogger(userid, info, [3])
    adminLog(info)
    return "1"

# cancle recommended the article
@adminManage.route("/cancleRecommendedArticle",methods=["POST"])
@logDanger
def cancleRecommendedArticle():
    userid = session.get("userid")
    username = instanceUser.searchUsernameByUserd(userid)
    articleid = request.form.get('articleid')
    instanceArticle.cancleRecommendedArticle(articleid)
    info=f"userid is {userid},username is {username} of the administrator,cancle recommended articleid is {articleid} of the article"
    listLogger(userid, info, [3])
    adminLog(info)
    return "1"