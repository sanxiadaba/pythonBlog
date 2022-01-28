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
from common.myLog import logDanger
from constant import classification, commentNum, regGiveCredit, loginEvereDayCredit, postArticleCredit, \
    replyAndAddCommentCredit, rateCreditForArticle, creditListForReleaseArticle, howArticleInWeb, howCommentInArticle, \
    maxUserPostArticleNum, maxUserPostArticleNumOfEditor, maxModifyArticleNum, maxUploadPicNum, ueiditorLanguage, \
    recommendedNumOfSide
from database.article import Article
from database.logs import Log
from database.users import Users

adminManage = Blueprint("adminManage", __name__)

instanceArticle = Article()
instanceUser = Users()
instanceLog = Log()


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
    webInfo["ueiditorLanguage"] = ueiditorLanguage

    end = time.time()
    loadTime = end - start
    webInfo["loadTime"] = loadTime
    return render_template("adminManage.html", webInfo=webInfo)


# Jumping options for "memory" admin pages
@adminManage.route("/adminTiaoNum", methods=["GET", "POST"])
@logDanger
def adminTiaoNum():
    if request.method == 'GET':
        adminTiaoNum = session.get("adminTiaoNum")
        session["adminTiaoNum"] = 0
        if adminTiaoNum is not None and adminTiaoNum != "0":
            return str(adminTiaoNum)
        else:
            return "0"
    elif request.method == 'POST':
        session["adminTiaoNum"] = str(request.form.get("adminTiaoNum"))
        return "1"
