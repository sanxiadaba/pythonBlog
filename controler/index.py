import math

from flask import Blueprint, render_template, abort, session, request
from flask.json import jsonify

from database.article import Article
from database.users import Users

index = Blueprint("index", __name__)


@index.route("/")
def home():
    article = Article()
    last, most, recommended = article.find_last_most_recommended()
    result = article.find_limit_with_users(0, 10)
    total = math.ceil((article.get_total_count() / 10))
    return render_template("index.html", result=result, total=total, page=1, last=last, most=most,
                           recommended=recommended)


@index.route("/page/<int:page>")
def paginate(page):
    start = (page - 1) * 10
    article = Article()
    result = article.find_limit_with_users(start, 10)
    total = math.ceil((article.get_total_count() / 10))
    return render_template("index.html", result=result, total=total, page=page)


@index.route("/type/<int:type>-<int:page>")
def classify(type, page):
    start = (page - 1) * 10
    article = Article()
    result = article.find_by_type(type, start, 10)
    total = math.ceil(article.get_count_by_type(type) / 10)
    return render_template("type.html", result=result, page=page, total=total, type=type)


@index.route("/search/<int:page>-<string:keyword>")
def search(page, keyword):
    keyword = keyword.strip()
    if keyword is None or keyword == "" or "%" in keyword or len(keyword) > 10:
        abort(404)
    start = (page - 1) * 10
    article = Article()
    result = article.find_by_headline(keyword, start, 10)
    total = math.ceil(article.get_count_by_headline(keyword) / 10)
    return render_template("search.html", page=page, total=total, result=result, keyword=keyword)


@index.route("/recommended")
def recommended():
    article = Article()
    last, most, recommended = article.find_last_most_recommended()
    return jsonify(last, most, recommended)
