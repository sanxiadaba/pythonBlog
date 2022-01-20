"""
文件说明：

本文件用来存放对article操作的一些函数
比如查看全文、发布文章、修改文章等
主要操作数据库中的article表

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
    maxUserPostArticleNumOfEditor, maxModifyArticleNum
from database.instanceDatabase import instanceUser, instanceArticle, instanceComment, instanceLog, instanceFavorite, \
    instanceCredit, instanceUpload, instanceArticleLog

article = Blueprint("article", __name__)


# 加载文章 访问article下不同articleid的文章
@article.route("/article/<int:articleid>")
@logDanger
def read(articleid):
    # 查询剩余的积分
    restOfCredit = instanceUser.findRestCredit()
    # 查询文章，找不到文章的话抛出404错误，发生其他错误的话抛出500错误
    # 随后错误页面会重定向到首页
    try:
        result = instanceArticle.find_by_id(articleid)
        if result is None:
            abort(404)
    except:
        abort(500)

    # dic字典用来存放要返回的数据
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
    # 该文章有几页评论
    total = math.ceil(count / howCommentInArticle)
    # 判断每个作者对每个评论的状态，方便前端加载对应的页面
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
    # 这里判断积分是否足够的判断已经在前端做过了
    articleid = request.form.get("articleid")
    result = instanceArticle.find_by_id(articleid)
    userid = session.get("userid")
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
    whetherHide = False
    #  上一个跳转的页面,如果不是从文章哪里跳转的，都不会填充
    fromUrl = str(request.referrer)
    # 查看是从哪个地方跳转来的，如果是从修改文章处跳转的话会将上一次的内容填充进去以供修改
    s1 = fromUrl
    if s1.split("/")[-1] == "userManage":
        session["controlBiaoNum"] = 1
    judge = True if ((s1.split("/")[-1].isdigit() is True and s1.split("/")[-2] == "article") or s1.split("/")[
        -1] == "userManage") else False
    # 填充修改页面的值 当然到底填充空还是对应的文章需要用articleJudge这个参数来判断
    articleidModify = session.get("articleidModify")
    if articleidModify == "0" or articleidModify is None or judge is False:
        session["articleidModify"] = "0"
        articleContent = ""
    else:
        whetherHide = instanceArticle.searchWhetherHide(articleidModify)
        articleContent = instanceArticle.searchHeadlineAndContentByArticleid(articleidModify)["content"]
    return render_template("write.html", maxUserPostArticleNum=maxUserPostArticleNum, articleContent=articleContent,
                           maxUserPostArticleNumOfEditor=maxUserPostArticleNumOfEditor,
                           maxModifyArticleNum=maxModifyArticleNum, whetherHide=whetherHide)


# 发布文章的按钮
@article.route("/article", methods=["POST"])
@logDanger
def addArticle():
    headline = request.form.get("headline")
    content = request.form.get("content")
    # 文章的标题不能小于五且内容不小于100
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
    # 用来判断前端执行的是什么操作  #1.保存草稿 2.发布文章 3.投递文章 4.修改文章
    judgeType = int(request.form.get("judgeType"))
    info = ""

    # 再判断今天是否超出了投稿的限制(判断的是1、2、3不判断修改次数)
    # 添加对应log表以及log日志的记录
    if instanceArticleLog.checkLimitUpload() is True and judgeType in range(1, 4):
        if judgeType == 1:
            info = f"userid为{userid}的用户 超出了每天保存草稿次数次数的限制"
            type = "保存草稿失败"
        elif judgeType == 2:
            type = "发布文章失败"
            info = f"userid为{userid}的用户 超出了编辑每天发布文章次数的限制"
        elif judgeType == 3:
            type = "投递文章失败"
            info = f"userid为{userid}的用户 超出了投递文章次数的限制"
        instanceLog.insert_detail(type=type, target=0, credit=0, info=info)
        listLogger(userid, info, [3])
        instanceArticleLog.insert_detail(articleid=articleid, type=type, info=info)
        return f"limit-error-{judgeType}"
    # 再判断修改次数
    if instanceArticleLog.checkLimitModify() is True and judgeType == 4:
        info = f"userid为{userid}的用户 超出了每天修改文章次数的限制"
        type = "修改失败"
        instanceLog.insert_detail(type=type, target=0, credit=0, info=info)
        listLogger(userid, info, [3])
        instanceArticleLog.insert_detail(articleid=articleid, type=type, info=info)
        return "modify-limited"
    # 文章生成缩略图，如果没有，就随机生成一张
    url_list = parser_image_url(content)
    # 如果文章中有图片，那就根据一定规则生成该文章的缩略图，否则就为其分配一个对应序号的缩略图
    if len(url_list) > 0:
        thumbname = generate_thumb(url_list, userid)
        instanceUpload.insert_detail(imgname=thumbname, info="上传缩略图")
    else:
        # 如果文章中没有图片，那么就根据文章类型指定一个
        thumbname = "default/" + "%d.jpg" % (int(type))
    if judgeType != 4:  # 直接进行插入数据库操作
        try:
            # 返回新插入文章的id
            id = instanceArticle.insert_article(type=typeArticle, headline=headline, content=content, credit=credit,
                                                drafted=drafted, checked=checked, thumbnail=thumbname)
            # 编辑发布文章成功的情况下 给积分
            if judgeType == 2:
                info = f"userid为{userid}的编辑 发布文章的articleid为{id}的需要消耗{credit}的文章，并且奖励{postArticleCredit}积分"
                type = "发布文章"
                # 这里奖励积分
                instanceCredit.insert_detail(type=type, credit=postArticleCredit, target=id, info=info)
                # 这里保存log
                listLogger(userid, info, [3, 5])

            # 普通用户保存草稿
            elif judgeType == 1:
                type = "保存草稿"
                info = f"userid为{userid}的普通用户 保存文章的articleid为{id}的需要消耗{credit}的文章"
                instanceLog.insert_detail(type=type, credit=0, target=id, info=info)
                listLogger(userid, info, [3])
            elif judgeType == 3:
                type = "投递文章"
                info = f"userid为{userid}的普通用户 投递文章的articleid为{id}的需要消耗{credit}的文章"
                # 这里奖励积分
                instanceCredit.insert_detail(type=type, credit=postArticleCredit, target=id, info=info)
                # 这里保存log
                listLogger(userid, info, [3, 5])
            instanceArticleLog.insert_detail(articleid=id, type=type, info=info)
            return str(id)
        except:
            e = traceback.format_exc()
            allLogger(0, e)
            return "post-fail"
    else:
        # 如果是已经添加过的文章，只做修改操作
        try:
            whetherDrafted = instanceArticle.searchWhetherDrafted(articleid)
            if whetherDrafted is True:
                drafted = 1

            id = instanceArticle.update_article(articleid=articleid, type=typeArticle, headline=headline,
                                                content=content,
                                                credit=credit, thumbnail=thumbname, drafted=drafted,
                                                checked=checked)
            if whetherDrafted is False:
                type = "修改文章"
                info = f"userid为{userid}的用户 修改了文章的articleid为{id}的需要消耗{credit}的文章"
                instanceLog.insert_detail(type="修改文章", credit=0, target=id, info=info)
                instanceArticleLog.insert_detail(articleid=articleid, type=type, info=info)
                listLogger(userid, info, [3])
                return str(id)
            else:
                type = "修改草稿"
                info = f"userid为{userid}的用户 修改了文章的articleid为{id}的需要消耗{credit}的草稿"
                instanceLog.insert_detail(type="修改草稿", credit=0, target=id, info=info)
                instanceArticleLog.insert_detail(articleid=articleid, type=type, info=info)
                listLogger(userid, info, [3])
                return "xiu"
        except:
            e = traceback.format_exc()
            allLogger(0, e)
            return "post-fail"


# 修改文章的时候访问的端口
@article.route("/modifyArticle/<int:articleid>", methods=["GET"])
@logDanger
def modifyArticle(articleid):
    result = instanceArticle.searchHeadlineAndContentByArticleid(articleid)
    return result


# 用来接收当前文章的id(修改文章时用的)
# 这里主要还是为了修改文章而服务的
@article.route('/centerVar', methods=['GET', 'POST'])  # 在路由中设置允许GET和POST两种方法可以访问
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
