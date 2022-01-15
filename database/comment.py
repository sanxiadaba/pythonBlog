import time

from flask import session,request
from sqlalchemy import Table

from common.connect_db import connect_db
from common.utility import model_join_list
from constant import commentNum
from database.users import Users

dbsession, md, DBase = connect_db()


class Comment(DBase):
    __table__ = Table("comment", md, autoload=True)

    # 新增一条原始评论
    def insert_comment(self, articleid, content,info=None):
        if info is not None:
            info=info
        ipaddr=request.remote_addr
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        comment = Comment(userid=session.get("userid"), articleid=articleid, content=content,
                          ipaddr=ipaddr, createtime=now,info=info)
        dbsession.add(comment)
        dbsession.commit()

    # 根据文章编号查询其所有评论
    def find_by_articleid(self, articleid):
        result = dbsession.query(Comment).filter_by(articleid=articleid, hide=0, replyid=0).all()
        return result

    # 根据用户编号和日期进行查询是否已经超过一定条数的限制
    # （每天的评论次数也是有限的）
    def check_limit_per_day(self):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(Comment).filter(Comment.userid == session.get("userid"),
                                                 Comment.createtime.between(start, end)).count()
        if result >= commentNum:
            return True
        else:
            return False

    # 查询评论与用户信息  注意评论也需要分页
    def find_limit_with_user(self, articleid, start, count):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == Comment.userid) \
            .filter(Comment.articleid == articleid, Comment.hide == 0) \
            .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        return result

    # 新增一条原始评论的回复
    def insert_reply(self, articleid, commentid, content, ipaddr,info=None):
        if info is not  None:
            info=info
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        comment = Comment(userid=session.get("userid"), articleid=articleid, content=content, ipaddr=ipaddr,
                          replyid=commentid, createtime=now, updatetime=now,info=info)
        dbsession.add(comment)
        dbsession.commit()

    # 查询原始评论对应的用户信息，带分页参数
    def find_comment_with_user(self, articleid, start, count):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == Comment.userid).filter(
            Comment.articleid == articleid, Comment.hide == 0, Comment.replyid == 0) \
            .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        return result

    # 查询回复评论，回复评论不需要分页
    def find_reply_with_user(self, replyid):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == \
                                                      Comment.userid) \
            .filter(Comment.replyid == replyid, Comment.hide == 0).all()
        return result

    # 根据原始评论和回复评论生成一个关联列表
    def get_comment_user_list(self, articleid, start, count):
        result = self.find_comment_with_user(articleid, start, count)
        comment_list = model_join_list(result)
        for comment in comment_list:
            result = self.find_reply_with_user(comment["commentid"])
            comment["reply_list"] = model_join_list(result)
        return comment_list

    # 计算原始评论数量进行分页
    def get_count_by_article(self, articleid):
        count = dbsession.query(Comment).filter_by(articleid=articleid, hide=0, replyid=0).count()
        return count

    # 评论的赞同数量加一
    def update_agreecount(self, commentid):
        row = dbsession.query(Comment).filter_by(commentid=int(commentid)).first()
        row.agreecount += 1
        dbsession.commit()

    # 评论的反对数量加一
    def update_disagreecount(self, commentid):
        row = dbsession.query(Comment).filter_by(commentid=int(commentid)).first()
        row.opposecount += 1
        dbsession.commit()

    # 取消赞同
    def cancle_update_agreecount(self, commentid):
        row = dbsession.query(Comment).filter_by(commentid=int(commentid)).first()
        row.agreecount -= 1
        dbsession.commit()

    # 取消反对
    def cancle_update_disagreecount(self, commentid):
        row = dbsession.query(Comment).filter_by(commentid=int(commentid)).first()
        row.opposecount -= 1
        dbsession.commit()

    # 根据commentid查询userid
    def searchUseridByCommentid(self, commentid):
        return dbsession.query(Comment.userid).filter_by(commentid=commentid).one()[0]

    # 让指定的commentid隐藏
    def hideCommentByCommentid(self, commentid):
        data = dbsession.query(Comment).filter_by(commentid=commentid).first()
        data.hide = 1
        dbsession.commit()

    # 我的评论 #评论点赞数 #评论反对数(为求方便，这里先只显有关原始评论的信息)
    def searchAllMyComment(self):
        userid = session.get("userid")
        data = dbsession.query(Comment.content,Comment.agreecount,Comment.opposecount,Comment.articleid,Comment.commentid).filter_by(userid==userid).all()
        return data  # 注意，返回的是一个列表，列表的每个元素都是包含这五个元素的数组

    def numOfALLMyComment(self,userid=None):
        userid = session.get("userid") if userid is None else userid
        numOfALLMyComment=dbsession.query(Comment).filter_by(userid=userid).count()
        return numOfALLMyComment


