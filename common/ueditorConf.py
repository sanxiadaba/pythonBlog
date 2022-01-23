"""
File description.
This file is used to modify the value of the ueitor (in order to adapt the ueitor to changes in the project parameters)


encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

import json
import traceback

from common.myLog import allLogger, rootDir
from constant import portNum


# The core function is to read the specified json file and change some fields, such as the port number, the storage directory
def returnUeConf(userid):
    myDirName = "myPic_" + str(userid)
    urlPort = f"http://127.0.0.1:{portNum}/"
    ueFormat = "../library/ueditor/jsp/upload/image" + f"/{myDirName}/" + "/{yyyy}{mm}{dd}/{time}{rand:6}"
    filename = "uecConfig" + '.json'
    directory = f"{rootDir}\\static\\ue"  # The path to the directory where the json file is located
    jsonStr = {}
    dic = {
        "imageUrlPrefix": urlPort,
        "imagePathFormat": ueFormat,
        "scrawlPathFormat": ueFormat,
        "scrawlUrlPrefix": urlPort,
        "snapscreenPathFormat": ueFormat,
        "snapscreenUrlPrefix": urlPort,
        "catcherPathFormat": ueFormat,
        "catcherUrlPrefix": urlPort,
        "videoPathFormat": ueFormat,
        "videoUrlPrefix": urlPort,
        "filePathFormat": ueFormat,
        "fileUrlPrefix": urlPort,
        "imageManagerListPath": urlPort,
        "imageManagerUrlPrefix": urlPort,
        "fileManagerListPath": "./static/upload/" + myDirName + "/",
        "fileManagerUrlPrefix": urlPort,
    }

    #  Changing the value of json
    def changeDic(name, value):
        jsonStr[f"{name}"] = value

    # Batch pass in what you want to change and change it with one click
    def doChange(dic):
        for name, value in dic.items():
            changeDic(name, value)

    #  Open the folder and load the json
    try:
        with open(directory + '\\' + filename) as f:
            jsonStr = json.load(f)
            doChange(dic)
            return json.dumps(jsonStr)
    except:
        e = traceback.format_exc()
        allLogger(0, e)
