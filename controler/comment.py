"""
文件说明：

本界面主要是对评论相关内容的控制
比如加载评论、赞成、反对、取消赞成评论
主要对数据库的comment表进行操作

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
        # 对评论内容进行校验
        # 如果评论超过1000字或小于五个字
        if len(content) < 5 or len(content) > 1000:
            return "content-invalid"
        # 没人每天只能评论一定次数
        if not instanceComment.whetherLimitEveryDayCommentNum():
            try:
                # 评论成功后，更新积分明细和剩余积分，及文章的回复数量
                info = f"userid为{userid}的用户 对作者id为{authorid}文章id为{articleid}进行了回复,并且获取{replyAndAddCommentCredit}积分"
                instanceComment.insertComment(articleid, content, info=info)
                instanceCredit.insertDetail(type="添加评论", target=articleid, credit=replyAndAddCommentCredit, info=info)
                instanceLog.insertDetail(type="文章被评论", target=articleid, credit=0, info=info)
                instanceArticle.updateReplyCount(articleid)
                listLogger(userid, info, [7, 5])
                # 接下来是被评论人对应的log日志
                listLogger(authorid, info, [6, 7])
                return "add-pass"
            except:
                e = traceback.format_exc()
                allLogger(0, e)
                return "add-fail"
        else:
            # 未评论成功的日志
            info = f"userid为{userid}的用户 对作者id为{authorid}文章id为{articleid}进行了回复,但是今日的评论次数已超过限制"
            instanceLog.insertDetail(type="添加评论失败", target=articleid, credit=0, info=info)
            listLogger(userid, info, [7])
            return "add-limit"
    else:
        return "not-login"


# 回复原始评论（回复其它人的评论，最多只能“套娃”到这，即回复原始评论的评论不可被评论）
@comment.route("/reply", methods=["POST"])
@logDanger
def reply():
    articleid = request.form.get("articleid")
    commentid = request.form.get("commentid")
    content = request.form.get("content").strip()
    ipaddr = request.remote_addr
    userid = session.get("userid")
    # 通过commentid获取原作者id
    authorid = instanceComment.searchUseridByCommentid(commentid)
    # 通过userid获取作者的昵称 方便后面的写日志
    authorNickname = instanceUser.searchNicknameByUserid(authorid)[0]
    if len(content) < 5 or len(content) > 1000:
        return "content-invaild"
    # 判断每天的评论限制 （每天的评论次数也有限制，这些都可以在constant文件修改）
    if not instanceComment.whetherLimitEveryDayCommentNum():
        try:
            info = f"userid为{userid}的用户，在articleid为{articleid}的文章中回复了userid为{authorid},昵称为{authorNickname}的commentid为{commentid}的评论"
            instanceComment.insertArticleComment(articleid=articleid, commentid=commentid, ipaddr=ipaddr, content=content,
                                                 info=info)
            instanceCredit.insertDetail(type="回复原始评论", target=articleid, credit=replyAndAddCommentCredit, info=info)
            instanceLog.insertDetail(type="评论被回复", target=articleid, credit=0, info=info)
            # 回复原始评论也算文章的评论
            instanceArticle.updateReplyCount(articleid)
            listLogger(userid, info, [7, 5])
            # 接下来是被评论人对应的log日志
            listLogger(authorid, info, [6, 10])
            return "reply-pass"
        except:
            e = traceback.format_exc()
            allLogger(0, e)
            return "reply-fail"
    else:
        info = f"userid为{userid}的用户，在articleid为{articleid}的文章中回复了userid为{authorid},昵称为{authorNickname}的commentid为{commentid}的评论，但因为次数限制失败了"
        instanceLog.insertDetail(type="回复原始评论失败", target=articleid, credit=0, info=info)
        listLogger(userid, info, [7])
        return "reply-limit"


# 获取加载评论的页面，将数据填充到前端
@comment.route("/comment/<int:articleid>-<int:page>", methods=["GET"])
@logDanger
def comment_page(articleid, page):
    start = (page - 1) * howCommentInArticle
    list = instanceComment.searchCommentWithUser(articleid, start, howCommentInArticle)
    # 再添加一条作者对这些评论的赞同反对的情况
    # 赞成返回1 反对返回2 不赞同不反对返回0
    for i in range(len(list)):
        list[i]["agreeOrdisAgreeType"] = instanceLog.whetherAgreeOrDisInThisComment(list[i]["commentid"])
    return jsonify(list)


"""
下面四个函数主要是执行赞同、反对评论以及取消赞同、反对评论的操作
"""


# 为赞同加一
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
        info = f"用户id为{userid} 昵称为{nickname} 赞同了用户id为{authorId} 昵称为{authorNickname} 的评论id号为{commentid}的评论 "
        instanceLog.insertDetail(type="赞同评论", target=commentid, credit=0,
                                 info=info)
        instanceLog.insertDetail(type="评论被赞同", target=commentid, credit=0,
                                 info=info)
        listLogger(userid, info, [9])
        listLogger(authorId, info, [10])
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# 反对加一
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
        info = f"用户id为{userid} 昵称为{nickname} 反对了用户id为{authorId} 昵称为{authorNickname} 的评论id号为{commentid}的评论 "
        instanceLog.insertDetail(type="反对评论", target=commentid, credit=0,
                                 info=info)
        instanceLog.insertDetail(type="评论被反对", target=commentid, credit=0,
                                 info=info)
        listLogger(userid, info, [9])
        listLogger(authorId, info, [10])
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# 为赞同或反对减1
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
        info = f"用户id为{userid} 昵称为{nickname} 取消赞成了用户id为{authorId} 昵称为{authorNickname} 的评论id号为{commentid}的评论 "
        instanceLog.insertDetail(type="取消赞成评论", target=commentid, credit=0,
                                 info=info)
        instanceLog.insertDetail(type="评论取消被赞同", target=commentid, credit=0,
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
        info = f"用户id为{userid} 昵称为{nickname} 取消反对了用户id为{authorId} 昵称为{authorNickname} 的评论id号为{commentid}的评论 "
        instanceLog.insertDetail(type="取消反对评论", target=commentid, credit=0,
                                 info=info)
        instanceLog.insertDetail(type="评论被取消反对", target=commentid, credit=0,
                                 info=info)
        listLogger(userid, info, [9])
        listLogger(authorId, info, [10])
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


#   隐藏评论  即将原评论的hide值变为1
@comment.route("/hideComment", methods=["POST"])
def hideComment():
    commentid = request.form.get("commentid")
    authorId = instanceComment.searchUseridByCommentid(commentid)
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorNickname = instanceUser.searchNicknameByUserid(authorId)[0]
    try:
        instanceComment.hideCommentByCommentid(commentid)
        # 隐藏评论后，这个文章的回复数减去一
        instanceArticle.subtractReplycount(articleid=authorId)
        info = f"用户id为{userid} 昵称为{nickname} 删除了用户id为{authorId} 昵称为{authorNickname} 的评论id号为{commentid}的评论 "
        instanceLog.insertDetail(type="删除评论", target=commentid, credit=0,
                                 info=info)
        listLogger(userid, info, [9])
        if userid != authorId:
            listLogger(authorId, info, [10])
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"
