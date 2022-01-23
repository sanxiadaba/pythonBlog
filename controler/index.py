"""
File description.

This file is mainly to load some response of the home page
such as the title of the article, the author, fill a few, etc.

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

instanceArticle = Article()

index = Blueprint("index", __name__)


# Loading the home page, filling the sidebar, and articles and other related information
@index.route("/")
@logDanger
def home():
    # The main objection here is to the sidebar corresponding to what is filled
    last, most, recommended = instanceArticle.searchLastMostRecommended()
    result = instanceArticle.searchArticleWithUserByPage(0, howArticleInWeb)
    # Display several articles on one page
    total = math.ceil((instanceArticle.getAllCountOfArticle() / howArticleInWeb))
    return render_template("index.html", result=result, total=total, page=1, last=last, most=most,
                           recommended=recommended)


# Jump to the first page Just change the parameter
@index.route("/page/<int:page>")
@logDanger
def paginate(page):
    start = (page - 1) * howArticleInWeb
    article = Article()
    result = article.searchArticleWithUserByPage(start, howArticleInWeb)
    total = math.ceil((article.getAllCountOfArticle() / howArticleInWeb))
    return render_template("index.html", result=result, total=total, page=page)


# Jump to the modules of different categories
@index.route("/type/<int:type>-<int:page>")
@logDanger
def classify(type, page):
    start = (page - 1) * 10
    result = instanceArticle.searchArticleByType(type, start, howArticleInWeb)
    total = math.ceil(instanceArticle.searchCountByType(type) / howArticleInWeb)
    return render_template("type.html", result=result, page=page, total=total, type=type)


# The search function for articles is implemented here
@index.route("/search/<int:page>-<string:keyword>")
@logDanger
def search(page, keyword):
    keyword = keyword.strip()
    if keyword is None or keyword == "" or "%" in keyword or len(keyword) > 10:
        abort(404)
    start = (page - 1) * 10
    result = instanceArticle.searchHeadlineBySearchWord(keyword, start, 10)
    total = math.ceil(instanceArticle.searchCountOfArticleBySearchWord(keyword) / 10)
    return render_template("search.html", page=page, total=total, result=result, keyword=keyword)


# Filled sidebar recommendations
@index.route("/recommended")
@logDanger
def recommended():
    last, most, recommended = instanceArticle.searchLastMostRecommended()
    return jsonify(last, most, recommended)
