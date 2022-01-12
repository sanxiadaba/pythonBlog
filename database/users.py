import random
import time

from flask import session
from sqlalchemy import Table

from common.connect_db import connect_db
from common.utility import genearteMD5
from constant import thumbNailNum

dbsession, md, DBase = connect_db()


class Users(DBase):
    __table__ = Table("users", md, autoload=True)

    # 登录校验，查看账户对应的密码是否正确
    def find_by_username(self, username):
        result = dbsession.query(Users).filter_by(username=username).all()
        return result

    # 根userid返回作者的相关信息
    def find_by_userid(self, userid):
        row = dbsession.query(Users).filter_by(userid=userid).first()
        return row

    # 实现注册，首次注册只需要用户名和密码
    # 通常用户不会填写太多资料，后续可以在用户中心完善
    def do_register(self, username, password):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        nickname = username.split("@")[0]  # 默认账号前缀作为昵称
        avatar = str(random.randint(1, thumbNailNum))  # 从十张随机图片中选一张作为初始默认头像
        user = Users(username=username, password=password, role="user", credit=0, nickname=nickname,
                     avatar=avatar + ".png", createtime=now, updatetime=now)
        dbsession.add(user)
        dbsession.commit()
        return user

    # 修改用户积分
    def update_credit(self, credit, userid):
        user = dbsession.query(Users).filter_by(userid=userid).one()
        user.credit = int(user.credit) + int(credit)
        dbsession.commit()

    # 查看用户剩余的积分
    def findRestCredit(self):
        userid = session.get("userid")
        restOfCredit = dbsession.query(Users.credit).filter_by(userid=userid).first()
        if restOfCredit is None:
            return None
        else:
            return restOfCredit[0]

    # 根据user全名查询对应的id
    def findUseridByUsername(self, username):
        userid = dbsession.query(Users.userid).filter_by(username=username).first()
        if userid is not None:
            return userid[0]
        else:
            return None

    # 根据用户的id查询其昵称
    def searchNicknameByUserid(self, userid):
        return dbsession.query(Users.nickname).filter_by(userid=userid).first()

    # 修改密码
    def modifyUserPassword(self, userid, newPassword):
        newPassword = genearteMD5(newPassword)
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.password = newPassword
        dbsession.commit()

