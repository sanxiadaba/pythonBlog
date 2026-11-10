# pythonBlog

个人博客：Markdown 写文章，访客可以评论，一个管理员，SQLite 存数据。

## 功能

- 首页列表、分类浏览、标题/正文搜索、分页
- Markdown 文章页，代码高亮，表格、引用、图片
- 游客填昵称即可评论，带限流；后台可隐藏或删除
- 后台：写文章（实时预览、插图上传）、发布/隐藏、删除、评论管理
- 密码用 scrypt 哈希，全站 CSRF 与安全响应头

## 启动

需要 Python 3.11+ 和 [uv](https://docs.astral.sh/uv/)。

```powershell
uv sync
Copy-Item .env.example .env      # 只有 DEBUG_MODE 需要关心
uv run flask --app app create-admin
uv run flask --app app run --debug
```

打开 <http://127.0.0.1:5000>，后台在 `/admin`。数据库自动建在 `instance/blog.db`。

不想用 `uv run` 也可以直接跑脚本：`.\scripts\start.ps1 -Port 5000`（`-Mode prod` 用 waitress 常驻）。

## 日常

- **写文章**：后台 → 文章 → 写文章。正文是 Markdown，Ctrl+S 保存。
- **配图**：编辑器里点「插入图片」，图片会自动压缩并改成随机文件名。
- **改站点信息**：`config.py` 里改站名、简介、分类、邮箱。
- **忘了密码**：重跑 `uv run flask --app app create-admin`，输入同名账号会重置密码。
- **备份**：拷走 `instance/blog.db` 和 `static/img/upload/`。

## 结构

```text
app.py         应用工厂、安全响应头、CLI
config.py      站名、分类、分页等配置
models.py      文章、评论、管理员三张表
utils.py       Markdown 渲染、密码哈希、图片处理、日志
routes/        访客页与后台路由
templates/     Jinja 模板
static/        CSS、JS、highlight.js/marked、上传的图片
tests/         pytest
```

## 检查

```powershell
uv run pytest
uv run ruff check .
```

CI 在 `.github/workflows/ci.yml`，每次 push 跑一遍上面两条。
