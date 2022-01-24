"""
File description.

This file is used to store some functions for article operations
such as view full text, publish articles, modify articles, etc.
Mainly operate the article table in the database

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

import math
import traceback

from flask import Blueprint, session, request, abort, render_template

from common.myLog import logDanger, listLogger, allLogger
from common.utility import parser_image_url, generate_thumb
from constant import postArticleCredit, howCommentInArticle, maxUserPostArticleNum, \
    maxUserPostArticleNumOfEditor, maxModifyArticleNum, ueiditorLanguage
from database.article import Article
from database.articleLog import ArticleLog
from database.comment import Comment
from database.credit import Credit
from database.favorite import Favorite
from database.logs import Log
from database.upload import Upload
from database.users import Users

instanceArticle = Article()
instanceArticleLog = ArticleLog()
instanceComment = Comment()
instanceCredit = Credit()
instanceFavorite = Favorite()
instanceLog = Log()
instanceUpload = Upload()
instanceUser = Users()

article = Blueprint("article", __name__)


# Load article Access article with different articleid under article
@article.route("/article/<int:articleid>")
@logDanger
def read(articleid):
    # Check the remaining points
    restOfCredit = instanceUser.findRestCredit()
    # Query the article, if you can't find the article, throw a 404 error, if other errors occur, throw a 500 error
    # Then the error page will redirect to the home page
    try:
        result = instanceArticle.find_by_id(articleid)
        if result is None:
            abort(404)
    except:
        abort(500)

    # The dic dictionary is used to store the data to be returned
    dict = {}
    for k, v in result[0].__dict__.items():
        if not k.startswith("_sa_instance_state"):
            dict[k] = v
    dict["nickname"] = result.nickname
    if session.get("islogin") == "true":
        #  Check if you have already bought this article, so that if you click again, you can buy it again by default in the author's words
        if instanceCredit.whetherPaidForArticle(articleid) or int(session.get("userid")) == int(
                instanceArticle.searchUseridByArticleid(articleid)[0]):
            dict["paid"] = "true"
        else:
            dict["paid"] = "false"
    else:
        dict["paid"] = "false"
    # Determine if the article is in your collection
    if session.get("islogin") == "true":
        is_favorite = instanceFavorite.checkFavorite(articleid)
    else:
        is_favorite = "0"
    # Get the previous and next post of the current article
    prev_next = instanceArticle.searchPrevNextArticleByArticleid(articleid)

    # Get reviews
    # Get ten on one page
    comment_list = instanceComment.searchCommentWithUser(articleid, 0, howCommentInArticle)
    count = instanceComment.searchCountOfCommentByArticleid(articleid)
    # The article has several pages of comments
    total = math.ceil(count / howCommentInArticle)
    # Determine the status of each author for each comment to facilitate the front-end loading of the corresponding page
    for i in range(len(comment_list)):
        comment_list[i]["agreeOrdisAgreeType"] = instanceLog.whetherAgreeOrDisInThisComment(
            comment_list[i]["commentid"])
    return render_template("article.html", article=dict, is_favorite=is_favorite, prev_next=prev_next,
                           comment_list=comment_list, total=total, restOfCredit=restOfCredit,
                           articleOfUserid=instanceArticle.searchUseridByArticleid(articleid)[0], articleid=articleid)


# Interface to view login status
@article.route("/islogin", methods=["POST"])
@logDanger
def islogin():
    islogin = session.get("islogin")
    return "1" if islogin == "true" else "0"


# Article to expand all, read more
@article.route("/readAll", methods=["POST"])
@logDanger
def readAll():
    # The determination of whether there are enough points here has already been done in the front-end
    articleid = request.form.get("articleid")
    result = instanceArticle.find_by_id(articleid)
    userid = session.get("userid")
    authorid = int(instanceArticle.searchUseridByArticleid(articleid)[0])
    authorNickname = instanceUser.searchNicknameByUserid(authorid)[0]
    # Points spent by readers
    readerPaidCredit = result[0].credit
    """
    If the points charged for the article are not 0
    """
    if readerPaidCredit != 0:
        # Subtract your own points #
        instanceCredit.insertDetail(type="Buy Article", target=articleid, credit=-1 * readerPaidCredit,
                                    info=f"The user with userid {userid} consumed {readerPaidCredit} points to buy the article with articleid {articleid} from the author with userid {articleid} and nickname {authorNickname}.")
    else:
        instanceCredit.insertDetail(type="Read the article", target=articleid, credit=0,
                                    info=f"The user with userid {userid} has read the article with userid {articleid} and nickname {authorNickname} with articleid {articleid}")
    # Increase article readership
    instanceArticle.updateReadCount(articleid)
    return "1"


# Load ueditor write article page
@article.route("/prepost")
@logDanger
def pre_post():
    whetherHide = False
    #  The last page that jumped, if not from the article where it jumped, will not be filled
    fromUrl = str(request.referrer)
    # Check where you are jumping from. If you are jumping from a modified article, the previous content will be filled in for modification.
    s1 = fromUrl
    if s1.split("/")[-1] == "userManage":
        session["controlBiaoNum"] = 1
    judge = True if ((s1.split("/")[-1].isdigit() is True and s1.split("/")[-2] == "article") or s1.split("/")[
        -1] == "userManage") else False
    # Fill the value of the modified page Of course, whether to fill the empty or the corresponding article needs to be determined with the articleJudge parameter
    if ueiditorLanguage == "Chinese":
        language = "zh-cn/zh-cn.js"
    elif ueiditorLanguage == "English":
        language = "en/en.js"
    else:
        allLogger(0, "ueditor language configuration error")
        language = "en/en.js"
    articleidModify = session.get("articleidModify")
    if articleidModify == "0" or articleidModify is None or judge is False:
        session["articleidModify"] = "0"
        articleContent = ""
    else:
        whetherHide = instanceArticle.searchWhetherHide(articleidModify)
        articleContent = instanceArticle.searchHeadlineAndContentByArticleid(articleidModify)["content"]
    return render_template("write.html", maxUserPostArticleNum=maxUserPostArticleNum, articleContent=articleContent,
                           maxUserPostArticleNumOfEditor=maxUserPostArticleNumOfEditor,
                           maxModifyArticleNum=maxModifyArticleNum, whetherHide=whetherHide, language=language)


# Button for posting articles
@article.route("/article", methods=["POST"])
@logDanger
def addArticle():
    # Here the code is written in a very messy way and unknowingly becomes a mountain of shit
    headline = request.form.get("headline")
    content = request.form.get("content")
    # The title of the article cannot be less than five and the content is not less than 100
    if (len(headline) < 5 or len(content) < 100):
        return "invalided"
    type = int(request.form.get("type"))
    typeArticle = type
    credit = int(request.form.get("credit"))
    credit = 0 if credit is None else credit
    credit = int(credit)
    drafted = int(request.form.get("drafted"))
    checked = int(request.form.get("checked"))
    articleid = int(request.form.get("articleid"))
    userid = session.get("userid")
    # Used to determine what operation the front-end is performing #1. save draft 2. publish article 3. drop article 4. modify article
    judgeType = int(request.form.get("judgeType"))
    info = ""

    # And then determine whether today exceeded the limit of the submission (judged by 1, 2, 3 not judged by the number of revisions)
    # Add the corresponding log table and log log records
    if instanceArticleLog.checkLimitUpload() is True and judgeType in range(1, 4):
        if judgeType == 1:
            info = f"Users with userid {userid} exceeded the limit of the number of drafts saved per day."
            type = "Failed to save draft"
        elif judgeType == 2:
            type = "Posting article failed"
            info = f"Users with userid {userid} have exceeded the limit of the number of posts per day for editors"
        elif judgeType == 3:
            type = "Failed to submit article"
            info = f"Users with userid {userid} have exceeded the limit for posting articles"
        instanceLog.insertDetail(type=type, target=0, credit=0, info=info)
        listLogger(userid, info, [3])
        instanceArticleLog.insertDetail(articleid=articleid, type=type, info=info)
        return f"limit-error-{judgeType}"
    # Then determine the number of modifications
    if instanceArticleLog.checkLimitModify() is True and judgeType == 4:
        info = f"Users with userid {userid} have exceeded the daily limit of post modifications"
        type = "Modification failure"
        instanceLog.insertDetail(type=type, target=0, credit=0, info=info)
        listLogger(userid, info, [3])
        instanceArticleLog.insertDetail(articleid=articleid, type=type, info=info)
        return "modify-limited"
    # Generate thumbnails for articles, if not, generate a random one
    url_list = parser_image_url(content)
    # If the article has images, then generate thumbnails for the article according to certain rules, otherwise assign a thumbnail with the corresponding serial number to it
    if len(url_list) > 0:
        thumbname = generate_thumb(url_list, userid)
        instanceUpload.insertDetail(imgname=thumbname, info="Upload thumbnails")
    else:
        # If there is no image in the article, then specify one based on the article type
        thumbname = "default/" + "%d.jpg" % (int(type))
    if judgeType != 4:  # Direct insert database operations
        try:
            # Returns the id of the newly inserted article
            id = instanceArticle.insertArticle(type=typeArticle, headline=headline, content=content, credit=credit,
                                               drafted=drafted, checked=checked, thumbnail=thumbname)
            # If an article is edited and published successfully, credit is given.
            if judgeType == 2:
                info = f"The editor whose userid is {userid} needs to consume {credit} for articles whose articleid is {id}, and is awarded {postArticleCredit} points"
                type = "Post Article"
                # Bonus points here
                instanceCredit.insertDetail(type=type, credit=postArticleCredit, target=id, info=info)
                # Save log here
                listLogger(userid, info, [3, 5])

            # Normal users save drafts
            elif judgeType == 1:
                type = "Save draft"
                info = f"Normal users with userid of {userid} Save articles with articleid of {id} that need to consume {credit}"
                instanceLog.insertDetail(type=type, credit=0, target=id, info=info)
                listLogger(userid, info, [3])
            elif judgeType == 3:
                type = "Submit an article"
                info = f"The normal user with userid {userid} submits articles with articleid {id} that need to consume {credit}"
                # Bonus points here
                instanceCredit.insertDetail(type=type, credit=postArticleCredit, target=id, info=info)
                # Save log here
                listLogger(userid, info, [3, 5])
            instanceArticleLog.insertDetail(articleid=id, type=type, info=info)
            return str(id)
        except:
            e = traceback.format_exc()
            allLogger(0, e)
            return "post-fail"
    else:
        # If it is an article that has already been added, only modify the operation
        try:
            whetherDrafted = instanceArticle.searchWhetherDrafted(articleid)
            if whetherDrafted is True:
                drafted = 1

            id = instanceArticle.updateArticle(articleid=articleid, type=typeArticle, headline=headline,
                                               content=content,
                                               credit=credit, thumbnail=thumbname, drafted=drafted,
                                               checked=checked)
            if whetherDrafted is False:
                type = "Modify article"
                info = f"Users with userid {userid} have modified articles with articleid {id} that need to consume {credit}"
                instanceLog.insertDetail(type="Modify article", credit=0, target=id, info=info)
                instanceArticleLog.insertDetail(articleid=articleid, type=type, info=info)
                listLogger(userid, info, [3])
                return str(id)
            else:
                type = "Revision Draft"
                info = f"Users whose userid is {userid} need to consume the draft of {credit} if the articleid of the article is {id} modified"
                instanceLog.insertDetail(type="Revision Draft", credit=0, target=id, info=info)
                instanceArticleLog.insertDetail(articleid=articleid, type=type, info=info)
                listLogger(userid, info, [3])
                # A status code to determine modifications
                return "xiu"
        except:
            e = traceback.format_exc()
            allLogger(0, e)
            return "post-fail"


# Modify the port accessed during the article
@article.route("/modifyArticle/<int:articleid>", methods=["GET"])
@logDanger
def modifyArticle(articleid):
    result = instanceArticle.searchHeadlineAndContentByArticleid(articleid)
    return result


# Used to receive the id of the current article (used when modifying the article)
# Here it is still mainly for the purpose of modifying the article
@article.route('/centerVar',
               methods=['GET', 'POST'])  # Set the route to allow both GET and POST methods to be accessible
@logDanger
def centerVar():
    if request.method == 'GET':
        articleidModify = session.get("articleidModify")
        if articleidModify is not None or articleidModify != "0":
            return str(articleidModify)
        else:
            return "0"
    elif request.method == 'POST':
        session["articleidModify"] = str(request.form.get("articleid"))
        return "1"
