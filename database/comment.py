import time
from constant import commentNum
from flask import session
from sqlalchemy import Table, func
from common.connect_db import connect_db
from common.utility import model_join_list
from database.users import Users
dbsession, md, DBase = connect_db()


class Comment(DBase):
    __table__ = Table("comment", md, autoload=True)

    # 新增一条评论
    def insert_comment(self, articleid, content, ipaddr):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        comment = Comment(userid=session.get("userid"), articleid=articleid, content=content,
                          ipaddr=ipaddr, createtime=now, updatetime=now)
        dbsession.add(comment)
        dbsession.commit()


    # 根据文章编号查询所有评论
    def find_by_articleid(self, articleid):
        result = dbsession.query(Comment).filter_by(articleid=articleid, hide=0, replyid=0).all()
        return result

    # 根据用户编号和日期进行查询是否已经超过每天五条的限制
    def check_limit_per_day(self):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(Comment).filter(Comment.userid == session.get("userid"),
                                                 Comment.createtime.between(start, end)).all()
        if len(result) >= commentNum:
            return True
        else:
            return False



    # 查询评论与用户信息  注意评论也需要分页
    def find_limit_with_user(self, articleid, start, count):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == Comment.userid) \
            .filter(Comment.articleid == articleid, Comment.hide == 0) \
            .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        return result

    # 新增一条回复
    def insert_reply(self, articleid, commentid, content, ipaddr):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        comment = Comment(userid=session.get("userid"), articleid=articleid, content=content, ipaddr=ipaddr,
                          replyid=commentid, createtime=now, updatetime=now)
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
