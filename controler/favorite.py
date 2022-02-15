"""
File description.

This file mainly completes the collection and uncollection of articles
Mainly manipulate the favorite file in the database


encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

import traceback

from flask import Blueprint, request, session

from common.myLog import listLogger, logDanger, allLogger
from database.article import Article
from database.favorite import Favorite
from database.logs import Log
from database.users import Users

instanceArticle = Article()
instanceFavorite = Favorite()
instanceLog = Log()
instanceUser = Users()

favorite = Blueprint("favorite", __name__)


# 收藏文章的函数
@favorite.route("/favorite", methods=["POST"])
@logDanger
def add_favorite():
    articleid = request.form.get("articleid")
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorid = int(instanceArticle.searchUseridByArticleid(articleid))
    authorNickname = instanceUser.searchNicknameByUserid(authorid)
    try:
        info = f"The user with userid {userid} and nickname {nickname} has unfavored the articles with userid {authorid}, nickname {authorNickname} and articleid {articleid}."
        instanceFavorite.insertFavorite(articleid)
        # Print Log
        listLogger(userid, info, [4])
        listLogger(authorid, info, [6])
        # Add log table
        instanceLog.insertDetail(userid=userid, type="Add Favorite", credit=0, target=articleid)
        instanceLog.insertDetail(userid=userid, type="Articles Bookmarked", credit=0, target=articleid)
        return "favorite-pass"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "favorite-fail"


# Cancel the operation of favorite articles Note that here is the delete request
@favorite.route("/favorite/<int:articleid>", methods=["DELETE"])
@logDanger
def cancel_favorite(articleid):
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorid = int(instanceArticle.searchUseridByArticleid(articleid))
    authorNickname = instanceUser.searchNicknameByUserid(authorid)
    try:
        instanceFavorite.cancelFavorite(articleid)
        info = f"The user with userid {userid} and nickname {nickname} has unfavored the articles with userid {authorid}, nickname {authorNickname} and articleid {articleid}."
        instanceFavorite.insertFavorite(articleid)
        # Print Log
        listLogger(userid, info, [4])
        listLogger(authorid, info, [6])
        # Add log table
        instanceLog.insertDetail(userid=userid, type="Cancel Favorites", credit=0, target=articleid)
        instanceLog.insertDetail(userid=userid, type="Articles are unfavored", credit=0, target=articleid)
        return "cancel-pass"
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return "cancel-fail"
