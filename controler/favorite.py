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

from common.auth import login_required
from common.myLog import allLogger, listLogger, logDanger
from database.article import Article
from database.favorite import Favorite
from database.logs import Log
from database.users import Users
from extensions import limiter

instanceArticle = Article()
instanceFavorite = Favorite()
instanceLog = Log()
instanceUser = Users()

favorite = Blueprint("favorite", __name__)


@favorite.before_request
@login_required
def require_login():
    """Favorites always belong to the authenticated user."""


# 收藏文章的函数
@favorite.route("/favorite", methods=["POST"])
@limiter.limit("60 per hour")
@logDanger
def add_favorite():
    articleid = request.form.get("articleid")
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorid = int(instanceArticle.searchUseridByArticleid(articleid))
    authorNickname = instanceUser.searchNicknameByUserid(authorid)
    try:
        info = f"The user with userid {userid} and nickname {nickname} has favorited the article with userid {authorid}, nickname {authorNickname} and articleid {articleid}."
        instanceFavorite.insertFavorite(articleid)
        # Print Log
        listLogger(userid, info, [4])
        listLogger(authorid, info, [6])
        # Add log table: the actor's own record, then the author's notification
        instanceLog.insertDetail(userid=userid, type="Add Favorite", credit=0, target=articleid, info=info)
        instanceLog.insertDetail(userid=authorid, type="Articles Bookmarked", credit=0, target=articleid, info=info)
        return "favorite-pass"
    except Exception:
        e = traceback.format_exc()
        allLogger(0, e)
        return "favorite-fail"


# Cancel the operation of favorite articles Note that here is the delete request
@favorite.route("/favorite/<int:articleid>", methods=["DELETE"])
@limiter.limit("60 per hour")
@logDanger
def cancel_favorite(articleid):
    userid = session.get("userid")
    nickname = session.get("nickname")
    authorid = int(instanceArticle.searchUseridByArticleid(articleid))
    authorNickname = instanceUser.searchNicknameByUserid(authorid)
    try:
        if not instanceFavorite.cancelFavorite(articleid):
            return "cancel-fail"
        info = f"The user with userid {userid} and nickname {nickname} has unfavored the articles with userid {authorid}, nickname {authorNickname} and articleid {articleid}."
        # Print Log
        listLogger(userid, info, [4])
        listLogger(authorid, info, [6])
        # Add log table
        instanceLog.insertDetail(userid=userid, type="Cancel Favorites", credit=0, target=articleid)
        instanceLog.insertDetail(userid=userid, type="Articles are unfavored", credit=0, target=articleid)
        return "cancel-pass"
    except Exception:
        e = traceback.format_exc()
        allLogger(0, e)
        return "cancel-fail"
