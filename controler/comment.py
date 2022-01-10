from flask import Blueprint, request, session, jsonify

from common.myLog import myLogger, allLogger, ininUserDir
from common.utility import getIpForFlask
from constant import howCommentInArticle
from constant import replyAndAddCommentCredit
from database.instanceDatabase import instanceArticle, instanceLog, instanceComment

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
                allLogger(0, e)
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
                instanceLog.insert_detail(type="回复评论", target=articleid, credit=replyAndAddCommentCredit,
                                          info=f"回复commentid为{commentid}的评论")
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
    # 再添加一条作者对这些评论的赞同反对的情况
    # 赞成返回1 反对返回2 不赞同不反对返回0
    for i in range(len(list)):
        list[i]["agreeOrdisAgreeType"] = instanceLog.whetherAgreeOrDisInThisComment(list[i]["commentid"])
    return jsonify(list)


# 为赞同或反对加一
@comment.route("/agreeComment", methods=["POST"])
def agreeComment():
    commentid = request.form.get("commentid")
    instanceLog.whetherAgreeOrDisInThisComment(commentid)
    authorId = instanceComment.searchUseridByCommentid(commentid)
    userid = session.get("userid")
    nickname = session.get("nickname")
    ip = getIpForFlask()
    ininUserDir(userid=authorId)
    try:
        instanceComment.update_agreecount(commentid)
        instanceLog.insert_detail(type="赞同评论", target=commentid, credit=0,
                                  info=f"赞同评论commentid为{commentid}的评论")
        myLogger(9, f"用户id为{userid} 昵称为{nickname} 赞同了用户id为{authorId} 的评论id号为{commentid}的评论 其赞同人的ip地址为{ip}",
                 userid=userid)
        myLogger(10,
                 f"用户id为{userid} 昵称为{nickname} 赞同了用户id为{authorId} 的评论id号为{commentid}的评论 其赞同人的ip地址为{ip}",
                 userid=authorId)
        return "1"
    except Exception as e:
        allLogger(0, e)
        return "0"


@comment.route("/disagreeComment", methods=["POST"])
def disagreeComment():
    commentid = request.form.get("commentid")
    authorId = instanceComment.searchUseridByCommentid(commentid)
    userid = session.get("userid")
    nickname = session.get("nickname")
    ip = getIpForFlask()
    ininUserDir(userid=authorId)
    try:
        instanceComment.update_disagreecount(commentid)
        instanceLog.insert_detail(type="反对评论", target=commentid, credit=0,
                                  info=f"反对评论commentid为{commentid}的评论")
        myLogger(9, f"用户id为{userid} 昵称为{nickname} 反对了用户id为{authorId} 的评论id号为{commentid}的评论 其反对人的ip地址为{ip}",
                 userid=userid)
        myLogger(10,
                 f"用户id为{userid} 昵称为{nickname} 反对了用户id为{authorId} 的评论id号为{commentid}的评论 其反对人的ip地址为{ip}",
                 userid=authorId)
        return "1"
    except Exception as e:
        allLogger(0, e)
        return "0"


# 为赞同或反对减1
@comment.route("/cancle_agreeComment", methods=["POST"])
def cancle_agreeComment():
    commentid = request.form.get("commentid")
    authorId = instanceComment.searchUseridByCommentid(commentid)
    userid = session.get("userid")
    nickname = session.get("nickname")
    ip = getIpForFlask()
    ininUserDir(userid=authorId)
    try:
        instanceComment.cancle_update_agreecount(commentid)
        instanceLog.insert_detail(type="取消赞同评论", target=commentid, credit=0,
                                  info=f"取消赞同评论commentid为{commentid}的评论")
        myLogger(9, f"用户id为{userid} 昵称为{nickname} 取消赞同了用户id为{authorId} 的评论id号为{commentid}的评论 其取消赞同人的ip地址为{ip}",
                 userid=userid)
        myLogger(10,
                 f"用户id为{userid} 昵称为{nickname} 取消赞同了用户id为{authorId} 的评论id号为{commentid}的评论 其取消赞同人的ip地址为{ip}",
                 userid=authorId)
        return "1"
    except Exception as e:
        allLogger(0, e)
        return "0"


@comment.route("/cancle_disagreeComment", methods=["POST"])
def cancle_disagreeComment():
    commentid = request.form.get("commentid")
    authorId = instanceComment.searchUseridByCommentid(commentid)
    userid = session.get("userid")
    nickname = session.get("nickname")
    ip = getIpForFlask()
    ininUserDir(userid=authorId)
    try:
        instanceComment.cancle_update_disagreecount(commentid)
        instanceLog.insert_detail(type="取消反对评论", target=commentid, credit=0,
                                  info=f"取消反对评论commentid为{commentid}的评论")
        myLogger(9, f"用户id为{userid} 昵称为{nickname} 取消反对了用户id为{authorId} 的评论id号为{commentid}的评论 其取消反对人的ip地址为{ip}",
                 userid=userid)
        myLogger(10,
                 f"用户id为{userid} 昵称为{nickname} 取消反对了用户id为{authorId} 的评论id号为{commentid}的评论 其取消反对人的ip地址为{ip}",
                 userid=authorId)
        return "1"
    except Exception as e:
        allLogger(0, e)
        return "0"


#   隐藏评论
@comment.route("/hideComment", methods=["POST"])
def hideComment():
    commentid = request.form.get("commentid")
    try:
        instanceComment.hideCommentByCommentid(commentid)
        return "1"
    except Exception as e:
        allLogger(0, e)
        return "0"
