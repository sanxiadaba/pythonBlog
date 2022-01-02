from flask import Blueprint, request, session, jsonify
from database.instanceDatabase import instanceArticle,instanceCredit,instanceUser,instanceComment

comment = Blueprint("comment", __name__)


# 可以用拦截器
# 未登录的不能通过直接访问端口发送评论
@comment.before_request
def before_comment():
    if session.get("islogin") is None or session.get("islogin") != "true":
        return "not-login"
    else:
        pass

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
                instanceCredit.insert_detail(type="添加评论", target=articleid, credit=2)
                instanceUser.update_credit(2)
                instanceArticle.update_replycount(articleid)
                return "add-pass"
            except Exception as ex:
                print(ex)
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
        if not instanceComment.check_limit_per_5():
            try:
                instanceComment.insert_reply(articleid=articleid, commentid=commentid, ipaddr=ipaddr, content=content)
                instanceCredit.insert_detail(type="添加评论", target=articleid, credit=2)
                instanceUser.update_credit(2)
                instanceArticle.update_replycount(articleid)
                return "reply-pass"
            except:
                return "reply-fail"
        else:
            return "reply-limit"


@comment.route("/comment/<int:articleid>-<int:page>")
def comment_page(articleid, page):
    start = (page - 1) * 10
    list = instanceComment.get_comment_user_list(articleid, start, 10)
    return jsonify(list)
