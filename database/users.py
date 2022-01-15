import random
import time

from flask import session
from sqlalchemy import Table

from common.connect_db import connect_db
from common.myLog import dirInDir, rootDir
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
        avatarPath = rootDir + "\\static\\img\\avatar"
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        nickname = username.split("@")[0]  # 默认账号前缀作为昵称
        avatar = "default/" + str(random.randint(1, thumbNailNum))  # 从十张随机图片中选一张作为初始默认头像
        user = Users(username=username, password=password, role="user", credit=0, nickname=nickname,
                     avatar=avatar + ".png", createtime=now)
        dirInDir(f"myPic_{user.userid}", avatarPath)
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

    # 根据userid查询注册邮箱
    def searchMyEmail(self, userid):
        return dbsession.query(Users.username).filter_by(userid=userid).first()[0]

    # 根据userid查询我QQ
    def searchMyQQ(self, userid):
        return dbsession.query(Users.qq).filter_by(userid=userid).first()[0]

    # 根据userid查询我的头像
    def searchMyAvatar(self, userid):
        return dbsession.query(Users.avatar).filter_by(userid=userid).first()[0]

    # 修改密码
    def modifyUserPassword(self, userid, newPassword):
        newPassword = genearteMD5(newPassword)
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.password = newPassword
        dbsession.commit()

    # 修改昵称
    def modifyUserNickname(self, nickname):
        userid = session.get("userid")
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.nickname = nickname
        dbsession.commit()

    # 修改头像
    def modifyUserThumbnail(self, thumbnail):
        userid = session.get("userid")
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.nickname = thumbnail
        dbsession.commit()

    # 修改qq号
    def modifyUserQQnum(self, newQQ):
        userid = session.get("userid")
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.nickname = newQQ
        dbsession.commit()

    # 申请成为编辑
    def applyForBecomeEditor(self):
        userid = session.get("userid")
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.apply = 1
        dbsession.commit()

    # 查看所有成员信息（用户数量、身份、qq等）
    def searchAllUserInfo(self):
        result = dbsession.query(Users).all()
        return result

    # 更改身份（可以将用户改为编辑，也可以将编辑改为用户）
    # changeType 0表示将编辑改为用户，1表示将用户改为编辑
    def changeIdentity(self, userid, changeType):
        row = dbsession.query(Users).filter_by(userid=userid).first()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        if changeType == 1:
            row.apply = 0
            row.role = "user"
        else:
            row.role = "editor"
        row.updatetime = now
        dbsession.commit()

    # 查看成为编辑的申请
    def searchApllyForEditor(self):
        allApplyForEditor = dbsession.query(Users).filter_by(apply=0).all()
        return allApplyForEditor

    # 修改积分
    def modifyCredit(self, userid, newCredit):
        row = dbsession.query(Users).filter_by(userid=userid)
        row.credit = int(newCredit)
        dbsession.commit()

    # 移除用户（将用户不可登录）
    def forbidUserLogin(self, userid):
        row = dbsession.query(Users).filter_by(userid=userid)
        row.forbidLogin = 1
        dbsession.commit()
