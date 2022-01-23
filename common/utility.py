"""
File description.
This file puts some functions that are more general and can run independently
such as sending emails, generating compressed images, compressing images, generating encrypted conversion md5, etc.
Some public functions of the component part

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

from PIL import Image, ImageFont, ImageDraw
from flask import request, session

from common.myLog import listLogger
from common.myLog import rootDir, dirInDir
from constant import emailAdmit, emailAccount, portNum


# Generate verification code (with jamming line)
class ImageCode:
    #  Generate a random string
    def gen_text(self):
        list = random.sample(string.ascii_letters + string.digits, 4)
        return "".join(list)

    # Generate random colors
    def rand_color(self):
        red = random.randint(32, 200)
        green = random.randint(22, 255)
        blue = random.randint(0, 200)
        return red, green, blue

    # Draw interference lines
    def draw_line(self, draw, num, width, height):
        for num in range(num):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height / 2, height)
            draw.line(((x1, y1), (x2, y2)), fill="black", width=2)

    # Drawing captcha images
    def draw_verify_code(self):
        code = self.gen_text()
        width, height = 120, 50  # Set image size
        # Create an image object and set the background to white
        im = Image.new("RGB", (width, height), "white")
        # What font to use and the font size
        font = ImageFont.truetype(font=rootDir + "\\static\\font\\arial.ttf", size=40)
        draw = ImageDraw.Draw(im)  # New generated object
        # Draw string
        for i in range(4):
            draw.text((5 + random.randint(-3, 3) + 23 * i, 5 + random.randint(-3, 3)), text=code[i],
                      fill=self.rand_color(), font=font)
        # Draw interference lines
        self.draw_line(draw, 2, width, height)
        # im.show()
        return im, code

    # Get image and captcha
    def get_code(self):
        img, code = self.draw_verify_code()
        buf = BytesIO()
        img.save(buf, "jpeg")
        bstring = buf.getvalue()
        return code, bstring


# Send Email
def send_email(receiver, ecode, n):
    sender = emailAccount
    # Set the content of the sent file
    # Determine whether it is a registration email or a password recovery email
    if n == 1:
        content = f"<br/>Welcome to register for the blog, your email verification code is：<span style='color:red;font-size:20px;'>{ecode}</span>,Please copy to the registration window to complete the registration, thank you for your support (verification code expires after two minutes)<br/>"
    else:
        content = f"<br/>Your email verification code for this password retrieval is<span style='color:red;font-size:20px;'>{ecode}</span>,Please copy the verification code to the specified location to complete the operation (verification code expires after two minutes)<br/>"
    message = MIMEText(content, "html", "utf-8")
    # Specify the email title
    message["Subject"] = Header("The blog verification code is", "utf-8")
    message["From"] = Header(f"Blog <{emailAccount}>", 'utf-8')  # Specify sender information
    message["To"] = Header(receiver, 'utf-8')  # Specify the recipient's email address
    message['Date'] = Header(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             'utf-8')  # Time can be obtained this way：datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    smtpObj = SMTP_SSL("smtp.qq.com", 465)
    smtpObj.login(user=emailAccount, password=emailAdmit)
    smtpObj.sendmail(sender, receiver, str(message))
    smtpObj.quit()


# Generate a random six-digit verification code for email registration or password retrieval
def gen_email_code():
    list = random.sample(string.ascii_letters + string.digits, 6)
    return "".join(list)


# SQLALchemy The two tables of the join query are transformed into [(),()] (used when manipulating the join query and the json data that needs to be passed to the frontend)
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


# Convert a single model class to python list data
def model_list(result):
    list = []
    for row in result:
        dict = {}
        for k, v in row.__dict__.items():
            if not k.startswith("_sa_instance_state"):
                dict[k] = v
        list.append(dict)
    return list


# Compress images Save the files in the specified path to another folder with a certain compression rate
def compress_image(source, dest, width):
    from PIL import Image
    im = Image.open(source)
    im = im.convert('RGB')
    x, y = im.size
    if x > width:
        ys = int(y * width / x)
        xs = width
        temp = im.resize((xs, ys), Image.ANTIALIAS)
        # 80 percent compression rate
        temp.save(dest, quality=80)
    else:
        im.save(dest, quality=80)


# Parse the image download address in the article
def parser_image_url(content):
    import re
    temp_list = re.findall('<img src="(.+?)"', content)
    url_list = []
    for url in temp_list:
        # If the image is a gif then nothing is done
        if url.lower().endswith(".gif"):
            continue
        url_list.append(url)
    return url_list


# Download remote images to the specified directory
def download_image(url, dest):
    import requests
    response = requests.get(url)
    with open(file=dest, mode="wb") as file:
        file.write(response.content)


# Parse the image url in the list and generate thumbnails
def generate_thumb(url_list, userid):
    myPictureName = "myPic_" + str(userid)
    savePath = rootDir + "\\static\\img\\thumb"
    # First, make sure this folder exists
    dirInDir(myPictureName, savePath)
    for url in url_list:
        if url.startswith(f"http://127.0.0.1:{portNum}/static/img/upload/{myPictureName}"):
            filename = url.split("/")[-1]
            picPathOld = f"{rootDir}\\static\\img\\upload\\{myPictureName}\\" + filename
            picPathNew = savePath + "\\" + myPictureName + "\\" + filename
            compress_image(picPathOld, picPathNew, 400)
            return myPictureName + "/" + filename
    # If no local image is found in the content, you need to download the network image to local and process it again
    # Directly use the first image as a thumbnail and generate a standard file name based on the timestamp
    savePath = rootDir + "\\static\\img\\download"
    dirInDir(myPictureName, savePath)
    url = url_list[0]
    thumbname = time.strftime("%Y%m%d_%H%M%S." + "jpg")
    download_image(url, savePath + "\\" + myPictureName + "\\" + thumbname)
    compress_image(savePath + "\\" + myPictureName + "\\" + thumbname,
                   rootDir + "\\" + "static\\img\\thumb\\" + myPictureName + "\\" + thumbname, 400)
    userid = session.get('userid')
    info = f"userid is {userid}, download the {url} picture, and thumbnail it and save it as thumb/{myPictureName}/{thumbname}"
    from database.logs import Log
    instanceLog = Log()
    instanceLog.insertDetail(userid=userid, target=0, credit=0, info=info,
                             type="Download and save thumbnails successfully")
    listLogger(userid, info, [8])
    return myPictureName + "/" + thumbname


# Set the acquisition time
def getDatatimeStr():
    return datetime.now().strftime('%Y-%m-%d')


# Generate MD5
def genearteMD5(strlin):
    strlin = str(strlin)
    # Create md5 objects
    hl = md5()
    # Tips
    # This must be declared here encode
    # Otherwise the error is reported as:hl.update(str)    Unicode-objects must be encoded before hashing
    hl.update(strlin.encode(encoding='utf-8'))
    return hl.hexdigest()


# Get the ip address to access the current port
def getIpForFlask():
    return str(request.remote_addr)
