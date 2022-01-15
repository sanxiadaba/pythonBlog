import time

from flask import session
from sqlalchemy import Table

from common.connect_db import connect_db

dbsession, md, DBase = connect_db()


class Favorite(DBase):
    __table__ = Table("favorite", md, autoload=True)

    # 新增一条收藏数据
    def insert_favorite(self, articleid):
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get("userid")).first()
        if row is not None:
            row.canceled = 0
        else:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            favorite = Favorite(articleid=articleid, userid=session.get("userid"), canceled=0, createtime=now)
            dbsession.add(favorite)
        dbsession.commit()

    # 取消收藏文章
    def cancel_favorite(self, articleid):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get("userid")).first()
        row.canceled = 1
        row.updatetime = now
        dbsession.commit()

    # 恢复收藏
    def replyFavorite(self, articleid):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get("userid")).first()
        row.canceled = 0
        row.updatetime = now
        dbsession.commit()

    # 判断是否已经已经被收藏
    def check_favorite(self, articleid):
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get("userid")).first()
        if row is None:
            return False
        elif row.canceled == 1:
            return False
        else:
            return True

    # 已收藏、已取消收藏
    def searchAllFavorite(self):
        userid = session.get("userid")
        AllFavorite = dbsession.query(Favorite).filter_by(userid=userid).all()
        return AllFavorite

    # 收藏文章的数量
    def numOfMyFavoriteArticle(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        numOfMyFavoriteArticle = dbsession.query(Favorite).filter_by(userid=userid).count()
        return numOfMyFavoriteArticle
