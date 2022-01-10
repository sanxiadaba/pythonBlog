import math

from flask import Blueprint, render_template, abort
from flask.json import jsonify

from constant import howArticleInWeb
from database.article import Article
from database.instanceDatabase import instanceArticle

index = Blueprint("index", __name__)


@index.route("/")
def home():
    last, most, recommended = instanceArticle.find_last_most_recommended()
    result = instanceArticle.find_limit_with_users(0, howArticleInWeb)
    total = math.ceil((instanceArticle.get_total_count() / howArticleInWeb))
    return render_template("index.html", result=result, total=total, page=1, last=last, most=most,
                           recommended=recommended)


@index.route("/page/<int:page>")
def paginate(page):
    start = (page - 1) * howArticleInWeb
    article = Article()
    result = article.find_limit_with_users(start, howArticleInWeb)
    total = math.ceil((article.get_total_count() / howArticleInWeb))
    return render_template("index.html", result=result, total=total, page=page)


@index.route("/type/<int:type>-<int:page>")
def classify(type, page):
    start = (page - 1) * 10
    result = instanceArticle.find_by_type(type, start, howArticleInWeb)
    total = math.ceil(instanceArticle.get_count_by_type(type) / howArticleInWeb)
    return render_template("type.html", result=result, page=page, total=total, type=type)


@index.route("/search/<int:page>-<string:keyword>")
def search(page, keyword):
    keyword = keyword.strip()
    if keyword is None or keyword == "" or "%" in keyword or len(keyword) > 10:
        abort(404)
    start = (page - 1) * 10
    result = instanceArticle.find_by_headline(keyword, start, 10)
    total = math.ceil(instanceArticle.get_count_by_headline(keyword) / 10)
    return render_template("search.html", page=page, total=total, result=result, keyword=keyword)


@index.route("/recommended")
def recommended():
    last, most, recommended = instanceArticle.find_last_most_recommended()
    return jsonify(last, most, recommended)
