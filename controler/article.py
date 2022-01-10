import math
from flask import Blueprint, session, request, abort, render_template
from common.utility import  parser_image_url, generate_thumb
from database.instanceDatabase import instanceUser,instanceArticle,instanceComment,instanceLog,instanceFavorite
from constant import postArticleCredit,rateCreditForArticle,howCommentInArticle
from common.myLog import myLogger
article = Blueprint("article", __name__)


@article.route("/article/<int:articleid>")
def read(articleid):
    restOfCredit=instanceUser.findRestCredit()
    try:
        result = instanceArticle.find_by_id(articleid)
        if result is None:
            abort(404)
    except:
        abort(500)

    dict = {}
    for k, v in result[0].__dict__.items():
        if not k.startswith("_sa_instance_state"):
            dict[k] = v
    dict["nickname"] = result.nickname
    #  检查是否已经买了这个文章，这样的话，再次点击就用再买  #作者的话默认买过了
    if instanceLog.check_paid_article(articleid) or int(session.get("userid"))==  int(instanceArticle.searchUseridByArticleid(articleid)[0]):
        dict["paid"] = "true"
    else:
        dict["paid"] = "false"

    is_favorite = instanceFavorite.check_favorite(articleid)

    # 获取当前文章的上一篇、下一篇
    prev_next = instanceArticle.find_prev_next_by_id(articleid)

    # 获取评论
    # 一页获取十条
    comment_list = instanceComment.get_comment_user_list(articleid, 0, howCommentInArticle)
    count = instanceComment.get_count_by_article(articleid)
    total = math.ceil(count / howCommentInArticle)
    for i in range(len(comment_list)):
        comment_list[i]["agreeOrdisAgreeType"] = instanceLog.whetherAgreeOrDisInThisComment(comment_list[i]["commentid"])
    return render_template("article.html", article=dict, is_favorite=is_favorite, prev_next=prev_next,
                           comment_list=comment_list, total=total,restOfCredit=restOfCredit)
@article.route("/readAll", methods=["POST"])
def readAll():
    articleid = request.form.get("articleid")
    result = instanceArticle.find_by_id(articleid)
    # 读者花费的的积分
    readerPaidedCredit=result[0].credit
    #  作者得到的积分
    authorGettedCredit=math.ceil(rateCreditForArticle * result[0].credit)
    # 这篇文章的作者id
    userid=int(instanceArticle.searchUseridByArticleid(articleid)[0])
    # 这篇作者的nickname
    nickname=instanceUser.searchNicknameByUserid(userid)
    # 减去自己的积分
    instanceLog.insert_detail(type="购买文章", target=articleid, credit=-1 * readerPaidedCredit,info=f"消耗{readerPaidedCredit}积分")
    # logger.info(f"userid 为{session.get('userid')},昵称为{nickname} 的读者")
    # 增加阅读量
    instanceArticle.update_read_count(articleid)
    # 增加作者的积分
    instanceLog.insert_detail(type="别人阅读", target=articleid, credit=authorGettedCredit, userid=userid,info=f"获取{math.ceil(rateCreditForArticle * result[0].credit)}积分")
    return "1"


@article.route("/prepost")
def pre_post():
    return render_template("write.html")



# 发布文章的按钮
@article.route("/article", methods=["POST"])
def add_article():
    headline = request.form.get("headline")
    content = request.form.get("content")
    type = int(request.form.get("type"))
    credit =int(request.form.get("credit"))
    if credit is None:
        credit=0
    drafted = int(request.form.get("drafted"))
    checked = int(request.form.get("checked"))
    articleid = int(request.form.get("articleid"))
    if session.get("userid") is None:
        return "perm-denied"
    else:
        user = instanceUser.find_by_userid(session.get("userid"))
        if user.role == "editor" or user.role == "admin" or checked==1:
            # 权限合格，可以执行发布文章的代码
            # 首先为文章生成缩略图，如果没有，就随机生成一张
            url_list = parser_image_url(content)
            if len(url_list) > 0:
                thumbname = generate_thumb(url_list)
            else:
                # 如果文章中没有图片，那么就根据文章类型指定一个
                thumbname = "%d.jpg" % (int(type))
            if articleid == 0:  # 如果为0说明是新文章
                try:
                    id = instanceArticle.insert_article(type=type, headline=headline, content=content, credit=credit,
                                                drafted=drafted, checked=checked, thumbnail=thumbname)
                    instanceLog.insert_detail(type="发布文章", target=0, credit=postArticleCredit)
                    return str(id)
                except Exception as e:
                    return "post-fail"
            else:
                # 如果是已经添加过的文章，只做修改操作
                try:
                    id = instanceArticle.update_article(articleid=articleid, type=type, headline=headline, content=content,
                                                credit=credit, thumbnail=thumbname, drafted=drafted, checked=checked)
                    return str(id)
                except:
                    return "post-fail"
        else:
            # 如果角色不是作者或管理员，只能投稿，不能正式发布
            # 只有作者，才能发布一篇不经审核的文章
            return "perm-denied"


