from flask import Blueprint, request, session, jsonify
from database.instanceDatabase import instanceArticle,instanceLog,instanceUser,instanceComment
from constant import replyAndAddCommentCredit
from constant import howCommentInArticle
from common.myLog import logger
comment = Blueprint("comment", __name__)

# 新增评论
@comment.route("/comment", methods=["POST"])
def add():
    if session.get("islogin") == "true":
        articleid = request.form.get("articleid")
        content = request.form.get("content").strip()
        ipaddr = request.remote_addr

        # 对评论内容进行校验
        # 如果评论超过1000字或小于五个字
        if len(content) < 5 or len(content) > 1000:
            return "content-invalid"
        # 没人每天只能评论5次
        if not instanceComment.check_limit_per_day():
            try:
                instanceComment.insert_comment(articleid, content, ipaddr)
                # 评论成功后，更新积分明细和剩余积分，及文章的回复数量
                instanceLog.insert_detail(type="添加评论", target=articleid, credit=replyAndAddCommentCredit)
                instanceArticle.update_replycount(articleid)
                return "add-pass"
            except Exception as e:
                logger.error(e)
                return "add-fail"
        else:
            return "add-limit"
    else:
        return "not-login"


@comment.route("/reply", methods=["POST"])
def reply():
    if session.get("islogin") == "false":
        return "not-login"
    else:
        articleid = request.form.get("articleid")
        commentid = request.form.get("commentid")
        content = request.form.get("content").strip()
        ipaddr = request.remote_addr

        if len(content) < 5 or len(content) > 1000:
            return "content-invaild"
        if not instanceComment.check_limit_per_day():
            try:
                instanceComment.insert_reply(articleid=articleid, commentid=commentid, ipaddr=ipaddr, content=content)
                instanceLog.insert_detail(type="回复评论", target=articleid, credit=replyAndAddCommentCredit)
                instanceArticle.update_replycount(articleid)
                return "reply-pass"
            except:
                return "reply-fail"
        else:
            return "reply-limit"


@comment.route("/comment/<int:articleid>-<int:page>", methods=["GET"])
def comment_page(articleid, page):
    start = (page - 1) * howCommentInArticle
    list = instanceComment.get_comment_user_list(articleid, start, howCommentInArticle)
    return jsonify(list)


# 为赞同或反对加一
@comment.route("/agreeComment", methods=["POST"])
def agreeComment():
    commentid = request.form.get("commentid")
    try:
        instanceComment.update_agreecount(commentid)
        return "1"
    except Exception as e:
        logger.error(e)
        return "0"

@comment.route("/disagreeComment", methods=["POST"])
def disagreeComment():
    commentid = request.form.get("commentid")
    try:
        instanceComment.update_disagreecount(commentid)
        return "1"
    except Exception as e:
        logger.error(e)
        return "0"


# 为赞同或反对减1
@comment.route("/cancle_agreeComment", methods=["POST"])
def cancle_agreeComment():
    commentid = request.form.get("commentid")
    try:
        instanceComment.cancle_update_agreecount(commentid)
        return "1"
    except Exception as e:
        logger.error(e)
        return "0"

@comment.route("/cancle_disagreeComment", methods=["POST"])
def cancle_disagreeComment():
    commentid = request.form.get("commentid")
    try:
        instanceComment.cancle_update_disagreecount(commentid)
        return "1"
    except Exception as e:
        logger.error(e)
        return "0"



