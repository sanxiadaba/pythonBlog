# 用来进行项目日志的一些基本设置
import os
from loguru import logger
from constant import compressedFormat,clearLogTime,logSize
# 日志存放目录
logDir=os.path.expanduser("../logs")

# 日志名称
logFile=os.path.join(logDir,"log_{time}.log")

#  如果不存在文件夹，那就创建一个
if not os.path.exists(logDir):
    os.mkdir(logDir)

# 是否打印控制台
# logger.remove(handler_id=None)

# 日志配置
logger.add(logFile,rotation=logSize,compression=compressedFormat,retention=clearLogTime)