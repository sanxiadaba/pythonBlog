"""站点配置。想改标题、分类、文案，改这里就够了。"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "img" / "upload"

SITE_NAME = "三夏的博客"
SITE_DESCRIPTION = "Python、LeetCode 和一些折腾记录"
AUTHOR = "张佳俊"
EMAIL = "jz272381@gmail.com"

# 键会出现在 URL 里（/?c=python），值是页面上显示的名字。
CATEGORIES = {
    "python": "Python",
    "leetcode": "LeetCode",
    "project": "项目",
    "learning": "学习笔记",
}

PAGE_SIZE = 10
COMMENT_MAX_LENGTH = 1000
NICKNAME_MAX_LENGTH = 30
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
