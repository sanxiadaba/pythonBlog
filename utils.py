"""不依赖 Flask 的小工具：Markdown 渲染、密码哈希、图片处理、日志。"""

import hashlib
import html
import logging
import re
import secrets
from io import BytesIO
from logging.handlers import RotatingFileHandler
from pathlib import Path

import mistune
from mistune.renderers.html import HTMLRenderer
from PIL import Image, ImageOps, UnidentifiedImageError
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers.special import TextLexer
from pygments.util import ClassNotFound

_TAG_RE = re.compile(r"<[^>]+>")
_NOISE_RE = re.compile(r"<(?:pre|table)\b.*?</(?:pre|table)>", re.S | re.I)
_SPACE_RE = re.compile(r"\s+")
_SCRYPT = {"n": 2**14, "r": 8, "p": 1}

# 代码块在保存时就高亮成静态 HTML，页面不需要下载任何高亮脚本。
_CODE_FORMATTER = HtmlFormatter(cssclass="highlight")


def _render_code(code: str, lang: str) -> str:
    try:
        lexer = get_lexer_by_name(lang, stripnl=False) if lang else TextLexer()
    except ClassNotFound:
        lexer = TextLexer()
    return highlight(code, lexer, _CODE_FORMATTER)


class _Renderer(HTMLRenderer):
    def block_code(self, code: str, info: str | None = None) -> str:
        # 围栏后面的第一个词是语言名，`python title="x"` 这种也认。
        return _render_code(code, info.split(None, 1)[0] if info else "")


_markdown = mistune.create_markdown(
    escape=True,
    renderer=_Renderer(escape=True),
    plugins=["strikethrough", "table", "url"],
)


def render_markdown(text: str) -> str:
    """Markdown 转 HTML。escape=True 让正文里的原始 HTML 失效，不需要再做白名单清洗。"""
    return _markdown(text or "")


def make_summary(html_text: str, limit: int = 150) -> str:
    """从渲染后的 HTML 里抽一段纯文本当摘要。代码块和表格读起来是噪音，先扔掉。"""
    text = _NOISE_RE.sub(" ", html_text or "")
    text = html.unescape(_SPACE_RE.sub(" ", _TAG_RE.sub(" ", text))).strip()
    return text[:limit] + "…" if len(text) > limit else text


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, dklen=32, **_SCRYPT)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt, digest = (stored or "").split("$")
        if scheme != "scrypt":
            return False
        computed = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), dklen=32, **_SCRYPT)
    except (ValueError, TypeError):
        return False
    return secrets.compare_digest(computed.hex(), digest)


def _to_rgb(image: Image.Image) -> Image.Image:
    """转 RGB；带透明通道的图先铺白底，否则透明区域会变成黑块。"""
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        canvas = Image.new("RGB", rgba.size, (255, 255, 255))
        canvas.paste(rgba, mask=rgba.getchannel("A"))
        return canvas
    return image.convert("RGB")


def save_image(data: bytes, directory: Path, max_bytes: int, max_width: int = 1600) -> str:
    """把上传的图片重新编码成 JPEG 后存盘，返回文件名。

    重新编码既是格式校验，也顺手抹掉 EXIF（手机照片里的定位）和尾部附加数据。
    """
    if not data or len(data) > max_bytes:
        raise ValueError("图片为空或超过大小限制")
    try:
        with Image.open(BytesIO(data)) as probe:
            probe.verify()
        with Image.open(BytesIO(data)) as image:
            image = ImageOps.exif_transpose(image)
            if image.width < 1 or image.height < 1 or image.width * image.height > 40_000_000:
                raise ValueError("图片尺寸不合法")
            image = _to_rgb(image)
            if image.width > max_width:
                height = max(1, round(image.height * max_width / image.width))
                image = image.resize((max_width, height), Image.Resampling.LANCZOS)
            directory.mkdir(parents=True, exist_ok=True)
            name = f"{secrets.token_hex(8)}.jpg"
            image.save(directory / name, format="JPEG", quality=85, optimize=True)
            return name
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as exc:
        raise ValueError("不是有效的图片文件") from exc


def setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        root.addHandler(handler)
