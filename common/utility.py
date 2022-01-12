"""
文件说明：
这个文件放一些比较通用，能独立运行的一些函数
比如发送邮件、生成压缩图片、压缩图片、生成加密转换md5等
一些公共的功能的组件部分

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

import random
import string
import time
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from hashlib import md5
from io import BytesIO
from smtplib import SMTP_SSL
from common.myLog import rootDir,dirInDir
from PIL import Image, ImageFont, ImageDraw
from flask import request, session
from common.myLog import listLogger
from constant import emailAdmit, emailAccount, portNum


# 生成验证码（带干扰线）
class ImageCode:
    #  生成随机字符串
    def gen_text(self):
        list = random.sample(string.ascii_letters + string.digits, 4)
        return "".join(list)

    # 生成随机颜色
    def rand_color(self):
        red = random.randint(32, 200)
        green = random.randint(22, 255)
        blue = random.randint(0, 200)
        return red, green, blue

    # 画干扰线
    def draw_line(self, draw, num, width, height):
        for num in range(num):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height / 2, height)
            draw.line(((x1, y1), (x2, y2)), fill="black", width=2)

    # 绘制验证码图片
    def draw_verify_code(self):
        code = self.gen_text()
        width, height = 120, 50  # 设置图片大小
        # 创建图片对象，并设置背景为白色
        im = Image.new("RGB", (width, height), "white")
        # 使用何种字体以及字体大小
        font = ImageFont.truetype(font="arial.ttf", size=40)
        draw = ImageDraw.Draw(im)  # 新建生成对象
        # 绘制字符串
        for i in range(4):
            draw.text((5 + random.randint(-3, 3) + 23 * i, 5 + random.randint(-3, 3)), text=code[i],
                      fill=self.rand_color(), font=font)
        # 绘制干扰线
        self.draw_line(draw, 2, width, height)
        # im.show()
        return im, code

    # 获取图片与验证码
    def get_code(self):
        img, code = self.draw_verify_code()
        buf = BytesIO()
        img.save(buf, "jpeg")
        bstring = buf.getvalue()
        return code, bstring


# 发送邮件
def send_email(receiver, ecode, n):
    sender = emailAccount
    # 定义发送文件的内容
    # 判断是注册邮件还是找回密码的邮件
    if n == 1:
        content = f"<br/>欢迎注册博客，你的邮箱验证码为：<span style='color:red;font-size:20px;'>{ecode}</span>,请复制到注册窗口完成注册，感谢你的支持(验证码两分钟后失效)。<br/>"
    else:
        content = f"<br/>你此次找回密码的邮箱验证码为：<span style='color:red;font-size:20px;'>{ecode}</span>,请将验证码复制到指定位置完成操作(验证码两分钟后失效)<br/>"
    message = MIMEText(content, "html", "utf-8")
    # 指定邮件标题
    message["Subject"] = Header("博客验证码为", "utf-8")
    message["From"] = Header(f"Blog <{emailAccount}>", 'utf-8')  # 指定发件人信息
    message["To"] = Header(receiver, 'utf-8')  # 指定收件人邮箱地址
    message['Date'] = Header(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             'utf-8')  # 时间可以这么获取：datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    smtpObj = SMTP_SSL("smtp.qq.com", 465)
    smtpObj.login(user=emailAccount, password=emailAdmit)
    smtpObj.sendmail(sender, receiver, str(message))
    smtpObj.quit()


# 随机生成六位数的邮箱注册或找回密码的验证码
def gen_email_code():
    list = random.sample(string.ascii_letters + string.digits, 6)
    return "".join(list)


# SQLALchemy 连接查询的两张表转化为 [(),()] （操作连接查询和需要传给前台json数据时用的）
def model_join_list(result):
    list = []
    for obj1, obj2 in result:
        dict = {}
        for k1, v1 in obj1.__dict__.items():
            if not k1.startswith("_sa_instance_state"):
                if not k1 in dict:
                    dict[k1] = v1

        for k2, v2 in obj2.__dict__.items():
            if not k2.startswith("_sa_instance_state"):
                if not k2 in dict:
                    dict[k2] = v2
        list.append(dict)
    return list


# 单个模型类转化为python list数据
def model_list(result):
    list = []
    for row in result:
        dict = {}
        for k, v in row.__dict__.items():
            if not k.startswith("_sa_instance_state"):
                dict[k] = v
        list.append(dict)
    return list


# 压缩图片  将指定路径下的文件按照一定的压缩率保存到另一个文件夹
def compress_image(source, dest, width):
    from PIL import Image
    im = Image.open(source)
    x, y = im.size
    if x > width:
        ys = int(y * width / x)
        xs = width
        temp = im.resize((xs, ys), Image.ANTIALIAS)
        # 百分之80的压缩率
        temp.save(dest, quality=80)
    else:
        im.save(dest, quality=80)


# 解析文章中图片下载地址
def parser_image_url(content):
    import re
    temp_list = re.findall('<img src="(.+?)"', content)
    url_list = []
    for url in temp_list:
        # 如果图片为gif就不做任何处理
        if url.lower().endswith(".gif"):
            continue
        url_list.append(url)
    return url_list


# 下载远程图片到指定目录中
def download_image(url, dest):
    import requests
    response = requests.get(url)
    with open(file=dest, mode="wb") as file:
        file.write(response.content)


# 解析列表中的图片url并生成缩略图
def generate_thumb(url_list,userid):
    myPictureName = "myPic_" + str(userid)
    savePath=rootDir+"\\static\\img\\thumb"
    # 先要确定存在这个文件夹
    dirInDir(myPictureName,savePath)
    for url in url_list:
        if url.startswith(f"http://127.0.0.1:{portNum}/static/img/upload/{myPictureName}"):
            filename = url.split("/")[-1]
            picPathOld=f"{rootDir}\\static\\img\\upload\\{myPictureName}\\" + filename
            picPathNew=savePath+"\\"+myPictureName+"\\"+filename
            compress_image(picPathOld, picPathNew, 400)
            return myPictureName+"/"+filename
    # 如果在内容中没有找到本地图片，需要将网络图片下载到本地再处理
    # 直接将第一张图片作为缩略图，并生成基于时间戳的标准文件名
    savePath=rootDir+"\\static\\img\\download"
    dirInDir(myPictureName,savePath)
    url = url_list[0]
    thumbname = time.strftime("%Y%m%d_%H%M%S." + "jpg")
    download_image(url, savePath+"\\" +myPictureName+"\\"+ thumbname)
    compress_image(savePath+"\\" +myPictureName+"\\"+ thumbname, rootDir+"\\"+"static\\img\\thumb\\" +myPictureName +"\\"+thumbname, 400)
    userid=session.get('userid')
    info=f"userid为{userid}的用户，下载{url}图片，并将其缩率图并将其保存为thumb/{myPictureName}/{thumbname}"
    from database.instanceDatabase import instanceLog
    instanceLog.insert_detail(userid=userid,target=0,credit=0,info=info,type="下载保存缩略图成功")
    listLogger(userid,info,[8])
    return myPictureName+"/" +thumbname


# 设置获取时间
def getDatatimeStr():
    return datetime.now().strftime('%Y-%m-%d')


# 生成MD5
def genearteMD5(strlin):
    strlin = str(strlin)
    # 创建md5对象
    hl = md5()
    # Tips
    # 此处必须声明encode
    # 否则报错为：hl.update(str)    Unicode-objects must be encoded before hashing
    hl.update(strlin.encode(encoding='utf-8'))
    return hl.hexdigest()

# 获取访问当前端口的ip地址
def getIpForFlask():
    return str(request.remote_addr)
