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


from flask import Blueprint, session, jsonify, render_template

from database.instanceDatabase import instanceArticle,instanceFavorite,instanceComment,instanceUser,instanceCredit

userManage = Blueprint("userManage", __name__)


@userManage.route("/userManage", methods=["GET"])
def baseManage():
    userid=session.get("userid")
    # 我的已发布文章的个数
    numOfAllMyArticle=instanceArticle.get_total_count()
    # 已发布文章的访问量
    allNumOfAllArticleRead=instanceArticle.allNumOfAllArticleRead()
    # 我收藏文章的数量
    numOfMyFavoriteArticle=instanceFavorite.numOfMyFavoriteArticle()
    # 我评论的个数
    numOfALLMyComment=instanceComment.numOfALLMyComment()
    # 我的昵称
    myNickname=instanceUser.searchNicknameByUserid(userid)[0]
    # 我的注册邮箱
    myEmail=instanceUser.searchMyEmail(userid)
    # 用户角色
    myRole=session.get("role")
    # 我的qq
    myQQ=instanceUser.searchMyQQ(userid)
    # 总共剩余积分
    restOfMyCredit=instanceUser.findRestCredit()
    # 我的头像
    myAvatar=instanceUser.searchMyAvatar(userid)

    MyInfo={}
    MyInfo["numOfAllMyArticle"]=numOfAllMyArticle
    MyInfo["allNumOfAllArticleRead"]=allNumOfAllArticleRead
    MyInfo["numOfMyFavoriteArticle"]=numOfMyFavoriteArticle
    MyInfo["numOfALLMyComment"]=numOfALLMyComment
    MyInfo["myNickname"]=myNickname
    MyInfo["myEmail"]=myEmail
    MyInfo["myRole"]=myRole
    MyInfo["myQQ"]=myQQ
    MyInfo["restOfMyCredit"]=restOfMyCredit
    MyInfo["myAvatar"]=myAvatar

    return render_template("userManage.html", myInfo=MyInfo)




#  返回我的资料
# 文章数、评论数、浏览总数、总积分、我的昵称、我的头像、我的qq号、我的角色
@userManage.route("/userInfo", methods=["GET"])
def userInfo():
    last, most, recommended = instanceArticle.find_last_most_recommended()
    return jsonify(last, most, recommended)

# 修改昵称

# 修改头像

# 修改qq号

# 申请角色

# 修改密码

# 我的评论 #评论点赞数 #评论反对数

# 删除评论（注意到时候设置文章评论数要减去1）

# 我的文章

# 文章评论数

# 文章浏览数

# 修改文章标题

# 修改文章内容

# 修改文章缩略图

# 已收藏、已取消收藏

# 取消收藏

# 回复收藏

# 登录记录

# 积分明细

# 如何获取积分
