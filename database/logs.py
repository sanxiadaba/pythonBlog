from flask import session, request
from sqlalchemy import Table
import time
from common.connect_db import connect_db
from database.users import Users


dbsession, md, DBase = connect_db()

class Log(DBase):
    __table__ = Table("log", md, autoload=True)

    # 插入log表
    def insert_detail(self, type, target, credit,userid=None,info=None):
        if userid is None:
            userid=session.get("userid")
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        creditP = Log(userid=userid, category=type, target=target, credit=credit, createtime=now, ipaddr = request.remote_addr,info=info)
        dbsession.add(creditP)
        u=Users()
        u.update_credit(credit,userid)
        dbsession.commit()

    # 判断用户是否已经购买了该积分
    def check_paid_article(self, articleid):
        result = dbsession.query(Log).filter_by(userid=session.get("userid"), target=articleid).all()
        if len(result) > 0:
            return True
        else:
            return False

    # 每天登录加一分
    def check_limit_login_per_day(self,userid):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(Log).filter(Log.userid == userid,
                                             Log.createtime.between(start, end)).count()
        if result == 0:
            return True
        else:
            return False
    # 判断是否已赞成或反对该评论
    # 赞成返回1 反对返回2 不赞同不反对返回0
    def whetherAgreeOrDisInThisComment(self,commentid):
        row= dbsession.query(Log.category).filter(Log.target==commentid).filter(Log.category!="添加评论").filter(Log.userid==session.get("userid")).order_by(Log.createtime.desc()).first()
        if row is None:
            return 0
        else:
            info=row[0]
            if info=="赞同评论":
                return 1
            elif info=="反对评论":
                return -1
            else:
                return 0
        pass



