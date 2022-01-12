import math
import time
import traceback

from flask import session, request
from sqlalchemy import Table

from constant import rateCreditForArticle
from database.article import Article
from database.logs import Log
from common.connect_db import connect_db
from database.users import Users
from common.myLog import listLogger,allLogger

dbsession, md, DBase = connect_db()


class Credit(DBase):
    __table__ = Table("credit", md, autoload=True)

    # 插入credit表数据  # 随后向log表插入相同数据
    def insert_detail(self, type, target, credit, userid=None, info=None):
        # userid确定要写入的用户目录 不输入的userid的话就默认为当前用户
        userid = session.get("userid") if userid is None else userid
        # 设置时间
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        # 查看当前的访问人的ip接口
        ipaddr=request.remote_addr
        # 实例化数据库,方便后续操作 （这里没有从instanceDatabase引入是为了避免循环引用）
        instanceArticle = Article()
        instanceUser = Users()
        instanceLog=Log()
        # 插入credit表
        creditP1 = Credit(userid=userid, category=type, target=target, credit=credit, createtime=now,
                          ipaddr=ipaddr, info=info)
        # 插入log表
        instanceLog.insert_detail(userid=userid,type=type,target=target,credit=credit,info=info)

        # 如果积分不为0 更新用户的积分表
        if credit!=0:
            instanceUser.update_credit(credit, userid)

        # 开始插入插入log日志（不同的type对应插入不同的表，不同的信息）
        try:
            if type=="购买文章":
                # 文章作者的userid 和nickname 以及应该获取的积分
                authorid=int(instanceArticle.searchUseridByArticleid(target)[0])
                authorNickname=instanceUser.searchNicknameByUserid(authorid)[0]
                authorGetCredit=math.ceil(rateCreditForArticle * credit)

                # 购买者在上面已经减去对应积分
                # 文章作者获取对应的积分
                instanceUser.update_credit(authorGetCredit, authorid)

                # 购买人的日志
                userPaidInfo=f"用户userid为{userid}的读者 花费{credit}积分，阅读了作者id为{authorid}昵称为`{authorNickname}`的articleid号为‘{target}’文章"
                listLogger(userid,userPaidInfo,[1,2,5])
                # 作者获取积分的日志
                authorInfo=f"用户userid为{userid}的读者 花费{credit}积分，阅读了作者id为{authorid}昵称为`{authorNickname}`的articleid号为‘{target}’文章,作者获取了{authorGetCredit}积分 "
                listLogger(authorid,authorInfo,[5,6])

                # 作者也需要进入credit表
                creditP2 = Credit(userid=authorid, category="文章被购买", target=target, credit=authorGetCredit, createtime=now,
                                  ipaddr=ipaddr, info=authorInfo)

                instanceLog.insert_detail(type="文章被购买",target=target,credit=authorGetCredit,info=authorInfo)
                dbsession.add(creditP2)
            elif type=="阅读文章":
                # 文章作者的userid 和nickname 以及应该获取的积分
                authorid = int(instanceArticle.searchUseridByArticleid(target)[0])
                authorNickname = instanceUser.searchNicknameByUserid(authorid)[0]

                # 阅读人的日志
                userPaidInfo = f"用户userid为{userid}的读者 ，阅读了作者id为{authorid}昵称为`{authorNickname}`的articleid号为‘{target}’文章"
                listLogger(userid, userPaidInfo, [2])
                # 作者获取积分的日志
                authorInfo = f"用户userid为{userid}的读者 ，阅读了作者id为{authorid}昵称为`{authorNickname}`的articleid号为‘{target}’文章 "
                listLogger(authorid, authorInfo, [6])
                instanceLog.insert_detail(type="文章被阅读",target=target,credit=0,info=authorInfo)
                # 作者也需要进入credit表
                creditP2 = Credit(userid=authorid, category="文章被阅读", target=target, credit=0,
                                  createtime=now,
                                  ipaddr=ipaddr, info=authorInfo)
                dbsession.add(creditP2)

        except:
            e=traceback.format_exc()
            allLogger(0,e)
        finally:
            # 提交表
            dbsession.add(creditP1)
            dbsession.commit()

    # 判断用户是否已经购买了该文章，已经购买的话，不会显示再让其购买
    def check_paid_article(self, articleid):
        result = dbsession.query(Credit).filter_by(userid=session.get("userid"), target=articleid).all()
        if len(result) > 0:
            return True
        else:
            return False

    # 每天登录加一分
    def check_limit_login_per_day(self, userid):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(Credit).filter(Credit.userid == userid,
                                                Credit.createtime.between(start, end)).count()
        if result == 0:
            return True
        else:
            return False


