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

import ipaddress
import random
import smtplib
import socket
import string
import time
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from hashlib import md5
from io import BytesIO
from pathlib import Path
from smtplib import SMTP_SSL
from urllib.parse import urlparse

import bleach
import requests
from flask import current_app, request
from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

from common.myLog import dirInDir, logDanger, rootDir
from constant import emailAccount, emailAdmit, emailType


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
        for _ in range(num):
            x1 = random.randint(0, width // 2)
            y1 = random.randint(0, height // 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height // 2, height)
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

@logDanger
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
    if emailType == "QQMAIL":
        smtpObj = SMTP_SSL("smtp.qq.com", 465)
    elif emailType == "GMAIL":
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
    else:
        raise Exception("Mail type USE_GMAIL_OR_QQMAIL error")
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
                if k1 not in dict:
                    dict[k1] = v1

        for k2, v2 in obj2.__dict__.items():
            if not k2.startswith("_sa_instance_state"):
                if k2 not in dict:
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
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.verify()
    with Image.open(source) as image:
        image = image.convert("RGB")
        if image.width > width:
            height = int(image.height * width / image.width)
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        image.save(dest, format="JPEG", quality=82, optimize=True)


def save_image_bytes(data, dest, max_bytes=5 * 1024 * 1024, max_width=1200):
    """Validate and re-encode untrusted image bytes as a safe JPEG."""
    if not data or len(data) > max_bytes:
        raise ValueError("Image is empty or exceeds the size limit")
    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()
        with Image.open(BytesIO(data)) as image:
            image = ImageOps.exif_transpose(image)
            if image.width < 1 or image.height < 1 or image.width * image.height > 40_000_000:
                raise ValueError("Image dimensions are invalid")
            image = image.convert("RGB")
            if image.width > max_width:
                height = max(1, int(image.height * max_width / image.width))
                image = image.resize((max_width, height), Image.Resampling.LANCZOS)
            destination = Path(dest)
            destination.parent.mkdir(parents=True, exist_ok=True)
            image.save(destination, format="JPEG", quality=82, optimize=True)
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as exc:
        raise ValueError("Uploaded file is not a valid image") from exc


_ARTICLE_TAGS = {
    "a", "abbr", "blockquote", "br", "code", "del", "div", "em", "figcaption", "figure",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img", "li", "ol", "p", "pre",
    "span", "strong", "sub", "sup", "table", "tbody", "td", "th", "thead", "tr", "u", "ul",
}
_ARTICLE_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan"],
    "*": ["class"],
}


def sanitize_article_html(content):
    return bleach.clean(
        content or "",
        tags=_ARTICLE_TAGS,
        attributes=_ARTICLE_ATTRIBUTES,
        protocols={"http", "https", "mailto"},
        strip=True,
        strip_comments=True,
    )


def sanitize_plain_text(content):
    """Remove markup from user-supplied text while preserving readable content."""
    return bleach.clean(content or "", tags=set(), attributes={}, strip=True, strip_comments=True).strip()


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
def _validate_public_http_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only public HTTP(S) image URLs are allowed")
    for address in socket.getaddrinfo(parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM):
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            raise ValueError("Private or reserved image hosts are not allowed")
    return parsed


def download_image(url, dest, max_bytes=5 * 1024 * 1024):
    _validate_public_http_url(url)
    with requests.get(url, stream=True, timeout=(3.05, 10), allow_redirects=False) as response:
        response.raise_for_status()
        if not response.headers.get("Content-Type", "").lower().startswith("image/"):
            raise ValueError("Remote resource is not an image")
        total = 0
        with open(dest, "wb") as output:
            for chunk in response.iter_content(64 * 1024):
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError("Remote image exceeds size limit")
                output.write(chunk)


# Parse the image url in the list and generate thumbnails
def generate_thumb(url_list, userid):
    myPictureName = "myPic_" + str(userid)
    savePath = rootDir + "\\static\\img\\thumb"
    # First, make sure this folder exists
    dirInDir(myPictureName, savePath)
    for url in url_list:
        parsed = urlparse(url)
        local_prefix = f"/static/img/upload/{myPictureName}/"
        if parsed.path.startswith(local_prefix):
            filename = Path(parsed.path).name
            picPathOld = str(Path(rootDir) / "static" / "img" / "upload" / myPictureName / filename)
            picPathNew = str(Path(savePath) / myPictureName / filename)
            if not Path(picPathOld).is_file():
                continue
            compress_image(picPathOld, picPathNew, 400)
            return myPictureName + "/" + filename

    if not current_app.config.get("ALLOW_REMOTE_IMAGES") or not url_list:
        return None
    download_dir = Path(rootDir) / "static" / "img" / "download" / myPictureName
    download_dir.mkdir(parents=True, exist_ok=True)
    thumbname = f"{time.strftime('%Y%m%d_%H%M%S')}.jpg"
    downloaded = download_dir / thumbname
    try:
        download_image(url_list[0], downloaded)
        target = Path(rootDir) / "static" / "img" / "thumb" / myPictureName / thumbname
        compress_image(downloaded, target, 400)
        return f"{myPictureName}/{thumbname}"
    except (OSError, ValueError, requests.RequestException):
        downloaded.unlink(missing_ok=True)
        return None


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
