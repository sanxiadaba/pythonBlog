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

from datetime import timedelta

"""Fill in the mysql configuration here
若是远程 配置格式例如“root(Remote host username):root(mysql username)@***.**.**.***(ip address):3306(Port number)” 
比如
config_mysql=mysql://root:root@120.28.243.198:3306(This address does not exist, just do an example)
"""
config_mysql = "root@localhost:3306"

# Set the name of the database (the following is the name of my test database, specific items need to be changed)
databaseName = "myBlog"

# Set the port number
portNum = 1234

# Whether to start in debug mode or not (if enabled, the server will restart automatically after the code is modified in the backend)
# The server will restart automatically, it is recommended to set to false in the official project)
whetherDebug = True

# Set the session expiration time Here you can also set weeks, months, etc.
sessionExpirationTime = timedelta(days=30)

# Set whether session is invalid after each server restart, default is false, i.e. session is still valid after server restart
sessionRestart = False

# Set the category name of the homepage, here write five, you can also add
classification = ["Python", "LeetCode", "Project", "Learning", "Others"]

# Send account with registered email
emailAccount = "*******"

""" Authorization code for registering mailbox (not mailbox login password) #Refer to this website (https://www.ujcms.com/documentation/351.html)
Now only qq mailbox sending service is supported, and it is also better to use qq mailbox registration when registering (please excuse any inconvenience) """

emailAdmit = "*******"

# Whether to use github's third-party login feature (requires configuration, see the readme documentation for details)
whetherUseGithubLogin = True

# Set the Client ID and Client secrets required for github third-party login # To be developed
# GITHUB_CLIENT_ID = '*********'
# GITHUB_CLIENT_SECRET = '***********'

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
# 压缩文件的格式
compressedFormat = "zip"

# The time for regular cleaning (optional such as "1 day" "1 week" "3 months" etc.) Note the plural of time
clearLogTime = "1 month"

# Size of split logs (logs are automatically compressed after a certain volume and then a new log is started) Optional parameters are KB GM MB
logSize = "0.1 MB"

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
everyPageInHou = 2

# Set the language of the ueditor (optionally "English" or "Chinese")
ueiditorLanguage = "English"
