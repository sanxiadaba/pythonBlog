"""
encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/13
@gituhb: sanxiadaba/pythonBlog
"""
import time

from flask import session, request
from sqlalchemy import Table
from common.connect_db import connect_db
from constant import maxUserPostArticleNum, maxUserPostArticleNumOfEditor, maxModifyArticleNum

dbsession, md, DBase = connect_db()


class ArticleLog(DBase):
    __table__ = Table("articleLog", md, autoload=True)

    def insert_detail(self, articleid, type, info=None):
        info = None if info is None else info
        userid = session.get("userid")
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        ArticleLogP = ArticleLog(userid=userid, articleid=articleid, createtime=now,
                                 ipaddr=request.remote_addr, info=info, type=type)

        dbsession.add(ArticleLogP)
        dbsession.commit()

    # 判断用户上传次数是否超过当日限制
    def checkLimitUpload(self):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(ArticleLog).filter(ArticleLog.userid == session.get("userid"),
                                                    ArticleLog.createtime.between(start, end),
                                                    ArticleLog.type != "修改文章", ArticleLog.type != "修改失败").count()
        role = session.get("role")
        if (result >= maxUserPostArticleNum and role == "user") or (
                result >= maxUserPostArticleNumOfEditor and role == "editor"):
            return True
        else:
            return False

    # 判断用户修改次数是否超过当日限制
    def checkLimitModify(self):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(ArticleLog).filter(ArticleLog.userid == session.get("userid"),
                                                    ArticleLog.createtime.between(start, end),
                                                    ArticleLog.type == "修改文章").count()
        if result>=maxModifyArticleNum:
            return True
        else:
            return False