"""
文件说明：

本文件主要用来设置日志
其对又对loguru进行了两次封装，可以根据登录者的信息生成对应文件夹
（文件夹不存在的话会自动创建）
然后将log日志打印到相应的地方

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

# 用来进行项目日志的一些基本设置
import os
# 导入追踪函数哪里出错的库，这样打印的日志更详细
import traceback
# 导入这个包是用来消除装饰器的”不良影响“
from functools import wraps

from flask import session, request, abort
# 本项目使用的日志系统是基于loguru进行封装得到的
from loguru import logger

from constant import compressedFormat, clearLogTime, logSize, whetherLogPrintInConsole

# 控制是否在控制台输出
if whetherLogPrintInConsole is True:
    pass
else:
    logger.remove(handler_id=None)


#  获取当前session的userid
def getUseridBySession():
    return session.get("userid")


# 去掉路径最后的 \abc
def deleteFinal(allStr):
    allStr = allStr[::-1].split("\\", 1)[-1][::-1]
    return allStr


# 判定指定目录下是否存在目录名
def dirInDir(dirName, path):
    if dirName in [dirNameLin for dirNameLin in os.listdir(path) if os.path.isdir(os.path.join(path, dirNameLin))]:
        pass
    else:
        osMkdir(dirName, path)


#  在指定目录下创建一个指定名称的文件夹
def osMkdir(dirName, path):
    os.mkdir(path + "\\" + dirName)


#  用户日志文件列表
userLogNameList = ["regLoginLogoutRecord", "payForArticle", "readArticle", "postArticle", "favoriteArticle",
                   "creditChange", "articleBeReaded", "commentArticle", "allLogs", "agreeOrDisagreeComment",
                   "beAgreeOrDisagreeComment"]

# 全部日志列表
adminLogNameList = ["errorLog", "allLogs"]

# 这个目录应该是 D:\Code\Github\pythonBlog\common
commonDir = os.path.expanduser(os.path.dirname(os.path.abspath(__file__)))

# D:\Code\Github\pythonBlog
rootDir = deleteFinal(commonDir)

# D:\Code\Github\pythonBlog\logs
logDir = rootDir + "\\logs"

# D:\Code\Github\pythonBlog\logs\userLog
logUserLog = logDir + "\\" + "userLog"

# D:\Code\Github\pythonBlog\logs\adminLog
logAdminLog = logDir + "\\" + "adminLog"

# 存放头像的路径
avatarPath=rootDir+"\\static\\img\\avatar"


# 在一开始，就创建allLog与ErrorLog文件夹
def ininLogDir():
    # 根目录下是否有logs文件夹，有的话pass，没有的话新建一个
    dirInDir("logs", rootDir)

    # 判断logDir文件夹下是否有errorLog与allLog、adminLog、userLog文件夹，没有的话生成
    dirInDir("errorLog", logDir)
    dirInDir("allLogs", logDir)
    dirInDir("adminLog", logDir)
    dirInDir("userLog", logDir)
    doMkdirManyInPath()


# 获取指定目录下的所有文件夹
def getAllDir(path):
    return [dirNameLin for dirNameLin in os.listdir(path) if os.path.isdir(os.path.join(path, dirNameLin))]


# 检查每个文件夹下是否应建了相关文件夹，没有的话，就自动给建
def doMkdirManyInPath():
    showMkdirList = getAllDir(logUserLog)
    for userid in showMkdirList:
        userid = userid.split("_")[-1]
        ininUserDir(userid=userid)


# 初始化user的相关目录
def ininUserDir(userid=None):
    """创建用户存放logs的目录"""
    useridInMyLog = getUseridBySession() if userid is None else userid
    # 创建存放用户信息的目录
    dirInDir(f"userLog_{useridInMyLog}", logUserLog)
    # 存放用户的目录路径
    logUserLogLin = logUserLog + "\\" + f"userLog_{useridInMyLog}"

    # 用户注册、登录、登出、找回密码、修改信息的表  0
    dirInDir(userLogNameList[0], logUserLogLin)
    # 购买文章的记录   1
    dirInDir(userLogNameList[1], logUserLogLin)
    # 阅读文章的记录（什么文章点过展开全文）   2
    dirInDir(userLogNameList[2], logUserLogLin)
    # 发布、修稿 草稿、文章的记录    3
    dirInDir(userLogNameList[3], logUserLogLin)
    # 收藏、取消收藏的记录    4
    dirInDir(userLogNameList[4], logUserLogLin)
    # 积分变化的记录   5
    dirInDir(userLogNameList[5], logUserLogLin)
    # 自己文章被阅读、被评论、收藏、取消收藏的记录    6
    dirInDir(userLogNameList[6], logUserLogLin)
    # 评论的记录 7
    dirInDir(userLogNameList[7], logUserLogLin)
    # 所有操作的记录   8
    dirInDir(userLogNameList[8], logUserLogLin)
    # 赞同、反对、隐藏评论的记录   9
    dirInDir(userLogNameList[9], logUserLogLin)
    # 自己评论被赞同、反对、回复的记录   10
    dirInDir(userLogNameList[10], logUserLogLin)


# 再次对日志函数logger进行封装，让其知道在哪个文件夹下打印日志
def myLogger(n, info, userid=None):
    userid = getUseridBySession() if userid is None else userid
    info = info
    logName = userLogNameList[n]
    logUserLogLin = logUserLog + "\\" + f"userLog_{userid}" + "\\" + logName
    logFile = os.path.join(logUserLogLin, logName + ".log")
    logger.add(logFile, rotation=logSize, compression=compressedFormat, retention=clearLogTime)
    logger.info(info)
    logger.remove()


# 对myLogger又封装了一层，方便控制写入多个文件
# 日志在放入特定的文件夹后，还会向自己的alllog以及总的alllog写入一份
def listLogger(userid, info, *logList):
    logList = logList[0]
    for logNum in logList:
        info = info + f" ip地址为{request.remote_addr}"
        myLogger(logNum, info, userid)
    if logList[0] != 8:
        myLogger(8, info, userid)
    allLogger(1, info)


# 向/logs 目录下的 allLogs errorLog 添加日志
# 0是errorLog 1是allLogs
def allLogger(n, info):
    info = info
    logName = adminLogNameList[n]
    logFile = os.path.join(logDir + "\\" + logName, logName + ".log")
    logger.add(logFile, rotation="10 MB", compression=compressedFormat, retention="12 months")
    if n == 0:
        logger.critical(info)
    else:
        logger.info(info)
    logger.remove()
    if n == 1:
        return
    else:
        allLogger(1, info)


# 错误信息的装饰器 注意这里要再加上一层wraps函数用来抵消装饰器使用过中的负面影响
def logDanger(func):
    @wraps(func)
    def logDannerFun(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            e = traceback.format_exc()
            # 打印错误日志并抛出异常
            allLogger(0, e)
            return abort(404)

    return logDannerFun
