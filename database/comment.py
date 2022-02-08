import time

from flask import session, request
from sqlalchemy import Table

from common.connectDb import connectDb
from common.utility import model_join_list
from constant import commentNum

dbsession, md, DBase = connectDb()

class Users(DBase):
    __table__ = Table("users", md, autoload=True)

class Comment(DBase):
    __table__ = Table("comment", md, autoload=True)

    # Add an original comment
    def insertComment(self, articleid, content, info=None):
        if info is not None:
            info = info
        ipaddr = request.remote_addr
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        comment = Comment(userid=session.get("userid"), articleid=articleid, content=content,
                          ipaddr=ipaddr, createtime=now, info=info)
        dbsession.add(comment)
        dbsession.commit()

    # Search all comments by article number
    def searchCommentByArticleid(self, articleid):
        result = dbsession.query(Comment).filter_by(articleid=articleid, hide=0, replyid=0).all()
        return result

    # Query by user number and date to see if the limit of a certain number of comments has been exceeded
    # (the number of comments per day is also limited)
    def whetherLimitEveryDayCommentNum(self):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(Comment).filter(Comment.userid == session.get("userid"),
                                                 Comment.createtime.between(start, end)).count()
        if result >= commentNum:
            return True
        else:
            return False

    # Query comments and user information Note that comments also need to be paged
    def searchCommentLimitWithUser(self, articleid, start, count):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == Comment.userid) \
            .filter(Comment.articleid == articleid, Comment.hide == 0) \
            .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        return result

    # Add a reply to the original comment
    def insertArticleComment(self, articleid, commentid, content, ipaddr, info=None):
        if info is not None:
            info = info
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        comment = Comment(userid=session.get("userid"), articleid=articleid, content=content, ipaddr=ipaddr,
                          replyid=commentid, createtime=now, updatetime=now, info=info)
        dbsession.add(comment)
        dbsession.commit()

    # Query the user information corresponding to the original comment, with paging parameters
    def searchUserInfoAndCommentByArticleid(self, articleid, start, count):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == Comment.userid).filter(
            Comment.articleid == articleid, Comment.hide == 0, Comment.replyid == 0) \
            .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        return result

    # Query reply comments, reply comments without paging
    def searchReplyWithUserByReplyid(self, replyid):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == \
                                                      Comment.userid) \
            .filter(Comment.replyid == replyid, Comment.hide == 0).all()
        return result

    # Generate a list of associations based on original comments and replies to comments
    def searchCommentWithUser(self, articleid, start, count):
        result = self.searchUserInfoAndCommentByArticleid(articleid, start, count)
        comment_list = model_join_list(result)
        for comment in comment_list:
            result = self.searchReplyWithUserByReplyid(comment["commentid"])
            comment["reply_list"] = model_join_list(result)
        return comment_list

    # Calculate the number of original comments for paging
    def searchCountOfCommentByArticleid(self, articleid):
        count = dbsession.query(Comment).filter_by(articleid=articleid, hide=0, replyid=0).count()
        return count

    # Add one to the number of approvals for comments
    def updataCommentAgree(self, commentid):
        row = dbsession.query(Comment).filter_by(commentid=int(commentid)).first()
        row.agreecount += 1
        dbsession.commit()

    # Number of objections to comments plus one
    def updateCommentDisagree(self, commentid):
        row = dbsession.query(Comment).filter_by(commentid=int(commentid)).first()
        row.opposecount += 1
        dbsession.commit()

    # Cancel endorsement
    def cancleUpdateCommentAgree(self, commentid):
        row = dbsession.query(Comment).filter_by(commentid=int(commentid)).first()
        row.agreecount -= 1
        dbsession.commit()

    # Cancel Objections
    def cancleUpdateCommentDisagree(self, commentid):
        row = dbsession.query(Comment).filter_by(commentid=int(commentid)).first()
        row.opposecount -= 1
        dbsession.commit()

    # Query userid according to commentid
    def searchUseridByCommentid(self, commentid):
        return dbsession.query(Comment.userid).filter_by(commentid=commentid).one()[0]

    # Make the specified commentid hidden
    def hideCommentByCommentid(self, commentid):
        data = dbsession.query(Comment).filter_by(commentid=commentid).first()
        data.hide = 1
        dbsession.commit()

    # My comments #Comment likes #Comment objections (for convenience, only information about the original comment is displayed here first)
    def searchAllMyComment(self):
        userid = session.get("userid")
        data = dbsession.query(Comment.content, Comment.agreecount, Comment.opposecount, Comment.articleid,
                               Comment.commentid).filter_by(userid == userid).all()
        return data  # Note that what is returned is a list, and each element of the list is an array containing these five elements

    def numOfALLMyComment(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        numOfALLMyComment = dbsession.query(Comment).filter_by(userid=userid, hide=0, replyid=0).count()
        return numOfALLMyComment

    # 查询所有评论，和隐藏评论的数量
    def numOfDeletedComment(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        numOfAll = dbsession.query(Comment).filter_by(userid=userid, hide=0).count()
        numOfDeleted = dbsession.query(Comment).filter_by(userid=userid, hide=1).count()
        return numOfAll, numOfDeleted

    # The module of my comments of the back office management
    def searchMyComment(self, userid):
        result = dbsession.query(Comment.content, Comment.agreecount, Comment.opposecount, Comment.articleid,
                                 Comment.createtime, Comment.commentid).filter(Comment.hide == 0, Comment.replyid == 0,
                                                                               Comment.userid == userid).all()
        return result, len(result)

    # Search all comments under articleid
    def searchAllComment(self, articleid):
        row = dbsession.query(Comment.commentid).filter_by(articleid=articleid).all()
        result = []
        for i in row:
            result.append(i[0])
        return result

    # Set all comments under the article to be hidden when deleting the article
    def hideCommnetWhenHideArticle(self, articleid):
        for i in self.searchAllComment(articleid):
            lin = dbsession.query(Comment).filter_by(commentid=i).first()
            lin.hide = 1
        dbsession.commit()
