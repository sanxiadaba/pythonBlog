import time

from flask import session
from sqlalchemy import Table, func

from common.connectDb import connectDb
from constant import recommendedNumOfSide

dbsession, md, DBase = connectDb()

class Users(DBase):
    __table__ = Table("users", md, autoload=True)

class Article(DBase):
    __table__ = Table("article", md, autoload=True)

    # Search articles by id
    def searchArticleByUserid(self, articleid):
        row = dbsession.query(Article, Users.nickname).join(Users, Users.userid \
                                                            == Article.userid).filter(Article.hide == 0,
                                                                                      Article.drafted == 0,
                                                                                      Article.checked == 1,
                                                                                      Article.articleid == articleid).first()
        return row

    # Specify the limit and offset of paging and do a join query with user
    def searchArticleWithUserByPage(self, start, count):
        result = dbsession.query(Users.nickname, Article).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # Query the number of all articles that can be displayed
    def getAllCountOfArticle(self):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1).count()
        return count

    # Query different types
    def searchArticleByType(self, type, start, count):
        result = dbsession.query(Users.nickname, Article).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1, Article.type == type) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # View the number of articles in different category types
    def searchCountByType(self, type):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                                Article.type == type).count()
        return count

    # Title fuzzy search according to the title of the article (mainly used when SEARCH is called)
    def searchHeadlineBySearchWord(self, headline, start, count):
        result = dbsession.query(Users.nickname, Article).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                    Article.headline.like("%" + headline + "%")) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # Count the total number of headline matches (also served with search)
    def searchCountOfArticleBySearchWord(self, headline):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                                Article.headline.like("%" + headline + "%")).count()
        return count

    # Latest article recommendation
    def searchRecommendedOfLastTime(self):
        result = dbsession.query(Article.articleid, Article.headline).filter(Article.hide == 0, Article.drafted == 0,
                                                                             Article.checked == 1) \
            .order_by(Article.articleid.desc()).limit(recommendedNumOfSide[0]).all()
        return result

    # Most Read Recommendations
    def searchRecommendedByReadMost(self):
        result = dbsession.query(Article.articleid, Article.headline).filter(Article.hide == 0, Article.drafted == 0,
                                                                             Article.checked == 1) \
            .order_by(Article.readcount.desc()).limit(recommendedNumOfSide[1]).all()
        return result

    # Special recommendation If the search results exceed the column capacity can be displayed randomly by rand
    def searchRecommendedByAdmin(self):
        result = dbsession.query(Article.articleid, Article.headline).filter(Article.hide == 0, Article.drafted == 0,
                                                                             Article.checked == 1,
                                                                             Article.recommended == 1) \
            .order_by(func.rand()).limit(recommendedNumOfSide[2]).all()
        return result

    # Return three recommendations at once (encapsulated)
    def searchLastMostRecommended(self):
        last = self.searchRecommendedOfLastTime()
        most = self.searchRecommendedByReadMost()
        recommended = self.searchRecommendedByAdmin()
        return last, most, recommended

    # For each reading, add one to the reading count
    def updateReadCount(self, articleid):
        article = dbsession.query(Article).filter_by(articleid=articleid).first()
        newcount = article.readcount + 1
        dbsession.query(Article).filter_by(articleid=articleid).update({'readcount': newcount})
        dbsession.commit()

    # Check the title according to the article id
    def searchHeadlineByArticleId(self, articleid):
        row = dbsession.query(Article.headline).filter_by(articleid=articleid).first()
        return row.headline

    # Get the number of the previous and next article
    def searchPrevNextArticleByArticleid(self, articleid):
        dict = {}

        # Query the largest one that is smaller than the current id
        row = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                              Article.articleid < articleid). \
            order_by(Article.articleid.desc()).limit(1).first()
        if row is None:
            prev_id = articleid
        else:
            prev_id = row.articleid
        dict["prev_id"] = prev_id
        dict["prev_headline"] = self.searchHeadlineByArticleId(prev_id)

        # Query the smallest one that is larger than the current id
        row = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                              Article.articleid > articleid). \
            order_by(Article.articleid).limit(1).first()
        if row is None:
            next_id = articleid
        else:
            next_id = row.articleid
        dict["next_id"] = prev_id
        dict["next_headline"] = self.searchHeadlineByArticleId(next_id)

        return dict

    # Add 1 to the replycount of the article
    def updateReplyCount(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.replycount += 1
        dbsession.commit()

    # Note that the hidden comment is the number of replies to the comment to be subtracted by one
    def subtractReplycount(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.replycount -= 1
        dbsession.commit()

    # Insert a new article
    def insertArticle(self, type, headline, content, thumbnail, credit, drafted=0, checked=1):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        userid = int(session.get("userid"))
        # Other fields are already set in the database and do not need to be inserted automatically
        articleP = Article(userid=userid, type=type, headline=headline, \
                           content=content, thumbnail=thumbnail, credit=credit, drafted=drafted, checked=checked,
                           createtime=now, updatetime=now)
        dbsession.add(articleP)
        dbsession.commit()
        return articleP.articleid

    # Update content by article number for article editing or draft revision and draft posting
    def updateArticle(self, articleid, type, headline, content, thumbnail, credit, drafted=0, checked=1):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.type = type
        row.headline = headline
        row.content = content
        row.thumbnail = thumbnail
        row.credit = credit
        row.drafted = drafted
        row.checked = checked
        row.updatetime = now
        dbsession.commit()
        return articleid

    # Search author id by article id
    def searchUseridByArticleid(self, articleid):
        return dbsession.query(Article.userid).filter_by(articleid=articleid).first()

    # Search the title and content of an article by its id
    def searchHeadlineAndContentByArticleid(self, articleid):
        result = {}
        row = dbsession.query(Article.headline, Article.content).filter_by(articleid=articleid).first()
        result["headline"] = row[0]
        result["content"] = row[1]
        return result

    # Look up the title of the article by its id
    def searchHeadlineByArticleid(self, articleid):
        row = dbsession.query(Article.headline).filter_by(articleid=articleid).first()[0]
        return row

    # Return all my posts with id number, title, content, number of replies, number of approval, number of disapproval
    def searchAllMyArticle(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        allMyArticle = dbsession.query(Article).filter(Article.userid == userid, Article.hide == 0,
                                                       Article.drafted == 0, Article.checked == 1).order_by(
            Article.articleid).all()
        return allMyArticle

    # Modify article title
    def modifyArticleHeadline(self, articleid, headline):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.headline = headline
        dbsession.commit()

    # Modify article thumbnails
    def modifyArticleThumbnail(self, articleid, thumbnail):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.thumbnail = thumbnail
        dbsession.commit()

    # Hide article
    def hideArticle(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.hide = 1
        dbsession.commit()

    # The author himself deleted the article
    def deleteArticle(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.hide = 1
        row.delete = 1
        dbsession.commit()

    # Set editorial recommendation by article
    def recommendedArticle(self, articleid):
        row = dbsession.query(articleid).filter_by(articleid=articleid).first()
        row.recommended = 1
        dbsession.commit()

    # Number of all articles
    def searchAllNumberOfArticle(self):
        return dbsession.query(Article).count()

    #  Check the number of articles you have deleted
    def searchDeleteArticleCount(self, userid=None):
        userid = session.get("userid") if userid == None else userid
        return dbsession.query(Article).filter_by(userid=userid, delete=1).count()

    # Number of all articles by the author
    def searchAllArticleNum(self):
        return dbsession.query(Article).count()

    # Number of all articles by the author
    def searchAllArticleNumByUserid(self, userid=None):
        userid = session.get("userid") if userid == None else userid
        return dbsession.query(Article).filter_by(userid=userid).count()

    # The number of articles the author has deleted in addition to
    def exceptDeleteNum(self, userid=None):
        return self.searchAllArticleNumByUserid(userid) - self.searchDeleteArticleCount(userid)

    # The sum of the number of comments and visits to all articles
    def searchALLNumberOfComment(self):
        result = dbsession.query(Article.replycount, Article.readcount).filter_by(drafted=0, hide=0, checked=1)
        allReplyCountList = []
        allReadCountList = []
        for row in result:
            allReplyCountList.append(row[0])
            allReadCountList.append(row[1])
        #   Return the number of comments and reads of all articles
        return sum(allReplyCountList), sum(allReadCountList)

    # Number of visits to published articles
    def allNumOfAllArticleRead(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        allNumOfAllArticleRead = dbsession.query(Article.readcount).filter(Article.hide == 0, Article.drafted == 0,
                                                                           Article.checked == 1,
                                                                           Article.userid == userid).all()
        allNumOfAllArticleRead = sum([i[0] for i in allNumOfAllArticleRead])
        return allNumOfAllArticleRead

    # Article number, article title, column, number of comments, number of reads, date of creation
    def articleInfo(self, userid):
        result = dbsession.query(Article.articleid, Article.headline, Article.type, Article.replycount,
                                 Article.readcount, Article.createtime, Article.credit, Article.drafted,
                                 Article.checked, Article.hide, Article.recommended).filter(
            Article.userid == userid, Article.delete == 0).all()
        return result

    # Based on the query whether articleid is a draft or not
    def searchWhetherDrafted(self, articleid):
        result = dbsession.query(Article.drafted).filter_by(articleid=articleid).first()[0]
        return True if result == 1 else False

    # Check if the article is hidden
    def searchWhetherHide(self, articleid):
        try:
            result = dbsession.query(Article.hide).filter_by(articleid=articleid).first()[0]
            return True if result == 1 else False
        except:
            return True
