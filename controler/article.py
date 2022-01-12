


import math
import traceback

from flask import Blueprint, session, request, abort, render_template, jsonify

from common.utility import parser_image_url, generate_thumb
from constant import postArticleCredit, rateCreditForArticle, howCommentInArticle, maxUserPostArticleNum, \
    maxUserPostArticleNumOfEditor, maxModifyArticleNum
from database.instanceDatabase import instanceUser, instanceArticle, instanceComment, instanceLog, instanceFavorite, \
    instanceCredit
from common.myLog import logDanger, listLogger, allLogger

article = Blueprint("article", __name__)


# 加载文章
@article.route("/article/<int:articleid>")
@logDanger
def read(articleid):
    # 剩余的积分
    restOfCredit = instanceUser.findRestCredit()
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
    if instanceCredit.check_paid_article(articleid) or int(session.get("userid")) == int(
            instanceArticle.searchUseridByArticleid(articleid)[0]):
        dict["paid"] = "true"
    else:
        dict["paid"] = "false"
    # 判断该文章是否是自己收藏的
    is_favorite = instanceFavorite.check_favorite(articleid)

    # 获取当前文章的上一篇、下一篇
    prev_next = instanceArticle.find_prev_next_by_id(articleid)

    # 获取评论
    # 一页获取十条
    comment_list = instanceComment.get_comment_user_list(articleid, 0, howCommentInArticle)
    count = instanceComment.get_count_by_article(articleid)
    total = math.ceil(count / howCommentInArticle)
    for i in range(len(comment_list)):
        comment_list[i]["agreeOrdisAgreeType"] = instanceLog.whetherAgreeOrDisInThisComment(
            comment_list[i]["commentid"])
    return render_template("article.html", article=dict, is_favorite=is_favorite, prev_next=prev_next,
                           comment_list=comment_list, total=total, restOfCredit=restOfCredit,
                           articleOfUserid=instanceArticle.searchUseridByArticleid(articleid)[0], articleid=articleid)


# 文章展开全部，阅读全文
@article.route("/readAll", methods=["POST"])
@logDanger
def readAll():
    ##### 积分是否足够已经在前端做过判断了

    articleid = request.form.get("articleid")
    result = instanceArticle.find_by_id(articleid)
    userid=session.get("userid")
    authorid = int(instanceArticle.searchUseridByArticleid(articleid)[0])
    authorNickname = instanceUser.searchNicknameByUserid(authorid)[0]
    # 读者花费的的积分
    readerPaidedCredit = result[0].credit
    """
    如果文章收取的积分不为0
    """
    if readerPaidedCredit != 0:
        # 减去自己的积分 #
        instanceCredit.insert_detail(type="购买文章", target=articleid, credit=-1 * readerPaidedCredit,
                                     info=f"userid为{userid}的用户，消耗{readerPaidedCredit}积分，向userid为{articleid} 昵称为{authorNickname}的作者购买了的articleid为{articleid}的文章")
    else:
        instanceCredit.insert_detail(type="阅读文章", target=articleid, credit=0,
                                     info=f"userid为{userid}的用户阅读了userid为{articleid} 昵称为{authorNickname}的articleid为{articleid}的文章")
    # 增加文章阅读量
    instanceArticle.update_read_count(articleid)
    return "1"


# 加载ueditor写文章的页面
@article.route("/prepost")
@logDanger
def pre_post():
    # 填充修改页面的值 当然到底填充空还是对应的文章需要用articleJudge这个参数来判断
    articleContent = ""
    articleidModify = session.get("articleidModify")
    if articleidModify == "0" or articleidModify is None:
        articleContent=""
    else:
        articleContent = instanceArticle.searchHeadlineAndContentByArticleid(articleidModify)["content"]
    return render_template("write.html", maxUserPostArticleNum=maxUserPostArticleNum, articleContent=articleContent,
                           maxUserPostArticleNumOfEditor=maxUserPostArticleNumOfEditor,
                           maxModifyArticleNum=maxModifyArticleNum)


# 发布文章的按钮
@article.route("/article", methods=["POST"])
@logDanger
def addArticle():
    headline = request.form.get("headline")
    content = request.form.get("content")
    if (len(headline) < 5 or len(content) < 100):
        return "invalided"
    type = int(request.form.get("type"))
    credit = int(request.form.get("credit"))
    credit = 0 if credit is None else credit
    drafted = int(request.form.get("drafted"))
    checked = int(request.form.get("checked"))
    articleid = int(request.form.get("articleid"))
    userid = session.get("userid")
    # 用来判断前端执行的是什么操作  #1.保存草稿 2.发布文章 3.投递文章 4.修改文章
    judgeType = int(request.form.get("judgeType"))
    info = ""
    # 再判断今天是否超出了投稿的限制(判断的是1、2、3不判断修改次数)
    # 添加对应log表以及log日志的记录
    if instanceArticle.judgePostTomany(userid) is True:
        if judgeType == 1:
            info = f"userid为{userid}的用户 超出了每天保存草稿次数次数的限制"
            instanceLog.insert_detail(type="保存草稿失败", target=0, credit=0, info=info)
        elif judgeType == 2:
            info = f"userid为{userid}的用户 超出了编辑每天发布文章次数的限制"
            instanceLog.insert_detail(type="发布文章失败", target=0, credit=0, info=info)
        elif judgeType == 3:
            info = f"userid为{userid}的用户 超出了投递文章次数的限制"
            instanceLog.insert_detail(type="投递文章失败", target=0, credit=0, info=info)
        listLogger(userid, info, [3])
        return f"limit-error-{judgeType}"
    # 再判断修改次数
    if instanceLog.whetherLimitModifyArticle(articleid) is True and judgeType == 4:
        info = f"userid为{userid}的用户 超出了每天修改文章次数的限制"
        instanceLog.insert_detail(type="投递", target=0, credit=0, info=info)
        listLogger(userid, info, [3])
        return "modify-limited"
    # 首先为文章生成缩略图，如果没有，就随机生成一张
    url_list = parser_image_url(content)
    if len(url_list) > 0:
        thumbname = generate_thumb(url_list)
    else:
        # 如果文章中没有图片，那么就根据文章类型指定一个
        thumbname = "%d.jpg" % (int(type))
    if judgeType != 4:  # 直接进行插入数据库操作
        try:
            id = instanceArticle.insert_article(type=type, headline=headline, content=content, credit=credit,
                                                drafted=drafted, checked=checked, thumbnail=thumbname)
            # 编辑发布文章成功的情况下 给积分
            if judgeType == 2:
                info = f"userid为{userid}的编辑 发布文章的articleid为{id}的需要消耗{credit}的文章，并且奖励{postArticleCredit}积分"
                # 这里奖励积分
                instanceCredit.insert_detail(type="发布文章", credit=postArticleCredit, target=id, info=info)
                # 这里保存log
                listLogger(userid, info, [3, 5])
            # 普通用户保存草稿
            elif judgeType == 1:
                info = f"userid为{userid}的普通用户 保存文章的articleid为{id}的需要消耗{credit}的文章"
                instanceLog.insert_detail(type="保存草稿", credit=0, target=id, info=info)
                listLogger(userid, info, [3])
            elif judgeType == 3:
                info = f"userid为{userid}的普通用户 投递文章的articleid为{id}的需要消耗{credit}的文章"
                # 这里奖励积分
                instanceCredit.insert_detail(type="投递文章", credit=postArticleCredit, target=id, info=info)
                # 这里保存log
                listLogger(userid, info, [3, 5])
            return str(id)
        except:
            e = traceback.format_exc()
            allLogger(0, e)
            return "post-fail"
    else:
        # 如果是已经添加过的文章，只做修改操作
        try:
            id = instanceArticle.update_article(articleid=articleid, type=type, headline=headline,
                                                content=content,
                                                credit=credit, thumbnail=thumbname, drafted=drafted,
                                                checked=checked)
            info = f"userid为{userid}的用户 修改了文章的articleid为{id}的需要消耗{credit}的文章"
            instanceLog.insert_detail(type="修改文章", credit=0, target=id, info=info)
            listLogger(userid, info, [3])
            return str(id)
        except:
            e = traceback.format_exc()
            allLogger(0, e)
            return "post-fail"


@article.route("/modifyArticle/<int:articleid>", methods=["GET"])
@logDanger
def modifyArticle(articleid):
    result = instanceArticle.searchHeadlineAndContentByArticleid(articleid)
    return result


# 用来接收当前文章的id(修改文章时用的)
@article.route('/centerVar', methods=['GET', 'POST'])  # 在路由中设置允许GET和POST两种方法可以访问
@logDanger
def centerVar():
    if request.method == 'GET':
        return str(session.get("articleidModify"))
    if request.method == 'POST':
        session["articleidModify"] = str(request.form.get("articleid"))
        return "1"
