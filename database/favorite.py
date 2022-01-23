import time

from flask import session
from sqlalchemy import Table
from database.article import Article
instanceArticle=Article()
from common.connect_db import connect_db

dbsession, md, DBase = connect_db()


class Favorite(DBase):
    __table__ = Table("favorite", md, autoload=True)

    # 新增一条收藏数据
    def insertFavorite(self, articleid):
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get("userid")).first()
        if row is not None:
            row.canceled = 0
        else:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            favorite = Favorite(articleid=articleid, userid=session.get("userid"), canceled=0, createtime=now)
            dbsession.add(favorite)
        dbsession.commit()

    # 取消收藏文章
    def cancelFavorite(self, articleid):
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
    def checkFavorite(self, articleid):
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

    # 收藏的文章
    def myFavoriteArticle(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        myFavoriteArticle = dbsession.query(Favorite.articleid,Favorite.createtime).filter_by(userid=userid,canceled=0).all()
        result=[]
        for i in myFavoriteArticle:
            lin=[]
            for j in i:
                lin.append(j)
            lin.append(instanceArticle.searchHeadlineByArticleid(i[0]))
            result.append(lin)
        myFavoriteArticle=result
        return myFavoriteArticle,len(myFavoriteArticle)

    # 根据articleid查询哪些收藏了
    def hideFavoByArticleid(self,articleid):
        result=dbsession.query(Favorite).filter_by(articleid=articleid).all()
        for i in result:
            i.canceled=1
        dbsession.commit()
