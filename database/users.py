import random
import time
from  constant import thumbNailNum
from flask import session
from sqlalchemy import Table

from common.connect_db import connect_db

dbsession, md, DBase = connect_db()


class Users(DBase):
    __table__ = Table("users", md, autoload=True)

    # 登录校验
    def find_by_username(self, username):
        result = dbsession.query(Users).filter_by(username=username).all()
        return result

    def find_by_userid(self, userid):
        row = dbsession.query(Users).filter_by(userid=userid).first()
        return row

    # 实现注册，首次注册只需要用户名和密码
    # 通常用户不会填写太多资料，后续可以完善
    def do_register(self, username, password):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        nickname = username.split("@")[0]  # 默认账号前缀作为昵称
        avatar = str(random.randint(1, thumbNailNum))  # 从十张随机图片中选一张作为初始默认头像
        user = Users(username=username, password=password, role="user", credit=0, nickname=nickname,
                     avatar=avatar + ".png", createtime=now, updatetime=now)
        dbsession.add(user)
        dbsession.commit()
        return user

    # 修改用户剩余积分
    def update_credit(self, credit,userid):
        user = dbsession.query(Users).filter_by(userid=userid).one()
        user.credit = int(user.credit) + credit
        dbsession.commit()

    # 查看剩余的积分
    def findRestCredit(self):
        userid=session.get("userid")
        restOfCredit= dbsession.query(Users.credit).filter_by(userid=userid).one()[0]
        return restOfCredit