"""
File description.

This file is mainly used to set the log
It wraps the loguru twice, and can generate the corresponding folder according to the logger's information
(The folder will be created automatically if it does not exist)
Then the logs are printed to the appropriate place

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

# Used for some basic settings of the project log
import os
# Import the library that traces where the function went wrong, so that the printed log is more detailed
import traceback
# 导入这个包是用来消除装饰器的”不良影响“
from functools import wraps

from flask import session, request, abort
# The logging system used in this project is based on the loguru package
from loguru import logger

from constant import compressedFormat, clearLogTime, logSize, whetherLogPrintInConsole

# Controls whether the output is on the console
if whetherLogPrintInConsole is True:
    pass
else:
    logger.remove(handler_id=None)


#  Get the userid of the current session
def getUseridBySession():
    return session.get("userid")


# Remove the \abc at the end of the path
def deleteFinal(allStr):
    allStr = allStr[::-1].split("\\", 1)[-1][::-1]
    return allStr


# Determine if a directory name exists in the specified directory
def dirInDir(dirName, path):
    if dirName in [dirNameLin for dirNameLin in os.listdir(path) if os.path.isdir(os.path.join(path, dirNameLin))]:
        pass
    else:
        osMkdir(dirName, path)


#  Create a folder with the specified name in the specified directory
def osMkdir(dirName, path):
    os.mkdir(path + "\\" + dirName)


#  List of user log files
userLogNameList = ["regLoginLogoutRecord", "payForArticle", "readArticle", "postArticle", "favoriteArticle",
                   "creditChange", "articleBeReaded", "commentArticle", "allLogs", "agreeOrDisagreeComment",
                   "beAgreeOrDisagreeComment"]

# All Log List
adminLogNameList = ["errorLog", "allLogs"]

# This directory should be D:\Code\Github\pythonBlog\common
commonDir = os.path.expanduser(os.path.dirname(os.path.abspath(__file__)))

# D:\Code\Github\pythonBlog
rootDir = deleteFinal(commonDir)

# D:\Code\Github\pythonBlog\logs
logDir = rootDir + "\\logs"

# D:\Code\Github\pythonBlog\logs\userLog
logUserLog = logDir + "\\" + "userLog"

# D:\Code\Github\pythonBlog\logs\adminLog
logAdminLog = logDir + "\\" + "adminLog"

# Path to store avatar
avatarPath = rootDir + "\\static\\img\\avatar"


# At the beginning, create the allLog and ErrorLog folders
def ininLogDir():
    # Is there a logs folder in the root directory, if so pass, if not create a new one
    dirInDir("logs", rootDir)

    # Determine whether there are errorLog and allLog, adminLog, userLog folders under the logDir folder, and generate if not
    dirInDir("errorLog", logDir)
    dirInDir("allLogs", logDir)
    dirInDir("adminLog", logDir)
    dirInDir("userLog", logDir)
    doMkdirManyInPath()


# Get all folders in the specified directory
def getAllDir(path):
    return [dirNameLin for dirNameLin in os.listdir(path) if os.path.isdir(os.path.join(path, dirNameLin))]


# Check if the relevant folders should be created under each folder, and if not, create them automatically
def doMkdirManyInPath():
    showMkdirList = getAllDir(logUserLog)
    for userid in showMkdirList:
        userid = userid.split("_")[-1]
        ininUserDir(userid=userid)


# Initialize the user's related directory
def ininUserDir(userid=None):
    """Create the directory where users store logs"""
    useridInMyLog = getUseridBySession() if userid is None else userid
    # Create a directory to store user information
    dirInDir(f"userLog_{useridInMyLog}", logUserLog)
    # Path to the directory where the user is stored
    logUserLogLin = logUserLog + "\\" + f"userLog_{useridInMyLog}"

    # Form for user registration, login, logout, password retrieval, and information modification  0
    dirInDir(userLogNameList[0], logUserLogLin)
    # Record of purchased articles   1
    dirInDir(userLogNameList[1], logUserLogLin)
    # Record of reading articles (what articles have been clicked to expand the full text)   2
    dirInDir(userLogNameList[2], logUserLogLin)
    # Posting, revision Drafting, recording of articles    3
    dirInDir(userLogNameList[3], logUserLogLin)
    # Favorites, uncollected records    4
    dirInDir(userLogNameList[4], logUserLogLin)
    # Record of point changes   5
    dirInDir(userLogNameList[5], logUserLogLin)
    # Records of your own articles being read, commented on, favorited, and unfavored    6
    dirInDir(userLogNameList[6], logUserLogLin)
    # Record of comments 7
    dirInDir(userLogNameList[7], logUserLogLin)
    # Logging of all operations   8
    dirInDir(userLogNameList[8], logUserLogLin)
    # Agree, disagree, and hide the record of comments   9
    dirInDir(userLogNameList[9], logUserLogLin)
    # Record of own comments being agreed, disagreed and replied   10
    dirInDir(userLogNameList[10], logUserLogLin)


# Wrapping the logger function logger again, so that it knows in which folder to print the log
def myLogger(n, info, userid=None):
    userid = getUseridBySession() if userid is None else userid
    info = info
    logName = userLogNameList[n]
    logUserLogLin = logUserLog + "\\" + f"userLog_{userid}" + "\\" + logName
    logFile = os.path.join(logUserLogLin, logName + ".log")
    logger.add(logFile, rotation=logSize, compression=compressedFormat, retention=clearLogTime)
    logger.info(info)
    logger.remove()


# Logging administrator actions
def adminLog(info=None):
    info = info
    logFile = logAdminLog + "\\" + "adminLog.log"
    logger.add(logFile, rotation=logSize, compression=compressedFormat, retention=clearLogTime)
    logger.info(info)
    logger.remove()


# Wraps another layer of myLogger to facilitate control of writing to multiple files
# # After the log is placed in a specific folder, it also writes a copy to its own alllog and to the total alllog
def listLogger(userid, info, *logList):
    logList = logList[0]
    for logNum in logList:
        info = info + f" The ip address is{request.remote_addr}"
        myLogger(logNum, info, userid)
    if logList[0] != 8:
        myLogger(8, info, userid)
    allLogger(1, info)


# Add logs to the allLogs errorLog in the /logs directory
# 0 is errorLog 1 is allLogs
def allLogger(n, info):
    info = info
    logName = adminLogNameList[n]
    logFile = os.path.join(logDir + "\\" + logName, logName + ".log")
    logger.add(logFile, rotation="20 MB", compression=compressedFormat, retention="12 months")
    if n == 0:
        logger.critical(info)
    else:
        logger.info(info)
    logger.remove()
    if n == 1:
        return
    else:
        allLogger(1, info)


# Error message decorators Note that another layer of wraps is added here to counteract the negative effects of the decorator usage
def logDanger(func):
    @wraps(func)
    def logDannerFun(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            e = traceback.format_exc()
            # Print error log and throw exceptions
            allLogger(0, e)
            return abort(404)

    return logDannerFun
