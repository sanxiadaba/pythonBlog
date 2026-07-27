"""Application settings kept as module attributes for legacy controllers.

Environment parsing is deliberately defensive so a fresh checkout can be imported
without a private .env file. Flask-specific settings live in ``create_app``.
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv(override=False)


def _env_int(name, default):
    raw = os.getenv(name)
    if raw in (None, ""):
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def _env_bool(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


sessionExpirationTime = timedelta(days=30)
classification = ["Python", "LeetCode", "Project", "Learning", "Others"]
commentNum = 10
whetherDistinguishCapital = False
regGiveCredit = 50
loginEvereDayCredit = 1
postArticleCredit = 10
replyAndAddCommentCredit = 2
rateCreditForArticle = 0.5
creditListForReleaseArticle = [1, 2, 5, 10, 20, 50]
howArticleInWeb = 10
howCommentInArticle = 5
whetherSaveShufflingFigure = True
shufflingFigurePicture = ["banner-1.jpg", "banner-2.jpg", "banner-3.jpg"]
shufflingFigureLink = ["/", "/", "/"]
indexLogoPicture = "logo.png"
indexLogoPictureSize = (60, 60)
indexAboveStr = ["Welcome to my blog", "Study well", "Day Up"]
thumbNailNum = 10
recommendedNumOfSide = [9, 9, 9]
compressedFormat = "zip"
clearLogTime = "1 month"
logSize = "1 MB"
whetherLogPrintInConsole = True
timeoutOfEcode = 120
maxUserPostArticleNum = 10
maxUserPostArticleNumOfEditor = 20
maxModifyArticleNum = 10
maxUploadPicNum = 20
everyPageInHou = 5

blogLanguage = os.getenv("blogLanguage", "Chinese")
md5Salt = os.getenv("md5Salt", "legacy-password-migration-only")
portNum = _env_int("PORT_NUM", 5000)
whetherDebug = _env_bool("DEBUG_MODE", True)
sessionRestart = False
emailType = os.getenv("USE_GMAIL_OR_QQMAIL", "QQMAIL")
emailAccount = os.getenv("EMAIL_ACCOUNT", "")
emailAdmit = os.getenv("EMAIL_PASSWORD", "")

# Compatibility attributes for old imports. New connections use DATABASE_URL.
localOrRemote = os.getenv("LOCAL_OR_REMOTE", "localhost")
mysqlUserName = os.getenv("MYSQL_USER_NAME", "")
mysqlPort = _env_int("MYSQL_PORT", 3306)
mysqlUrl = os.getenv("MYSQL_URL", "127.0.0.1")
databaseName = os.getenv("MYSQL_DATABASE_NAME", "python_blog")
mysqlPassword = os.getenv("MYSQL_PASSWORD", "")
config_mysql = ""

adminLogin = os.getenv("ADMIN_LOGIN_NAME", "")
editorLogin = os.getenv("EDITOR_LOGIN_NAME", "")
userLogin = os.getenv("USER_LOGIN_NAME", "")
adminPassword = os.getenv("ADMIN_PASSWORD", "")
editorPassword = os.getenv("EDITOR_PASSWORD", "")
userPassword = os.getenv("USER_PASSWORD", "")
