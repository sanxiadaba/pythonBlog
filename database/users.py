import random
import time

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
        avatar = str(random.randint(1, 15))  # 从十五张随机图片中选一张
        user = Users(username=username, password=password, role="user", credit=50, nickname=nickname,
                     avatar=avatar + ".png", createtime=now, updatetime=now)
        dbsession.add(user)
        dbsession.commit()
        return user

    # 修改用户剩余积分
    def update_credit(self, credit):
        user = dbsession.query(Users).filter_by(userid=session.get("userid")).one()
        user.credit = int(user.credit) + credit
        dbsession.commit()
