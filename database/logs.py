import time

from flask import session, request
from sqlalchemy import Table

from common.connect_db import connect_db

dbsession, md, DBase = connect_db()


class Log(DBase):
    __table__ = Table("log", md, autoload=True)

    # 插入log表
    def insert_detail(self, type, target, credit, userid=None, info=None):
        if userid is None:
            userid = session.get("userid")
        if info is not None:
            info = info + f" ip地址为{request.remote_addr}"
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        logP = Log(userid=userid, category=type, target=target, credit=credit, createtime=now,
                   ipaddr=request.remote_addr, info=info)
        dbsession.add(logP)
        dbsession.commit()

    # 判断是否已赞成或反对该评论
    # 赞成返回1 反对返回2 不赞同不反对返回0
    def whetherAgreeOrDisInThisComment(self, commentid):
        row = dbsession.query(Log.category).filter(Log.target == commentid).filter(Log.category != "添加评论").filter(
            Log.userid == session.get("userid")).order_by(Log.createtime.desc()).first()
        if row is None:
            return 0
        else:
            info = row[0]
            if info == "赞同评论":
                return 1
            elif info == "反对评论":
                return -1
            else:
                return 0
        pass

    # 查看某一个用户的所有记录
    def searchAllLogOfUser(self, userid):
        allLogOfUser = dbsession.query(Log).filter_by(userid=userid).all()
        return allLogOfUser
