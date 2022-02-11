"""
Document Description.

Many configuration parameters for the entire blog project
Each parameter is annotated with a description

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""
# Load environment variables first
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)
import os
from datetime import timedelta

# Set the session expiration time Here you can also set weeks, months, etc.
sessionExpirationTime = timedelta(days=30)

# Set the category name of the homepage, here write five, you can also add
classification = ["Python", "LeetCode", "Project", "Learning", "Others"]

# Set the maximum number of comments per day for no one
commentNum = 10

# Whether the image verification code supports case-insensitive (this refers to the image verification code for login, not the text verification code for account registration)
whetherDistinguishCapital = False

# of points sent for registration
regGiveCredit = 50

# Daily login bonus points (already processed, you can only receive one login bonus per day)
loginEvereDayCredit = 1

# Points sent for publishing articles (there is no limit to the number of articles sent per day here, so please be careful to give editor status)
postArticleCredit = 10

# Adding comments and replying to comments increases points per point
replyAndAddCommentCredit = 2

# The author sets the article to receive points, and the author's share after other readers pay points
rateCreditForArticle = 0.5

# Posting with points for optional collection of points for articles
creditListForReleaseArticle = [1, 2, 5, 10, 20, 50]

# There are several articles per page
howArticleInWeb = 10

# of comments per post (not counting replies to replies to comments)
howCommentInArticle = 5

# Whether to have a rotating image of the home page
whetherSaveShufflingFigure = True

# The position of the image corresponding to the rotating image Note that the number of links should be consistent with the following images
# Note that this should be the image at the bottom of /static/img/banner (only the file name is filled in below)
shufflingFigurePicture = ["banner-1.jpg", "banner-2.jpg", "banner-3.jpg"]

# Click on the link of the corresponding image of the rotating image
shufflingFigureLink = ["https://github.com/sanxiadaba/pythonBlog", "https://github.com/sanxiadaba/pythonBlog",
                       "https://github.com/sanxiadaba/pythonBlog"]

# The address of the logo on the top left corner of the home page (the location of the image here is placed under /static/img/logo)
indexLogoPicture = "logo.png"

# The length and width of the logo (in the form of an array)
indexLogoPictureSize = (60, 60)

# The two words at the top of the home page and the words in the upper left corner of the mobile
indexAboveStr = ["Welcome to my blog", "Study well", "Day Up"]

# of randomly generated avatar thumbnails (a random thumbnail is generated when the user registers, which can be changed by the reader later)
# Be sure to have the appropriate number of avatar images at the bottom of /static/img/avatar

thumbNailNum = 10

# of recommendations in the three columns of the sidebar
# Latest posts Most reads Special recommendations
recommendedNumOfSide = [9, 9, 9]

"""
Here are the settings related to the log file
"""
# Format of compressed files
compressedFormat = "zip"

# The time for regular cleaning (optional such as "1 day" "1 week" "3 months" etc.) Note the plural of time
clearLogTime = "1 month"

# Size of split logs (logs are automatically compressed after a certain volume and then a new log is started) Optional parameters are KB GM MB
logSize = "1 MB"

# Whether the printed loguru is output on the console
whetherLogPrintInConsole = True

# Captcha will expire after a specified time # in seconds
timeoutOfEcode = 120

# Set the maximum number of contributions and posts per user and editor per day
maxUserPostArticleNum = 10
maxUserPostArticleNumOfEditor = 20

# Set the maximum number of post modifications per day
maxModifyArticleNum = 10

# Maximum number of images uploaded per person per day
maxUploadPicNum = 20

# Set in the backend page of managing articles, not many article pagination
everyPageInHou = 5

# Here are some variables about the environment configuration
blogLanguage = os.environ.get("blogLanguage")

md5Salt = os.environ.get("md5Salt")

localOrRemote = os.environ.get("LOCAL_OR_REMOTE")

mysqlUserName = os.environ.get("MYSQL_USER_NAME")

mysqlPort = int(os.environ.get("MYSQL_PORT"))

mysqlUrl = os.environ.get("MYSQL_URL")

databaseName = os.environ.get("MYSQL_DATABASE_NAME")

portNum = int(os.environ.get("PORT_NUM"))

if localOrRemote == "localhost":
    config_mysql = mysqlUserName + "@" + mysqlUrl + ":" + str(mysqlPort)
elif localOrRemote == "remote":
    remoteAccount = os.environ.get("REMOTE_ADDRESS_ACCOUNT")
    config_mysql = remoteAccount + ":" + mysqlUserName + "@" + mysqlUrl + ":" + str(portNum)
else:
    raise Exception("Please configure the correct mysql")

adminLogin = os.environ.get("ADMIN_LOGIN_NAME")
editorLogin = os.environ.get("EDITOR_LOGIN_NAME")
userLogin = os.environ.get("USER_LOGIN_NAME")
adminPassword = os.environ.get("ADMIN_PASSWORD")
editorPassword = os.environ.get("EDITOR_PASSWORD")
userPassword = os.environ.get("USER_PASSWORD")

whetherDebug = True if os.environ.get("DEBUG_MODE") == "True" else False

sessionRestart = True if os.environ.get("SESSION_RESTART") == "True" else False

# Send account with registered email
emailType = os.environ.get("USE_GMAIL_OR_QQMAIL")
emailAccount = os.environ.get("EMAIL_ACCOUNT")
emailAdmit = os.environ.get("EMAIL_PASSWORD")
mysqlPassword = os.environ.get("MYSQL_PASSWORD")
