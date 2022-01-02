from flask import session
from sqlalchemy import Table
import time
from common.connect_db import connect_db

dbsession, md, DBase = connect_db()


class Credit(DBase):
    __table__ = Table("credit", md, autoload=True)

    # 插入积分明细表
    def insert_detail(self, type, target, credit):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        credit = Credit(userid=session.get("userid"), category=type, target=target, credit=credit, createtime=now,
                        updatetime=now)
        dbsession.add(credit)
        dbsession.commit()

    # 判断用户是否已经消耗积分
    def check_paid_article(self, articleid):
        result = dbsession.query(Credit).filter_by(userid=session.get("userid"), target=articleid).all()
        if len(result) > 0:
            return True
        else:
            return False

    # 每天登录只加一分
    def check_limit_login_per_day(self):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(Credit).filter(Credit.userid == session.get("userid"),
                                          Credit.createtime.between(start, end)).all()
        if len(result) > 0:
            return True
        else:
            return False
