import math
import time
import traceback

from flask import session, request
from sqlalchemy import Table

from common.connect_db import connect_db
from common.myLog import listLogger, allLogger
from constant import rateCreditForArticle
from database.article import Article
from database.logs import Log
from database.users import Users

instanceArticle = Article()
instanceLog = Log()
instanceUser = Users()

dbsession, md, DBase = connect_db()


class Credit(DBase):
    __table__ = Table("credit", md, autoload=True)

    # Insert credit table data # then insert the same data into the log table
    def insertDetail(self, type, target, credit, userid=None, info=None):
        # userid determines the user directory to write to. If you don't enter a userid, it defaults to the current user.
        userid = session.get("userid") if userid is None else userid
        # 设置时间
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        # View the current visitor's ip interface
        ipaddr = request.remote_addr

        # Insert credit table
        creditP1 = Credit(userid=userid, category=type, target=target, credit=credit, createtime=now,
                          ipaddr=ipaddr, info=info)
        # Insert log table
        instanceLog.insertDetail(userid=userid, type=type, target=target, credit=credit, info=info)

        # If the points are not 0, update the user's points table.
        if credit != 0:
            instanceUser.updateCredit(credit, userid)

        # Start inserting insert log logs (different types correspond to insert different tables, different information)
        try:
            if type == "购买文章":
                # The userid and nickname of the author of the article and the number of points that should be earned
                authorid = int(instanceArticle.searchUseridByArticleid(target)[0])
                authorNickname = instanceUser.searchNicknameByUserid(authorid)[0]
                #  Note that here the credit should be multiplied by -1 to change back
                authorGetCredit = math.ceil(rateCreditForArticle * credit * -1)

                # The purchaser has subtracted the corresponding points above
                # The author of the article gets the corresponding points
                instanceUser.updateCredit(authorGetCredit, authorid)

                # Buyer's Journal
                userPaidInfo = f"The reader with userid {userid} spent {credit} points to read the article with articleid number '{target}' by authorid {authorid} with nickname `{authorNickname}`."
                listLogger(userid, userPaidInfo, [1, 2, 5])
                # Author's log for getting points
                authorInfo = f"The reader with userid {userid} spent {credit} points to read the article with articleid number '{target}' with authorid {authorid} nickname '{authorNickname}', and the author got {authorGetCredit} points. "
                listLogger(authorid, authorInfo, [5, 6])

                # The author also needs access to the credit form
                creditP2 = Credit(userid=authorid, category="Article was purchased", target=target,
                                  credit=authorGetCredit,
                                  createtime=now,
                                  ipaddr=ipaddr, info=authorInfo)

                instanceLog.insertDetail(type="Article was purchased", target=target, credit=authorGetCredit,
                                         info=authorInfo)
                dbsession.add(creditP2)
            elif type == "Read the article":
                # The userid and nickname of the author of the article and the number of points that should be earned
                authorid = int(instanceArticle.searchUseridByArticleid(target)[0])
                authorNickname = instanceUser.searchNicknameByUserid(authorid)[0]

                # Read people's logs
                userPaidInfo = f"The reader with userid {userid} has read the article with articleid number '{target}' with authorid {authorid} and nickname `{authorNickname}`."
                listLogger(userid, userPaidInfo, [2])
                # 作者获取积分的日志
                authorInfo = f"The reader with userid {userid} has read the article with articleid number '{target}' with authorid {authorid} and nickname `{authorNickname}`. "
                listLogger(authorid, authorInfo, [6])
                instanceLog.insertDetail(type="Articles are read", target=target, credit=0, info=authorInfo)
                # The author also needs access to the credit form
                creditP2 = Credit(userid=authorid, category="Articles are read", target=target, credit=0,
                                  createtime=now,
                                  ipaddr=ipaddr, info=authorInfo)
                dbsession.add(creditP2)

        except:
            e = traceback.format_exc()
            allLogger(0, e)
        finally:
            # Submission Form
            dbsession.add(creditP1)
            dbsession.commit()

    # Determine whether the user has already purchased the article, if already purchased, it will not show again to let them buy
    def whetherPaidForArticle(self, articleid):
        result = dbsession.query(Credit).filter_by(userid=session.get("userid"), target=articleid).all()
        if len(result) > 0:
            return True
        else:
            return False

    # Login every day plus one point
    def whetherFirstLoginThisDay(self, userid):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(Credit).filter(Credit.userid == userid,
                                                Credit.createtime.between(start, end)).count()
        if result == 0:
            return True
        else:
            return False

    # Points breakdown
    # Back to point-related changes
    def creditChangeLog(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        allCreditChangeLog = dbsession.query(Credit.category, Credit.credit, Credit.target).filter_by(
            userid=userid).all()
        result = []
        for i in allCreditChangeLog:
            lin = []
            for j in i:
                lin.append(j)
            if i[2] != 0:
                # If the article is not hidden
                lin.append(instanceArticle.searchHeadlineByArticleid(i[2]))
            else:
                lin.append(" ")
            # Then determine if the article has been hidden
            if instanceArticle.searchWhetherHide(i[2]) is False:
                lin.append("0")
            else:
                lin.append("1")
            result.append(lin)
        allCreditChangeLog = result
        return allCreditChangeLog
