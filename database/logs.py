import time

from flask import session, request
from sqlalchemy import Table

from common.connectDb import connectDb

dbsession, md, DBase = connectDb()


class Log(DBase):
    __table__ = Table("log", md, autoload=True)

    # 插入log表
    def insertDetail(self, type, target, credit, userid=None, info=None):
        if userid is None:
            userid = session.get("userid")
        if info is not None:
            info = info + f" The ip address is{request.remote_addr}"
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        logP = Log(userid=userid, category=type, target=target, credit=credit, createtime=now,
                   ipaddr=request.remote_addr, info=info)
        dbsession.add(logP)
        dbsession.commit()

    # Determine if the comment has been approved or disapproved
    # For return 1 Against return 2 Disagree not oppose return 0
    def whetherAgreeOrDisInThisComment(self, commentid):
        row = dbsession.query(Log.category).filter(Log.target == commentid).filter(
            Log.category != "Add a comment").filter(
            Log.userid == session.get("userid")).order_by(Log.createtime.desc()).first()
        if row is None:
            return 0
        else:
            info = row[0]
            if info == "Agree with the comments":
                return 1
            elif info == "Opposing Comments":
                return -1
            else:
                return 0
        pass

    # View all records for a particular user
    def searchAllLogOfUser(self, userid):
        allLogOfUser = dbsession.query(Log).filter_by(userid=userid).all()
        return allLogOfUser

    # View user login, logout, registration, and password retrieval records
    def searchLoginLog(self, userid):
        result = dbsession.query(Log.category, Log.createtime).filter(Log.userid == userid, Log.category.in_(
            ["每日登录", "登录成功", "登出账户", "重设密码"])).all()
        return result
