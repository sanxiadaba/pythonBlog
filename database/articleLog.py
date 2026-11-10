"""
encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/13
@gituhb: sanxiadaba/pythonBlog
"""
from datetime import datetime, timedelta

from flask import request, session

from common.connectDb import connectDb
from constant import maxModifyArticleNum, maxUserPostArticleNum, maxUserPostArticleNumOfEditor

dbsession, md, DBase = connectDb()

# Every log type that represents editing an existing article rather than posting one.
MODIFY_TYPES = {"Modify article", "Revision Draft", "Modification failure"}


class ArticleLog(DBase):
    __table__ = md.tables["articleLog"]

    def insertDetail(self, articleid, type, info=None):
        info = None if info is None else info
        userid = session.get("userid")
        now = datetime.now()
        ArticleLogP = ArticleLog(userid=userid, articleid=articleid, createtime=now,
                                 ipaddr=request.remote_addr, info=info, type=type)

        dbsession.add(ArticleLogP)
        dbsession.commit()

    # Determine if the number of user uploads exceeds the daily limit
    def checkLimitUpload(self):
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        result = dbsession.query(ArticleLog).filter(ArticleLog.userid == session.get("userid"),
                                                    ArticleLog.createtime.between(start, end),
                                                    ArticleLog.type.notin_(MODIFY_TYPES)).count()
        role = session.get("role")
        if (result >= maxUserPostArticleNum and role == "user") or (
                result >= maxUserPostArticleNumOfEditor and role == "editor"):
            return True
        else:
            return False

    # Determine if the number of user modifications exceeds the daily limit
    def checkLimitModify(self):
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        result = dbsession.query(ArticleLog).filter(ArticleLog.userid == session.get("userid"),
                                                    ArticleLog.createtime.between(start, end),
                                                    ArticleLog.type.in_(MODIFY_TYPES)).count()
        if result >= maxModifyArticleNum:
            return True
        else:
            return False
