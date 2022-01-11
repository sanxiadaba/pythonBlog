import json
from common.myLog import allLogger,rootDir
from constant import portNum

def returnUeConf(userid):
    myDirName="myPic_" + str(userid)
    urlPort=f"http://127.0.0.1:{portNum}/"
    ueFormat="../library/ueditor/jsp/upload/image"+f"/{myDirName}/"+"/{yyyy}{mm}{dd}/{time}{rand:6}"
    filename = "uecConfig" + '.json'
    directory = f"{rootDir}\\static\\ue"  # json文件所在的目录路径
    jsonStr = {}
    dic={
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
  "fileManagerListPath": "./static/upload/"+myDirName+"/",
  "fileManagerUrlPrefix": urlPort,
}

    def changeDic(name,value):
        jsonStr[f"{name}"]=value

    def doChange(dic):
        for name,value in dic.items():
            changeDic(name,value)

    try:
        with open(directory + '\\' + filename) as f:
            jsonStr = json.load(f)
            doChange(dic)
            return json.dumps(jsonStr)
    except Exception as e:
        allLogger(0,e)



