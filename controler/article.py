import math

from flask import Blueprint, make_response, session, request, redirect, url_for, abort, render_template
from common.utility import ImageCode, gen_email_code, send_email, parser_image_url, generate_thumb
import re, hashlib

from database.article import Article
from database.comment import Comment
from database.credit import Credit
from database.favorite import Favorite
from database.users import Users

article = Blueprint("article", __name__)


@article.route("/article/<int:articleid>")
def read(articleid):
    article = Article()
    credit = Credit()
    try:
        result = article.find_by_id(articleid)
        if result is None:
            abort(404)
    except:
        abort(500)

    dict = {}
    for k, v in result[0].__dict__.items():
        if not k.startswith("_sa_instance_state"):
            dict[k] = v
    dict["nickname"] = result.nickname
    if credit.check_paid_article(articleid):
        dict["paid"] = "true"
    else:
        dict["paid"] = "false"

    favo = Favorite()
    is_favorite = favo.check_favorite(articleid)

    # 获取当前文章的上一篇、下一篇
    prev_next = article.find_prev_next_by_id(articleid)

    # 获取评论
    comment = Comment()
    # comment_user=comment.find_limit_with_user(articleid,0,50)
    comment_list = comment.get_comment_user_list(articleid, 0, 10)
    # print(comment_list)
    count = comment.get_count_by_article(articleid)
    total = math.ceil(count / 10)
    return render_template("artical.html", article=dict, is_favorite=is_favorite, prev_next=prev_next,
                           comment_list=comment_list, total=total)


@article.route("/readAll", methods=["POST"])
def readAll():
    articleid = request.form.get("articleid")
    article = Article()
    result = article.find_by_id(articleid)
    # 修改插入积分
    credit = Credit()
    credit.insert_detail(type="阅读文章", target=articleid, credit=-1 * result[0].credit)
    # 减少用户的剩余积分
    users = Users()
    users.update_credit(credit=-1 * result[0].credit)
    # print(articleid)
    return "1"


@article.route("/prepost")
def pre_post():
    return render_template("write.html")


@article.route("/article", methods=["POST"])
def add_article():
    headline = request.form.get("headline")
    content = request.form.get("content")
    type = int(request.form.get("type"))
    credit = int(request.form.get("credit"))
    drafted = int(request.form.get("drafted"))
    checked = int(request.form.get("checked"))
    articleid = int(request.form.get("articleid"))
    article = Article()
    if session.get("userid") is None:
        return "perm-denied"
    else:
        user_temp = Users()
        user = user_temp.find_by_userid(session.get("userid"))
        if user.role == "editor":
            # 权限合格，可以执行发布文章的代码
            # 首先为文章生成缩略图，如果没有，就随机生成一张
            url_list = parser_image_url(content)
            if len(url_list) > 0:
                thumbname = generate_thumb(url_list)
            else:
                # 如果文章中没有图片，那么就根据文章类型指定一个
                thumbname = "%d.png" % (int(type))
            if articleid == 0:  # 如果为0说明是新数据
                try:
                    id = article.insert_article(type=type, headline=headline, content=content, credit=credit,
                                                drafted=drafted, checked=checked, thumbnail=thumbname)
                    return str(id)
                except Exception as e:
                    return "post-fail"
            else:
                # 如果是已经添加过的文章，只做修改操作
                try:
                    id = article.update_article(articleid=articleid, type=type, headline=headline, content=content,
                                                credit=credit, thumbnail=thumbname, drafted=drafted, checked=checked)
                    return str(id)
                except:
                    return "post-fail"
        # 弱国角色不是作者，只能投稿，不能正式发布
        # 只有作者，才能发布一篇不经审核的文章
        elif checked == 1:
            return "perm-denied"
        else:
            return "perm-denied"
