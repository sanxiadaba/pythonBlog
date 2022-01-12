"""
文件说明：

本文件主要完成对收藏与取消收藏文章
主要操作数据库中的favorite文件


encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""


import traceback

from flask import Blueprint, request, session

from common.myLog import listLogger,logDanger,allLogger
from database.favorite import Favorite
from database.instanceDatabase import instanceFavorite, instanceArticle, instanceUser, instanceLog

favorite = Blueprint("favorite", __name__)

# 收藏文章的函数
@favorite.route("/favorite", methods=["POST"])
@logDanger
def add_favorite():
    articleid = request.form.get("articleid")
    userid=session.get("userid")
    nickname = session.get("nickname")
    authorid = int(instanceArticle.searchUseridByArticleid(articleid)[0])
    authorNickname=instanceUser.searchNicknameByUserid(authorid)[0]
    try:
        info=f"userid为{userid},昵称为{nickname}的用户,将用户id为{authorid}，昵称为{authorNickname}，articleid为{articleid}的文章取消了收藏"
        instanceFavorite.insert_favorite(articleid)
        # 打印日志
        listLogger(userid,info,[4])
        listLogger(authorid,info,[6])
        # 添加日志表
        instanceLog.insert_detail(userid=userid,type="添加收藏",credit=0,target=articleid)
        instanceLog.insert_detail(userid=userid,type="文章被收藏",credit=0,target=articleid)
        return "favorite-pass"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "favorite-fail"


# 取消收藏文章的操作 注意这里是delete请求
@favorite.route("/favorite/<int:articleid>", methods=["DELETE"])
@logDanger
def cancel_favorite(articleid):
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorid = int(instanceArticle.searchUseridByArticleid(articleid)[0])
    authorNickname = instanceUser.searchNicknameByUserid(authorid)[0]
    try:
        instanceFavorite.cancel_favorite(articleid)
        info = f"userid为{userid},昵称为{nickname}的用户,将用户id为{authorid}，昵称为{authorNickname}，articleid为{articleid}的文章取消了收藏"
        instanceFavorite.insert_favorite(articleid)
        # 打印日志
        listLogger(userid, info, [4])
        listLogger(authorid, info, [6])
        # 添加日志表
        instanceLog.insert_detail(userid=userid, type="取消收藏", credit=0, target=articleid)
        instanceLog.insert_detail(userid=userid, type="文章被取消收藏", credit=0, target=articleid)
        return "cancel-pass"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "cancel-fail"
