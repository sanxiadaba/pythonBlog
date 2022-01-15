"""
文件说明：

此文件主要是加载首页的一些响应
比如文章的标题、作者、填充几个等

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

import math

from flask import Blueprint, render_template, abort
from flask.json import jsonify

from common.myLog import logDanger
from constant import howArticleInWeb
from database.article import Article
from database.instanceDatabase import instanceArticle

index = Blueprint("index", __name__)


# 加载首页，填充侧边栏、以及文章等相关信息
@index.route("/")
@logDanger
def home():
    # 这里主要是反对侧边栏对应填充的东西
    last, most, recommended = instanceArticle.find_last_most_recommended()
    result = instanceArticle.find_limit_with_users(0, howArticleInWeb)
    # 一页显示几篇文章
    total = math.ceil((instanceArticle.get_total_count() / howArticleInWeb))
    return render_template("index.html", result=result, total=total, page=1, last=last, most=most,
                           recommended=recommended)


# 跳转到第几页 换个参数即可
@index.route("/page/<int:page>")
@logDanger
def paginate(page):
    start = (page - 1) * howArticleInWeb
    article = Article()
    result = article.find_limit_with_users(start, howArticleInWeb)
    total = math.ceil((article.get_total_count() / howArticleInWeb))
    return render_template("index.html", result=result, total=total, page=page)


# 跳转到不同分类的模块
@index.route("/type/<int:type>-<int:page>")
@logDanger
def classify(type, page):
    start = (page - 1) * 10
    result = instanceArticle.find_by_type(type, start, howArticleInWeb)
    total = math.ceil(instanceArticle.get_count_by_type(type) / howArticleInWeb)
    return render_template("type.html", result=result, page=page, total=total, type=type)


# 这里实现对文章的搜索功能
@index.route("/search/<int:page>-<string:keyword>")
@logDanger
def search(page, keyword):
    keyword = keyword.strip()
    if keyword is None or keyword == "" or "%" in keyword or len(keyword) > 10:
        abort(404)
    start = (page - 1) * 10
    result = instanceArticle.find_by_headline(keyword, start, 10)
    total = math.ceil(instanceArticle.get_count_by_headline(keyword) / 10)
    return render_template("search.html", page=page, total=total, result=result, keyword=keyword)


# 填充侧边栏推荐
@index.route("/recommended")
@logDanger
def recommended():
    last, most, recommended = instanceArticle.find_last_most_recommended()
    return jsonify(last, most, recommended)
