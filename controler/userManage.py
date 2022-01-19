"""
文件说明：

模块正在开发，用户查看自己信息的后台接口

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""
import base64
import os
import time
import traceback
from math import ceil
from flask import Blueprint, session, jsonify, render_template, request
from constant import everyPageInHou
from common.myLog import logDanger, dirInDir, avatarPath, listLogger, allLogger
from common.utility import compress_image
from database.instanceDatabase import instanceArticle, instanceFavorite, instanceComment, instanceUser, instanceLog

userManage = Blueprint("userManage", __name__)


@userManage.route("/userManage", methods=["GET"])
@logDanger
def baseManage():
    userid = session.get("userid")
    # 我的已发布文章的个数
    numOfAllMyArticle = len(instanceArticle.searchAllMyArticle())
    # 已发布文章的访问量
    allNumOfAllArticleRead = instanceArticle.allNumOfAllArticleRead()
    # 我收藏文章的数量
    numOfMyFavoriteArticle = instanceFavorite.numOfMyFavoriteArticle()
    # 我评论的个数
    numOfALLMyComment = instanceComment.numOfALLMyComment()
    # 我的昵称
    myNickname = instanceUser.searchNicknameByUserid(userid)[0]
    # 我的注册邮箱
    myEmail = instanceUser.searchMyEmail(userid)
    # 用户角色
    myRole = session.get("role")
    # 我的qq
    myQQ = instanceUser.searchMyQQ(userid)
    # 总共剩余积分
    restOfMyCredit = instanceUser.findRestCredit()
    # 我的头像
    myAvatar = instanceUser.searchMyAvatar(userid)
    # 是否申请成为编辑
    whetherApplyForEditor = instanceUser.whetherApplyForEditor(userid)

    # 用户后台管理文章的信息
    articleInfo=instanceArticle.articleInfo(userid)

    #  查询我的所有文章的数量（除了已删除）
    myArticleNum=instanceArticle.exceptDeleteNum()

    #  管理页面的文章页面分几页
    howManyPage=ceil(myArticleNum/everyPageInHou)
    howManyPage_1=howManyPage
    howManyPage=list(range(2,howManyPage+1))

    # 判断跳转到哪个页面
    controlBiaoNum=session.get("controlBiaoNum")
    controlBiaoNum =0 if controlBiaoNum is None else int(controlBiaoNum)

    MyInfo = {}
    MyInfo["numOfAllMyArticle"] = numOfAllMyArticle
    MyInfo["allNumOfAllArticleRead"] = allNumOfAllArticleRead
    MyInfo["numOfMyFavoriteArticle"] = numOfMyFavoriteArticle
    MyInfo["numOfALLMyComment"] = numOfALLMyComment
    MyInfo["myNickname"] = myNickname
    MyInfo["myEmail"] = myEmail
    MyInfo["myRole"] = myRole
    MyInfo["myQQ"] = myQQ
    MyInfo["restOfMyCredit"] = restOfMyCredit
    MyInfo["myAvatar"] = myAvatar
    MyInfo["whetherApplyForEditor"] = whetherApplyForEditor
    return render_template("userManage.html", myInfo=MyInfo,articleInfo=articleInfo,everyPageInHou=everyPageInHou,myArticleNum=myArticleNum,howManyPage=howManyPage,howManyPage_1=howManyPage_1,controlBiaoNum=controlBiaoNum)


#  返回我的资料
# 文章数、评论数、浏览总数、总积分、我的昵称、我的头像、我的qq号、我的角色
@userManage.route("/userInfo", methods=["GET"])
@logDanger
def userInfo():
    last, most, recommended = instanceArticle.find_last_most_recommended()
    return jsonify(last, most, recommended)


# 修改昵称
@userManage.route("/modifyNickname", methods=["POST"])
@logDanger
def modifyNickname():
    userid = session.get('userid')
    newNickname = request.form.get("newNickname")
    try:
        instanceUser.modifyUserNickname(newNickname)
        info = f"userid为{userid}的用户修改昵称为{newNickname}"
        listLogger(userid, info, [0])
        instanceLog.insert_detail(type="修改昵称", target=userid, credit=0, info=info)
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# 修改文章缩略图

# 修改qq号
@userManage.route("/modifyQQ", methods=["POST"])
@logDanger
def modifyQQ():
    newQQ = request.form.get("newQQ")
    userid = session.get("userid")
    try:
        instanceUser.modifyUserQQnum(newQQ)
        info = f"userid为{userid}的用户修改qq号为{newQQ}"
        listLogger(userid, info, [0])
        instanceLog.insert_detail(type="修改QQ", target=userid, credit=0, info=info)
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# 申请角色
@userManage.route("/applyEditor", methods=["POST"])
@logDanger
def applyEditor():
    userid = session.get('userid')
    try:
        instanceUser.applyForBecomeEditor()
        info = f"userid为{userid}的用户申请成为编辑"
        listLogger(userid, info, [0])
        instanceLog.insert_detail(type="申请成为编辑", target=userid, credit=0, info=info)
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"


# 修改密码

# 我的评论 #评论点赞数 #评论反对数

# 删除评论（注意到时候设置文章评论数要减去1）
@userManage.route("/hideArticle", methods=["POST"])
@logDanger
def hideArticle():
    userid=session.get("userid")
    articleid = request.form.get('articleid')
    try:
        instanceArticle.deleteArticle(articleid)
        info = f"userid为{userid}的用户删除了articleid为{articleid}的文章"
        listLogger(userid, info, [0])
        instanceLog.insert_detail(type="删除文章", target=userid, credit=0, info=info)
        return "1"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "0"

# 我的文章

# 文章评论数

# 文章浏览数

# 修改文章标题

# 修改文章内容

# 修改头像
@userManage.route("/uploadUserAvatar", methods=["POST", "GET"])
@logDanger
def uploadUserAvatar():
    if request.method == "GET":
        return render_template("uploadUserAvatar.html")


# 对头像图片上传进行响应
@userManage.route('/uploadImg', methods=['POST', 'OPTIONS'])
@logDanger
def upload():
    userid = session.get("userid")
    myAvatarPath = avatarPath + "\\" + f"myPic_{userid}"
    dirInDir(f"myPic_{userid}", avatarPath)
    if request.form.get("action") == "add":
        data = request.form.get("picStr")
        imgdata = base64.b64decode(data)
        thumbname = time.strftime("%Y%m%d_%H%M%S." + "jpg")
        now = thumbname.split(".")
        imgfile = os.path.join(myAvatarPath, "test.jpg")
        file = open(imgfile, 'wb')
        file.write(imgdata)
        file.close()
        oldpicPath = myAvatarPath + "\\" + "test.jpg"
        newPicPath = myAvatarPath + "\\" + thumbname
        compress_image(oldpicPath, newPicPath, 400)
        newPicPath = f"myPic_{userid}" + "/" + thumbname
        instanceUser.modifyUserThumbnail(newPicPath)
        os.remove(oldpicPath)
        allPathPic = [lists for lists in os.listdir(myAvatarPath) if os.path.isfile(os.path.join(myAvatarPath, lists))]
        for i in allPathPic:
            biJiao = i.split(".")
            if biJiao < now:
                os.remove(myAvatarPath + "\\" + i)
        info = f"userid为{userid}的用户，更改自己的头像为{newPicPath}"
        listLogger(userid, info, [0])
        instanceLog.insert_detail(type="更换头像", target=userid, credit=0, info=info)
        return "1"
# 已收藏、已取消收藏

# 取消收藏

# 回复收藏

# 登录记录

# 积分明细

# 如何获取积分

# 控制再次刷新页面时，出现在哪个标签
@userManage.route("/controlBiaoNum",methods=["POST","GET"])
@logDanger
def controlBiaoNum():
    if request.method == 'GET':
        controlBiaoNum = session.get("controlBiaoNum")
        session["controlBiaoNum"]=0
        if controlBiaoNum is not None or controlBiaoNum != "0":
            return str(controlBiaoNum)
        else:
            return "0"
    elif request.method == 'POST':
        session["controlBiaoNum"] = str(request.form.get("controlBiaoNum"))
        return "1"