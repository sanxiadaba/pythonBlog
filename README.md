# pythonBlog

这是一个 Flask 个人博客。原作者的目标是用一个完整但容易理解的项目演示用户、文章、审核、评论、收藏、积分、图片上传和后台管理。当前版本保留了原页面和主要交互，并完成了 Python 3.11+、Flask 3、SQLAlchemy 2 和 SQLite/MySQL 的现代化适配。

## 已完成的改造

- 应用工厂 `create_app()`，配置与扩展解耦。
- 默认零配置 SQLite；可通过 `DATABASE_URL` 切换 MySQL。
- `pyproject.toml` + `uv.lock` 管理和锁定依赖，自动创建项目内 `.venv`。
- Alembic 数据库迁移、初始化与用户创建 CLI。
- scrypt 密码哈希；旧 MD5 密码在成功登录后自动升级。
- 管理员 RBAC、文章所有权、登录状态和封禁状态服务端校验。
- 全站 CSRF、接口限流、安全响应头和生产密钥检查。
- 文章 HTML 白名单清洗；付费正文未购买前不会下发到浏览器。
- 图片真实格式、大小、像素数、随机文件名和重新编码校验。
- SQLite/MySQL 时间类型和随机排序兼容。
- pytest 回归测试和 Ruff 静态检查。

## 环境要求

- Python 3.11 或更高版本。`uv` 会选择可用解释器并管理虚拟环境。
- [uv](https://docs.astral.sh/uv/)
- MySQL 仅在使用 MySQL 部署时需要；本地开发不需要。

## 首次启动

在项目目录执行：

```powershell
Copy-Item .env.example .env
uv sync --frozen
uv run flask --app app init-db
uv run flask --app app create-user --username admin@example.com --role admin --nickname admin
uv run flask --app app run --debug
```

打开 <http://127.0.0.1:5000>。数据库默认位于 `instance/pythonblog.db`，虚拟环境位于 `.venv`。`uv run` 会自动使用该虚拟环境，不需要手动激活；需要激活时可执行：

```powershell
.\.venv\Scripts\Activate.ps1
```

也可以使用启动脚本：

```powershell
.\scripts\start.ps1 -Mode development -Port 5000
```

## 配置

`.env.example` 包含可用配置。至少应在非开发环境设置一个随机 `SECRET_KEY`：

```powershell
uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
```

关键变量：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `SECRET_KEY` | 仅开发占位值 | 会话与 CSRF 签名密钥，生产环境必须修改 |
| `DATABASE_URL` | 空 | 空值使用 SQLite；支持 SQLAlchemy 数据库 URL |
| `AUTO_INIT_DB` | `True` | 启动时补建缺失表；迁移管理的生产环境建议设为 `False` |
| `DEBUG_MODE` | `True` | 生产环境必须关闭 |
| `SESSION_COOKIE_SECURE` | `False` | HTTPS 部署时设为 `True` |
| `MAX_CONTENT_LENGTH_MB` | `8` | 单次请求上限 |
| `ALLOW_REMOTE_IMAGES` | `False` | 是否允许抓取公网文章图片，默认关闭以规避 SSRF |
| `RATELIMIT_STORAGE_URI` | `memory://` | 单进程限流存储；多实例部署应改为共享存储 |

邮件注册和找回密码需要设置 `EMAIL_ACCOUNT`、`EMAIL_PASSWORD` 和 `USE_GMAIL_OR_QQMAIL`。`EMAIL_PASSWORD` 应填写邮箱服务商生成的应用授权码，而不是登录密码。

## 数据库

本地开发直接使用 SQLite。使用 MySQL 时，先创建空数据库和低权限应用账号，再配置：

```dotenv
DATABASE_URL=mysql+pymysql://blog_user:password@127.0.0.1:3306/python_blog?charset=utf8mb4
```

新生产数据库建议使用迁移创建：

```powershell
$env:AUTO_INIT_DB="False"
uv run flask --app app db upgrade
```

修改 `common/schema.py` 后生成迁移并检查内容：

```powershell
uv run flask --app app db migrate -m "describe change"
uv run flask --app app db upgrade
uv run flask --app app db check
```

接入已有数据库前必须先备份。若现有表结构已经与初始迁移完全一致，应审查后使用 `flask db stamp head` 建立版本标记，不要直接重复建表。

## 生产启动

`.env` 中设置强随机 `SECRET_KEY`、`DEBUG_MODE=False`，并在 HTTPS 下设置 `SESSION_COOKIE_SECURE=True`。Windows 可使用 Waitress：

```powershell
.\scripts\start.ps1 -Mode production -Port 8000
```

脚本只监听 `127.0.0.1`。对外服务应在前面配置 IIS、Nginx 或 Caddy，负责 HTTPS、访问日志和静态资源缓存。生产脚本使用 `uv sync --no-dev`，不会安装测试工具。

## 包管理

`pyproject.toml` 是直接依赖和工具配置的来源，`uv.lock` 是可复现安装的唯一锁文件，二者都应提交。常用命令：

```powershell
uv add package-name
uv add --dev package-name
uv lock --upgrade
uv sync --frozen
```

`requirements.txt` 仅用于不支持 uv 的兼容环境，由锁文件生成，不应手工改版本：

```powershell
uv export --frozen --no-dev --no-hashes --no-emit-project --output-file requirements.txt
```

## 质量检查

```powershell
uv run pytest
uv run ruff check .
uv run flask --app app routes
```

当前测试覆盖应用启动、首页、权限与角色、文章所有权、审核状态、HTML 清洗、CSRF 和旧密码迁移。

## 目录

```text
app.py                 应用工厂、扩展注册、错误处理和 CLI
common/                配置无关的安全、认证、日志与工具函数
controler/             兼容原项目命名的路由控制器
database/              兼容原业务调用的数据访问层
migrations/            Alembic 数据库迁移
templates/             Jinja 页面模板
static/                前端资源与运行时上传目录
tests/                 回归测试
scripts/start.ps1      开发/生产启动脚本
pyproject.toml         直接依赖与工具配置
uv.lock                完整锁定依赖
```

## 仍需注意

前端仍使用较旧的 Bootstrap、jQuery 和 UEditor，已经在服务端补上安全边界，但后续若重做界面，优先替换 UEditor 和旧前端依赖。邮件发送与部分日志写入仍是同步操作，高流量部署应迁移到任务队列和结构化集中日志。多实例部署不能继续使用内存限流存储。
