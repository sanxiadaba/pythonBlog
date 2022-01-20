import time

from flask import session
from sqlalchemy import Table, func

from common.connect_db import connect_db
from constant import recommendedNumOfSide
from database.users import Users

dbsession, md, DBase = connect_db()


class Article(DBase):
    __table__ = Table("article", md, autoload=True)

    # 根据id查询文章<Article,"nickname">
    def find_by_id(self, articleid):
        row = dbsession.query(Article, Users.nickname).join(Users, Users.userid \
                                                            == Article.userid).filter(Article.hide == 0,
                                                                                      Article.drafted == 0,
                                                                                      Article.checked == 1,
                                                                                      Article.articleid == articleid).first()
        return row

    # 指定分页的limit与offset 并与user做连接查询
    def find_limit_with_users(self, start, count):
        result = dbsession.query(Users.nickname, Article).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # 查询所有能显示的文章的数量
    def get_total_count(self):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1).count()
        return count

    # 查询不同的分页
    def find_by_type(self, type, start, count):
        result = dbsession.query(Users.nickname, Article).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1, Article.type == type) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # 查看不同分类类型的文章的数量
    def get_count_by_type(self, type):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                                Article.type == type).count()
        return count

    # 根据文章标题进行标题模糊搜索（主要用于search时调用）
    def find_by_headline(self, headline, start, count):
        result = dbsession.query(Users.nickname, Article).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                    Article.headline.like("%" + headline + "%")) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # 统计headline匹配的总数量（也是服务与搜索）
    def get_count_by_headline(self, headline):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                                Article.headline.like("%" + headline + "%")).count()
        return count

    # 最新文章推荐
    def find_last(self):
        result = dbsession.query(Article.articleid, Article.headline).filter(Article.hide == 0, Article.drafted == 0,
                                                                             Article.checked == 1) \
            .order_by(Article.articleid.desc()).limit(recommendedNumOfSide[0]).all()
        return result

    # 最多阅读推荐
    def find_most(self):
        result = dbsession.query(Article.articleid, Article.headline).filter(Article.hide == 0, Article.drafted == 0,
                                                                             Article.checked == 1) \
            .order_by(Article.readcount.desc()).limit(recommendedNumOfSide[1]).all()
        return result

    # 特别推荐  如果搜索结果超过栏目容量可以用rand的方式随机显示
    def find_recommended(self):
        result = dbsession.query(Article.articleid, Article.headline).filter(Article.hide == 0, Article.drafted == 0,
                                                                             Article.checked == 1,
                                                                             Article.recommended == 1) \
            .order_by(func.rand()).limit(recommendedNumOfSide[2]).all()
        return result

    # 一次性返回三个推荐  (封装）
    def find_last_most_recommended(self):
        last = self.find_last()
        most = self.find_most()
        recommended = self.find_recommended()
        return last, most, recommended

    # 每阅读一次，阅读次数加一
    def update_read_count(self, articleid):
        article = dbsession.query(Article).filter_by(articleid=articleid).first()
        newcount = article.readcount + 1
        dbsession.query(Article).filter_by(articleid=articleid).update({'readcount': newcount})
        dbsession.commit()

    # 根据文章id查标题
    def find_headline_by_id(self, articleid):
        row = dbsession.query(Article.headline).filter_by(articleid=articleid).first()
        return row.headline

    # 获取文章上一篇和下一篇的编号
    def find_prev_next_by_id(self, articleid):
        dict = {}

        # 查询比当前id 小的最大的一个
        row = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                              Article.articleid < articleid). \
            order_by(Article.articleid.desc()).limit(1).first()
        if row is None:
            prev_id = articleid
        else:
            prev_id = row.articleid
        dict["prev_id"] = prev_id
        dict["prev_headline"] = self.find_headline_by_id(prev_id)

        # 查询比当前id 大的最小的一个
        row = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                              Article.articleid > articleid). \
            order_by(Article.articleid).limit(1).first()
        if row is None:
            next_id = articleid
        else:
            next_id = row.articleid
        dict["next_id"] = prev_id
        dict["next_headline"] = self.find_headline_by_id(next_id)

        return dict

    # 为文章的的replycount+1
    def update_replycount(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.replycount += 1
        dbsession.commit()

    # 注意隐藏评论是评论的回复数要减去一
    def subtract_replycount(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.replycount -= 1
        dbsession.commit()

    # 插入一篇新文章
    def insert_article(self, type, headline, content, thumbnail, credit, drafted=0, checked=1):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        userid = int(session.get("userid"))
        # 其他字段在数据库中已经设置好，无需自动插入
        articleP = Article(userid=userid, type=type, headline=headline, \
                           content=content, thumbnail=thumbnail, credit=credit, drafted=drafted, checked=checked,
                           createtime=now, updatetime=now)
        dbsession.add(articleP)
        dbsession.commit()
        return articleP.articleid

    # 根据文章编号更新内容，用于文章编辑或草稿修改 以及草稿的发布
    def update_article(self, articleid, type, headline, content, thumbnail, credit, drafted=0, checked=1):
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

    # 根据文章id查询作者id
    def searchUseridByArticleid(self, articleid):
        return dbsession.query(Article.userid).filter_by(articleid=articleid).first()

    # 根据文章的id查询文章的标题和内容
    def searchHeadlineAndContentByArticleid(self, articleid):
        result = {}
        row = dbsession.query(Article.headline, Article.content).filter_by(articleid=articleid).first()
        result["headline"] = row[0]
        result["content"] = row[1]
        return result

    # 根据文章的id查询文章的标题
    def searchHeadlineByArticleid(self, articleid):
        row = dbsession.query(Article.headline).filter_by(articleid=articleid).first()[0]
        return row

    # 返回我的所有文章的id号、标题、内容、回复数、赞同数、反对数
    def searchAllMyArticle(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        allMyArticle = dbsession.query(Article).filter(Article.userid == userid, Article.hide == 0,
                                                       Article.drafted == 0, Article.checked == 1).order_by(
            Article.articleid).all()
        return allMyArticle

    # 修改文章标题
    def modifyArticleHeadline(self, articleid, headline):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.headline = headline
        dbsession.commit()

    # 修改文章缩略图
    def modifyArticleThumbnail(self, articleid, thumbnail):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.thumbnail = thumbnail
        dbsession.commit()

    # 隐藏文章
    def hideArticle(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.hide = 1
        dbsession.commit()

    # 作者本人删除文章
    def deleteArticle(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.hide = 1
        row.delete = 1
        dbsession.commit()

    # 设置编辑推荐按文章
    def recommendedArticle(self, articleid):
        row = dbsession.query(articleid).filter_by(articleid=articleid).first()
        row.recommended = 1
        dbsession.commit()

    # 所有文章数量
    def searchAllNumberOfArticle(self):
        return dbsession.query(Article).count()

    #  查询自己已经删除的文章的数量
    def searchDeleteArticleCount(self):
        userid = session.get("userid")
        return dbsession.query(Article).filter_by(userid=userid, delete=1).count()

    # 作者所有文章的数量
    def searchAllArticleNum(self):
        userid = session.get("userid")
        return dbsession.query(Article).filter_by(userid=userid).count()

    # 作者除了已删除的文章的数量
    def exceptDeleteNum(self):
        return self.searchAllArticleNum() - self.searchDeleteArticleCount()

    # 所有文章评论数量、访问数量之和
    def searchALLNumberOfComment(self):
        result = dbsession.query(Article.replycount, Article.readcount)
        allReplyCountList = []
        allReadCountList = []
        for row in result:
            allReplyCountList.append(row[0])
            allReadCountList.append(row[1])
        return sum(allReplyCountList), sum(allReadCountList)

    # 已发布文章的访问量
    def allNumOfAllArticleRead(self, userid=None):
        userid = session.get("userid") if userid is None else userid
        allNumOfAllArticleRead = dbsession.query(Article.readcount).filter(Article.hide == 0, Article.drafted == 0,
                                                                           Article.checked == 1,
                                                                           Article.userid == userid).all()
        allNumOfAllArticleRead = sum([i[0] for i in allNumOfAllArticleRead])
        return allNumOfAllArticleRead

    # 文章编号、文章标题、栏目、评论数量、阅读数量、创建日期
    def articleInfo(self, userid):
        result = dbsession.query(Article.articleid, Article.headline, Article.type, Article.replycount,
                                 Article.readcount, Article.createtime, Article.credit, Article.drafted,
                                 Article.checked, Article.hide, Article.recommended, Article.delete).filter(
            Article.userid == userid, Article.delete == 0).all()
        return result

    # 根据查询articleid是否是草稿
    def searchWhetherDrafted(self, articleid):
        result = dbsession.query(Article.drafted).filter_by(articleid=articleid).first()[0]
        return True if result is 1 else False

    # 查看文章是否被隐藏
    def searchWhetherHide(self, articleid):
        result = dbsession.query(Article.hide).filter_by(articleid=articleid).first()[0]
        return True if result is 1 else False
