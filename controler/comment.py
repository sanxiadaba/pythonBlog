"""
Document Description.

This interface is mainly for the control of comment related content
such as loading comments, approval, disapproval, canceling approval comments
Mainly operates on the comment table of the database

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

import traceback

from flask import Blueprint, request, session, jsonify

from common.myLog import allLogger, ininUserDir, listLogger, logDanger
from constant import howCommentInArticle
from constant import replyAndAddCommentCredit



from database.article import Article
from database.comment import Comment
from database.credit import Credit
from database.logs import Log
from database.users import Users
instanceArticle=Article()
instanceComment=Comment()
instanceCredit=Credit()
instanceLog=Log()
instanceUser=Users()

comment = Blueprint("comment", __name__)


# 添加原始评论
@comment.route("/comment", methods=["POST"])
@logDanger
def addOriginComment():
    if session.get("islogin") == "true":
        articleid = request.form.get("articleid")
        content = request.form.get("content").strip()
        userid = session.get("userid")
        authorid = int(instanceArticle.searchUseridByArticleid(articleid)[0])
        # Verify the content of the comment
        # If the comment is more than 1000 words or less than five words
        if len(content) < 5 or len(content) > 1000:
            return "content-invalid"
        # Each person can only comment a certain number of times per day
        if not instanceComment.whetherLimitEveryDayCommentNum():
            try:
                # After a successful comment, update the details of points and remaining points, and the number of replies to the article
                info = f"User with userid {userid} replied to author id {authorid} article id {articleid}, and got {replyAndAddCommentCredit} points."
                instanceComment.insertComment(articleid, content, info=info)
                instanceCredit.insertDetail(type="Add a comment", target=articleid, credit=replyAndAddCommentCredit, info=info)
                instanceLog.insertDetail(type="Article was commented", target=articleid, credit=0, info=info)
                instanceArticle.updateReplyCount(articleid)
                listLogger(userid, info, [7, 5])
                # Next is the logbook corresponding to the person being commented on
                listLogger(authorid, info, [6, 7])
                return "add-pass"
            except:
                e = traceback.format_exc()
                allLogger(0, e)
                return "add-fail"
        else:
            # 未评论成功的日志
            info = f"The user with userid {userid} has replied to the author with authorid {articleid}, but the number of comments today has exceeded the limit."
            instanceLog.insertDetail(type="添加评论失败", target=articleid, credit=0, info=info)
            listLogger(userid, info, [7])
            return "add-limit"
    else:
        return "not-login"


# Reply to the original comment (reply to other people's comments, up to "nesting" to this, that is, reply to the original comment comments can not be commented)
@comment.route("/reply", methods=["POST"])
@logDanger
def reply():
    articleid = request.form.get("articleid")
    commentid = request.form.get("commentid")
    content = request.form.get("content").strip()
    ipaddr = request.remote_addr
    userid = session.get("userid")
    # Get the original author id by commentid
    authorid = instanceComment.searchUseridByCommentid(commentid)
    # Get the author's nickname by userid for writing logs later
    authorNickname = instanceUser.searchNicknameByUserid(authorid)[0]
    if len(content) < 5 or len(content) > 1000:
        return "content-invaild"
    # Determine the daily comment limit (there is also a limit to the number of comments per day, which can be modified in the constant file)
    if not instanceComment.whetherLimitEveryDayCommentNum():
        try:
            info = f"A user with userid {userid} replied to a comment with userid {authorid}, nickname {authorNickname} and commentid {commentid} in an article with articleid {articleid}."
            instanceComment.insertArticleComment(articleid=articleid, commentid=commentid, ipaddr=ipaddr, content=content,
                                                 info=info)
            instanceCredit.insertDetail(type="Reply to original comment", target=articleid, credit=replyAndAddCommentCredit, info=info)
            instanceLog.insertDetail(type="Comments are replied to", target=articleid, credit=0, info=info)
            # Replying to the original comment also counts as a comment on the article
            instanceArticle.updateReplyCount(articleid)
            listLogger(userid, info, [7, 5])
            # Next is the logbook corresponding to the person being commented on
            listLogger(authorid, info, [6, 10])
            return "reply-pass"
        except:
            e = traceback.format_exc()
            allLogger(0, e)
            return "reply-fail"
    else:
        info = f"A user with userid {userid} replied to a comment with userid {authorid}, nickname {authorNickname} and commentid {commentid} in an article with articleid {articleid}, but it failed because of the limit"
        instanceLog.insertDetail(type="Reply to original comment failed", target=articleid, credit=0, info=info)
        listLogger(userid, info, [7])
        return "reply-limit"


# Get the page that loads the comments and populate the data to the front end
@comment.route("/comment/<int:articleid>-<int:page>", methods=["GET"])
@logDanger
def comment_page(articleid, page):
    start = (page - 1) * howCommentInArticle
    list = instanceComment.searchCommentWithUser(articleid, start, howCommentInArticle)
    # Add another approval or disapproval of these comments by the author
    # Agree to return 1 Disagree to return 2 Disagree to return 0
    for i in range(len(list)):
        list[i]["agreeOrdisAgreeType"] = instanceLog.whetherAgreeOrDisInThisComment(list[i]["commentid"])
    return jsonify(list)


"""
The following four functions mainly perform operations to approve and disapprove comments and to cancel approval and disapproval comments
"""


# For endorsement plus one
@comment.route("/agreeComment", methods=["POST"])
@logDanger
def agreeComment():
    commentid = request.form.get("commentid")
    instanceLog.whetherAgreeOrDisInThisComment(commentid)
    authorId = instanceComment.searchUseridByCommentid(commentid)
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorNickname = instanceUser.searchNicknameByUserid(authorId)[0]
    ininUserDir(userid=authorId)
    try:
        instanceComment.updataCommentAgree(commentid)
        info = f"User id is {userid} Nickname is {nickname} Endorsed the comment with id number {commentid} from user id {authorId} Nickname is {authorNickname} "
        instanceLog.insertDetail(type="Agree with the comments", target=commentid, credit=0,
                                 info=info)
        instanceLog.insertDetail(type="Comments are agreed upon", target=commentid, credit=0,
                                 info=info)
        listLogger(userid, info, [9])
        listLogger(authorId, info, [10])
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# Against plus one
@comment.route("/disagreeComment", methods=["POST"])
@logDanger
def disagreeComment():
    commentid = request.form.get("commentid")
    authorId = instanceComment.searchUseridByCommentid(commentid)
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorNickname = instanceUser.searchNicknameByUserid(authorId)[0]
    ininUserDir(userid=authorId)
    try:
        instanceComment.updataCommentAgree(commentid)
        info = f"User id {userid} Nickname {nickname} objected to a comment with id {commentid} from user id {authorId} Nickname {authorNickname} "
        instanceLog.insertDetail(type="Opposing Comments", target=commentid, credit=0,
                                 info=info)
        instanceLog.insertDetail(type="Comments are opposed", target=commentid, credit=0,
                                 info=info)
        listLogger(userid, info, [9])
        listLogger(authorId, info, [10])
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# For approval or disapproval minus 1
@comment.route("/cancle_agreeComment", methods=["POST"])
@logDanger
def cancle_agreeComment():
    commentid = request.form.get("commentid")
    authorId = instanceComment.searchUseridByCommentid(commentid)
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorNickname = instanceUser.searchNicknameByUserid(authorId)[0]
    ininUserDir(userid=authorId)
    try:
        instanceComment.updataCommentAgree(commentid)
        info = f"User id is {userid} Nickname is {nickname} Disapproved the comment with id number {commentid} from user id {authorId} Nickname is {authorNickname} "
        instanceLog.insertDetail(type="Cancel favorable comments", target=commentid, credit=0,
                                 info=info)
        instanceLog.insertDetail(type="Comments Disapproved", target=commentid, credit=0,
                                 info=info)
        listLogger(userid, info, [9])
        listLogger(authorId, info, [10])
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


@comment.route("/cancle_disagreeComment", methods=["POST"])
@logDanger
def cancle_disagreeComment():
    commentid = request.form.get("commentid")
    authorId = instanceComment.searchUseridByCommentid(commentid)
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorNickname = instanceUser.searchNicknameByUserid(authorId)[0]
    ininUserDir(userid=authorId)
    try:
        instanceComment.updataCommentAgree(commentid)
        info = f"User id is {userid} Nickname is {nickname} Unopposed comment id number {commentid} with user id is {authorId} Nickname is {authorNickname} "
        instanceLog.insertDetail(type="Cancel opposing comments", target=commentid, credit=0,
                                 info=info)
        instanceLog.insertDetail(type="Comments are cancelled against", target=commentid, credit=0,
                                 info=info)
        listLogger(userid, info, [9])
        listLogger(authorId, info, [10])
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


#   Hide comments Change the hide value of the original comment to 1
@comment.route("/hideComment", methods=["POST"])
def hideComment():
    commentid = request.form.get("commentid")
    authorId = instanceComment.searchUseridByCommentid(commentid)
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorNickname = instanceUser.searchNicknameByUserid(authorId)[0]
    try:
        instanceComment.hideCommentByCommentid(commentid)
        # After hiding comments, the number of replies to this post is subtracted by one
        instanceArticle.subtractReplycount(articleid=authorId)
        info = f"User id is {userid} Nickname is {nickname} Deleted comment id number {commentid} with user id is {authorId} Nickname is {authorNickname} "
        instanceLog.insertDetail(type="Delete Comments", target=commentid, credit=0,
                                 info=info)
        listLogger(userid, info, [9])
        if userid != authorId:
            listLogger(authorId, info, [10])
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"
