import time
from flask import session
from sqlalchemy import Table, func
from common.connect_db import connect_db
from database.users import Users
from constant import recommendedNumOfSide

dbsession, md, DBase = connect_db()


class Article(DBase):
    __table__ = Table("article", md, autoload=True)

    # 查询所有文章
    def find_all(self):
        return dbsession.query(Article).all()

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

    # 查询显示文章地数量
    def get_total_count(self):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1).count()
        return count

    # 进行分页
    def find_by_type(self, type, start, count):
        result = dbsession.query(Users.nickname, Article).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1, Article.type == type) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # 查看分页的数量
    def get_count_by_type(self, type):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                                Article.type == type).count()
        return count

    # 根据文章标题进行标题模糊搜索
    def find_by_headline(self, headline, start, count):
        result = dbsession.query(Users.nickname, Article).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                    Article.headline.like("%" + headline + "%")) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # 统计headline匹配的总数量
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

    # 最多阅读
    def find_most(self):
        result = dbsession.query(Article.articleid, Article.headline).filter(Article.hide == 0, Article.drafted == 0,
                                                                             Article.checked == 1) \
            .order_by(Article.readcount.desc()).limit(recommendedNumOfSide[1]).all()
        return result

    # 特别推荐  如果超过九篇可以用rand的方式随机显示
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

    # 当发表或者着回复评论后，为文章的replycount+1
    def update_replycount(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.replycount += 1
        dbsession.commit()

    # 插入一篇新文章
    def insert_article(self, type, headline, content, thumbnail, credit, drafted=0, checked=1):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        userid = session.get("userid")
        # 其他字段在数据库中已经设置好，无需自动插入
        article = Article(userid=userid, type=type, headline=headline, \
                          content=content, thumbnail=thumbnail, credit=credit, drafted=drafted, checked=checked,
                          createtime=now, updatetime=now)
        dbsession.add(article)
        dbsession.commit()
        return article.articleid

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
    def searchUseridByArticleid(self,articleid):
        return dbsession.query(Article.userid).filter_by(articleid=articleid).first()
