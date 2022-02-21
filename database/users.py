import random
import time

from flask import session
from sqlalchemy import Table

from common.connectDb import connectDb
from common.myLog import dirInDir, rootDir
from common.utility import genearteMD5
from constant import thumbNailNum

dbsession, md, DBase = connectDb()


class Article(DBase):
    __table__ = Table("article", md, autoload=True)

    def exceptDeleteNum(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        return dbsession.query(Article).filter(Article.userid == userid, Article.delete == 0).count()


class Comment(DBase):
    __table__ = Table("comment", md, autoload=True)

    def numOfComment(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        numOfAll = dbsession.query(Comment).filter_by(userid=userid, hide=0).count()
        return numOfAll


instanceArticle = Article()
instanceComment = Comment()


class Users(DBase):
    __table__ = Table("users", md, autoload=True)

    # Login verification to see if the password corresponding to the account is correct
    def searchUserByUsername(self, username):
        result = dbsession.query(Users).filter_by(username=username).first()
        return result

    # Return information about the author by userid
    def searchUserByUserid(self, userid):
        row = dbsession.query(Users).filter_by(userid=userid).first()
        return row

    # Implement registration, the first registration only need user name and password
    # Usually users do not fill in too much information, and can subsequently improve in the user center
    def doRegister(self, username, password):
        avatarPath = rootDir + "\\static\\img\\avatar"
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        nickname = username.split("@")[0]  # Default account prefix as nickname
        avatar = "default/" + str(
            random.randint(1, thumbNailNum))  # Choose one of the ten random images as the initial default avatar
        user = Users(username=username, password=password, role="user", credit=0, nickname=nickname,
                     avatar=avatar + ".png", createtime=now)
        dirInDir(f"myPic_{user.userid}", avatarPath)
        dbsession.add(user)
        dbsession.commit()
        return user

    # Modify user points
    def updateCredit(self, credit, userid):
        user = dbsession.query(Users).filter_by(userid=userid).one()
        user.credit = int(user.credit) + int(credit)
        dbsession.commit()

    # Check the remaining points of the user
    def findRestCredit(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        restOfCredit = dbsession.query(Users.credit).filter_by(userid=userid).first()
        if restOfCredit is None:
            return None
        else:
            return restOfCredit[0]

    # Query the corresponding id according to the full name of the user
    def findUseridByUsername(self, username):
        userid = dbsession.query(Users.userid).filter_by(username=username).first()
        if userid is not None:
            return userid[0]
        else:
            return None

    # Query username by userid
    def searchUsernameByUserd(self, userid):
        row = dbsession.query(Users.username).filter_by(userid=userid).first()[0]
        return row

    # Query a user's nickname based on his or her id
    def searchNicknameByUserid(self, userid):
        return dbsession.query(Users.nickname).filter_by(userid=userid).first()[0]

    # Search registered mailbox according to userid
    def searchMyEmail(self, userid):
        return dbsession.query(Users.username).filter_by(userid=userid).first()[0]

    # I'm not sure if I'm a good person.
    def searchMyQQ(self, userid):
        row = dbsession.query(Users.qq).filter_by(userid=userid).first()[0]
        if row is None:
            return "None"
        else:
            return row

    # Search my avatar by userid
    def searchMyAvatar(self, userid):
        return dbsession.query(Users.avatar).filter_by(userid=userid).first()[0]

    # Change password
    def modifyUserPassword(self, userid, newPassword):
        newPassword = genearteMD5(newPassword)
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.password = newPassword
        dbsession.commit()

    # Change nickname
    def modifyUserNickname(self, nickname):
        userid = session.get("userid")
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.nickname = nickname
        dbsession.commit()

    # Modify avatar
    def modifyUserThumbnail(self, thumbnail):
        userid = session.get("userid")
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.avatar = thumbnail
        dbsession.commit()

    # Modify qq number
    def modifyUserQQnum(self, newQQ):
        userid = session.get("userid")
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.qq = newQQ
        dbsession.commit()

    # Apply to become an editor
    def applyForBecomeEditor(self):
        userid = session.get("userid")
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.apply = 1
        dbsession.commit()

    # cancle Apply to become an editor
    def cancleApplyForBecomeEditor(self):
        userid = session.get("userid")
        user = dbsession.query(Users).filter_by(userid=userid).first()
        user.apply = 0
        dbsession.commit()

    # View all member information (number of users, identity, qq, etc.)
    def searchAllUserInfo(self):
        result = dbsession.query(Users).all()
        return result

    # change identity (you can change user to editor or editor to user)
    # changeType 0 means change editor to user, 1 means change user to editor
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

    # View the application to become an editor
    def searchApllyForEditor(self):
        allApplyForEditor = dbsession.query(Users).filter_by(apply=0).all()
        return allApplyForEditor

    # Modify Points
    def modifyCredit(self, userid, newCredit):
        row = dbsession.query(Users).filter_by(userid=userid)
        row.credit = int(newCredit)
        dbsession.commit()


    # Check whether to apply to become an editor
    def whetherApplyForEditor(self, userid):
        whetherApplyForEditor = dbsession.query(Users.apply).filter_by(userid=userid).first()[0]
        return whetherApplyForEditor

    # View the number of all people
    def searchAllNumOfUser(self):
        allUserNum = dbsession.query(Users).count()
        return allUserNum

    # view number of admin
    def searchNumOfAdmin(self):
        numOfAdmin = dbsession.query(Users).filter_by(role="admin").count()
        return numOfAdmin

    # view number of editor
    def searchNumOfEditor(self):
        numOfEditor = dbsession.query(Users).filter_by(role="editor").count()
        return numOfEditor

    # view number of user
    def searchNumOfUser(self):
        numOfUser = dbsession.query(Users).filter_by(role="user").count()
        return numOfUser

    # Return all users, editors' information
    def searchInfoOfUserAndEditor(self):
        result = dbsession.query(Users).filter(Users.role != "admin").all()
        infoList = []
        for user in result:
            info = []
            userid = user.userid
            info.extend([user.username, user.nickname, instanceArticle.exceptDeleteNum(userid=userid),
                         instanceComment.numOfComment(userid=userid), user.credit, user.createtime, user.apply,
                         user.userid,
                         user.forbidLogin, user.role])
            infoList.append(info)
        newInfoList = []
        for i in infoList:
            if i[-1] == "admin":
                newInfoList.append(i)
                infoList.remove(i)
        for i in infoList:
            newInfoList.append(i)
        return newInfoList

    # Set the user role of the specified user to Edit
    def becomeEditor(self, userid):
        row = dbsession.query(Users).filter_by(userid=userid).first()
        row.role = "editor"
        dbsession.commit()

    # Set the user role of the specified user to user
    def becomeUser(self, userid):
        row = dbsession.query(Users).filter_by(userid=userid).first()
        row.role = "user"
        dbsession.commit()

    # Disabling a user's login
    def forbidUserLogin(self, userid):
        row = dbsession.query(Users).filter_by(userid=userid).first()
        row.forbidUserLogin = 1
        dbsession.commit()

    # Reply to a user's login
    def restoreLogin(self, userid):
        row = dbsession.query(Users).filter_by(userid=userid).first()
        row.forbidUserLogin = 0
        dbsession.commit()

    # Determine if it is an administrator by id
    def judgeAdminByUserid(self, userid):
        row = dbsession.query(Users.role).filter_by(userid=userid).first()[0]
        return True if row == "admin" else False
