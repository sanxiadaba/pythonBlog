# pythonBlog 代码审查报告

> 审查日期：2026-11-10 ｜ 目标：Windows 本机（SQLite）演示/学习 ｜ 方式：静态审计 + 真实安装依赖、跑测试、起服务、逐条复现

---

## 0.0 修复已落地（2026-11-10，共 3 个 commit）

`0e63d7b` 修坏掉的功能与密钥守卫；`2ad267a` 把验证码搬到服务端、把 Alembic 变成唯一 schema 来源、给写接口补限流。
全部经实测：`pytest` **12 passed**、`ruff` **0 error**、空库 `flask db upgrade` 成功且 `flask db check` 无差异。

### 第一轮：坏功能与密钥（9 文件，+39 / −30）

| 修复项 | 改动 | 验证 |
| --- | --- | --- |
| P0-3 回复评论 | `database/comment.py` 删 `updatetime=now` 与无效的 `info = info` | `POST /reply -> reply-pass`，评论行数 1 → 2 |
| P0-4 用户中心 500 | `database/favorite.py` 删副本 `Article` 类，改从 `database.article` 导入 | 带 1 条收藏 `GET /userManage -> 200` |
| P0-5 常量污染 | `controler/adminManage.py` 改用局部字符串，不再就地改写常量 | 后台后 `creditListForReleaseArticle == [1,2,5,10,20,50]`；`POST /article credit=1 -> 200` |
| P0-2 弱密钥 | `app.py` 弱密钥集合 + 长度 ≥32 校验；`.env.example` 的 `SECRET_KEY` 置空 | 占位值 → `RuntimeError`；随机 40 字符 → 正常启动 |
| 取消收藏无效 | `controler/favorite.py` 删多余的 `insertFavorite`；`cancelFavorite` 返回布尔并防 None | `DELETE /favorite/<id>` 后 `canceled == 1` |
| 昵称保存 | `templates/userManage.html:53` 改 `\|tojson` + 单引号属性 | 渲染为 `onclick='modifyNickname(this,"owner")'` |
| 评论时间空白 | `templates/article.html:248,325` `createment` → `createtime` | 文章页渲染出时间戳 |
| 搜索缩略图 | `templates/search.html:40` 补 `/thumb` | 与 index/type 页路径一致 |

**行为变更**：`SECRET_KEY` 未配置时，`DEBUG`/`TESTING` 自动生成进程内随机密钥（重启后登录态失效），`DEBUG=False` 直接启动失败。`scripts/start.ps1 -Mode production` 现在会明确拒绝无密钥启动。

### 第二轮：验证码、迁移基线、限流

| 项 | 改动 | 验证 |
| --- | --- | --- |
| P0-1 账号接管 | 新增 `one_time_code` 表 + `common/oneTimeCode.py`；验证码只存 SHA-256，会话里只有不透明 `email_token` / `captcha_token`；用后即删、5 次锁定、2 分钟过期 | cookie 里 `code material: []`；拿 cookie 内容去重置密码 → `ecode-error` |
| 图形码可读 | `/vcode` 同样走服务端存储，登录时消费一次 | 同一验证码第二次登录 → `vcode-error` |
| 密码重置不失效旧会话 | `users.session_version` + `before_request` 比对；重置时 bump | 重置后旧 cookie 访问 `/userManage` → **403**，新密码登录 → 200 |
| 迁移基线 | `AUTO_INIT_DB` 默认改 `False`；删 `myBlog.sql`；README 首启改 `flask db upgrade`；新增迁移 `9f1c2b7a4d10` | 空库 upgrade 通过；`db check` 无差异 |
| 写接口裸奔 | `/article`、`/comment`、`/reply`、`/favorite`、上传、`/uedit` 补 `@limiter.limit` | 测试中 `RATELIMIT_ENABLED=False`，路由正常 |
| 上传到顶 500 | `ueditor.py` `listLogger(..., 8)` → `[8]` | — |
| 5–8 MB 图判为非法 | 按 `MAX_CONTENT_LENGTH` 读取，不再硬编码 5 MB | — |
| 图片绝对地址 | UEditor 的 `*UrlPrefix` 置空，返回 `/static/img/upload/...` | 换端口/换机器不再失效 |
| 修改限额失效 | `articleLog.py` 用 `MODIFY_TYPES` 常量匹配实际写入的类型 | — |
| 每日登录分漏发 | `whetherFirstLoginThisDay` 加 `category` 过滤 | — |
| 收藏日志发错人 | 作者通知改用 `userid=authorid`，文案由 "unfavored" 改 "favorited" | — |
| 回复删除删错对象 | `article.html:331` 传 `reply.commentid` 并同步权限判断 | — |
| 评论分页少一页 | `range(1,total)` → `range(1,total+1)` | — |
| SQLite 并发 | `busy_timeout=30000`、`journal_mode=WAL`；`is_sqlite` 改由最终 URI 判定 | — |
| 热查询缺索引 | `comment(userid,createtime)`、`favorite(userid,canceled)`、`log(category,target)` | `db check` 通过 |

### 第三轮：收尾加固（commit `2ae8d7a`）

| 项 | 改动 | 验证 |
| --- | --- | --- |
| 评论页 N+1 | `searchCommentWithUser` 改为一次 `replyid IN (...)` 批量取回复 | 文章页 200，回复正确渲染 |
| 反代取 IP | `TRUST_PROXY_HOPS` 环境变量，>0 时启用 `ProxyFix`（默认 0，避免伪造 XFF） | 配置项已文档化 |
| 安全头补全 | `SESSION_COOKIE_SECURE=True` 时加 HSTS；已登录的 HTML 响应加 `Cache-Control: no-store` | HSTS 与 no-store 实测出现 |
| 外链安全 | 文章 HTML 清洗后给 `<a>` 补 `rel="noopener noreferrer"` | 新增断言通过 |
| 标题编码 | `write.html` 的 `headline` 改 `encodeURIComponent`（`&`/`+` 不再截断正文） | — |
| 上传页 jQuery | `uploadUserAvatar.html` 从 1.11.1 换到 3.5.1 | 静态资源存在 |
| 启动脚本 | `scripts/start.ps1` 启动前自动 `flask db upgrade`（AUTO_INIT_DB 已默认关闭） | — |
| 死接口 | 删除永不生效的 `/userInfo`（`jsonify` 用法本身就是错的） | ruff 干净 |

回归：`pytest` **16 passed**（新增回复落库、取消收藏、收藏后个人中心、后台后付费发文、重置失效会话、验证码单次可用、cookie 不含验证码等用例），`ruff` 0 error。

### 仍未做

- `.env` 历史泄露的口令**轮换**。仓库的 `origin` 指向 `github.com/sanxiadaba/pythonBlog`，改写历史需要 force-push 上游，属于破坏性操作且有外溢风险，我没有动；正确做法是轮换那些口令，必要时由仓库所有者自行 `git filter-repo`。
- 共享限流存储（多实例）、CSP 去掉 `unsafe-inline`（需先把上百个 `onclick` 迁走）、UEditor / Bootstrap 双版本替换。
- 事务边界重构（每条 DAO 仍各自 commit）、其余 N+1、`userManage` 表格列数这类前端细节。
- MySQL 未实测（本机无服务端）。

---

## 0. 一句话结论

**能启动，不能算能用。**

- 实测可跑：Python 3.14.4 + `requirements.txt` 装依赖 → waitress 起服务，`/`、`/healthz`、静态资源、品牌 404 全部正常；现在 `pytest` **12 passed**、`ruff` 0 error。
- 审查时发现 **5 个 P0**：任意账号接管（含管理员）、回复评论 100% 失败、收藏过文章的用户中心直接 500、管理员看过后台后全进程付费发文 400、公开占位密钥可绕过生产校验。**这 5 个已在本次修复中全部关闭**（见 0.0 节，commit `0e63d7b` / `2ad267a`）。
- 纵向看，这个仓库的"骨架"是好的（应用工厂、Alembic、CSRF、HTML 清洗、图片重编码、回归测试都在），修完 P0 后可作为本机/内网项目继续用；**公网部署前仍需处理限流、HTTPS、CSP 与口令轮换**。

---

## 1. 我实测了什么

| 动作 | 结果 |
| --- | --- |
| 新建 venv + `pip install -r requirements.txt`（Python 3.14.4） | 成功，无编译失败 |
| `flask --app app routes` | 40+ 条路由正常注册 |
| `pytest`（`tests/`） | 审查时 **7 passed**；补齐回归后 **16 passed** |
| `ruff check .` | **All checks passed** |
| `waitress-serve --call app:create_app` | `/healthz` 200、`/` 200（16.9 KB，title=Blog Home）、`/nope` 404、`/article/999999` 404、`/static/css/...` 200 |
| `flask db upgrade`（默认 `AUTO_INIT_DB=True`） | **失败**：`table log already exists`，且不写 `alembic_version` |
| `POST /ecode`（未配邮箱） | **500** `SMTPServerDisconnected` |
| `POST /reply`（回复评论） | **`reply-fail`**，评论数 1 → 1 |
| 收藏 → 取消收藏 | 返回 `cancel-pass`，但库里 `canceled` 仍为 0 |
| 带 1 条收藏访问 `/userManage` | **500**（AttributeError） |
| 访问 `/adminManage` 后 `POST /article credit=1` | **400**（常量被就地改成字符串） |
| 用公开占位密钥签管理员会话 → `/adminManage` | **200** |
| 从自己的 cookie 读出验证码 → 重置他人密码 | **成功登录受害者账号** |

环境事实（影响"怎么跑"）：本机**没有 uv**、没有 `.env`、没有 `.venv`；`README` 的第一步在这台机器上会直接失败（`scripts/start.ps1:11` 会 `throw`）。

---

## 2. 这个仓库怎么用

### A. 不装 uv（本机实测可用）

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:SECRET_KEY = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 48 | ForEach-Object { [char]$_ })
.\.venv\Scripts\python.exe -m flask --app app init-db
.\.venv\Scripts\python.exe -m flask --app app create-user --username admin@example.com --role admin
.\.venv\Scripts\python.exe -m waitress --host=127.0.0.1 --port=5000 --call app:create_app
```

两个坑：
- `create-user` 的密码是**交互式** prompt（`app.py:223`），命令行传不了；README:33 那条命令会停在输入密码 + 确认。
- `AUTO_INIT_DB` 默认 `True`，`create_app()` 已经 `create_all()`，所以 `init-db` 其实多余；但**恰恰是这个默认值让 `flask db upgrade` 用不了**（见 P1-2）。

### B. 按 README 走 uv

```powershell
winget install astral-sh.uv        # 或 pip install uv
Copy-Item .env.example .env
uv sync --frozen
uv run flask --app app create-user --username admin@example.com --role admin
uv run flask --app app run --debug
```

`uv` 路径本次**未验证**（机器上没有 uv，你选了不装）；`requirements.txt` 与 `uv.lock` 出自同一次导出，依赖版本本身一致。

### 功能前提

- 默认 SQLite：`instance/pythonblog.db`（首次启动自动建）；MySQL 用 `DATABASE_URL` 切。
- **注册 / 找回密码必须先配 SMTP**（`EMAIL_ACCOUNT` + `EMAIL_PASSWORD` 用授权码），否则 `/ecode` 直接 500。不想配就只用 `create-user` CLI 建号。
- 上传缩略图要 `static/img/...` 可写。

---

## 3. 缺陷清单

### P0 — 阻断或可利用（全部已复现）

**P0-1 任意账号接管，包括管理员** — `controler/user.py:85`

Flask 默认 session 是**签名、不加密**的 cookie。`/ecode` 把 6 位验证码**明文**写进调用者自己的 session：

```python
session.update(ecode=code, ecode_email=email, ecode_issued_at=time.time())   # user.py:85
```

攻击链：`POST /ecode email=victim n=2` → 解自己的 cookie 拿码 → `POST /resetUserPassword username=victim&ecode=<码>&password=...`。全程不碰受害者邮箱。

实测（把 SMTP 调用 stub 掉以模拟已配置邮箱的部署）：`attacker sees ecode: IrUpGt for email: a@example.com` → `reset victim -> fi-pass` → 用新密码 `login -> add-credit`。
同一根因让图形验证码也可读（`user.py:65`），登录验证码还能无限复用（`:149` 比较后不清理）。

修复（唯一"大改"，需要一次迁移）：

```python
# common/schema.py
Table("email_code", metadata,
      Column("email", String(254), primary_key=True),
      Column("purpose", Integer, primary_key=True),
      Column("code_hash", String(64), nullable=False),
      Column("expires_at", DateTime, nullable=False),
      Column("attempts", Integer, nullable=False, server_default="0"))

# common/auth.py
def save_email_code(email, purpose, code, ttl=120):
    dbsession.merge(EmailCode(email=email, purpose=purpose,
                              code_hash=hashlib.sha256(code.encode()).hexdigest(),
                              expires_at=datetime.now() + timedelta(seconds=ttl), attempts=0))
    dbsession.commit()

def consume_email_code(email, purpose, code):
    row = dbsession.get(EmailCode, (email, purpose))
    if row is None or row.expires_at < datetime.now() or row.attempts >= 5:
        return False
    ok = hmac.compare_digest(row.code_hash, hashlib.sha256(code.encode()).hexdigest())
    row.attempts += 1
    if ok:
        dbsession.delete(row)
    dbsession.commit()
    return ok
```

然后 `user.py` 的 `/ecode` 改成 `save_email_code(...)`，`_email_code_valid` 改成 `consume_email_code(...)`，**session 里不再放任何秘密**。图形验证码同理（或干脆去掉——注册/找回都不靠它）。

**P0-2 公开占位密钥能过"生产密钥检查"** — `app.py:49,73-74` + `.env.example:2`

守卫只拦字面量 `dev-only-change-me`；`.env.example` 给的是 `replace-with-a-random-secret`，而 README:30 让你原样复制。于是 `DEBUG_MODE=False` 也照样启动，密钥却是公开值。

实测：拿该值签 `{"islogin":"true","userid":3,"role":"admin"}` 的 cookie → `GET /adminManage` **200**。

```diff
-    secret_key = os.getenv("SECRET_KEY", "dev-only-change-me")
+    secret_key = os.getenv("SECRET_KEY", "").strip()
+    weak_keys = {"", "dev-only-change-me", "replace-with-a-random-secret", "changeme"}
...
-    if not app.config.get("TESTING") and not app.config["DEBUG"] and secret_key == "dev-only-change-me":
+    if not app.config.get("TESTING") and not app.config["DEBUG"] and (
+        app.config["SECRET_KEY"] in weak_keys or len(app.config["SECRET_KEY"]) < 32
+    ):
         raise RuntimeError("SECRET_KEY must be configured outside development")
```

同时把 `.env.example` 的 `SECRET_KEY=` 留空并写清生成命令。

**P0-3 回复评论 100% 失败** — `database/comment.py:82`

```python
Comment(..., createtime=now, updatetime=now, info=info)   # comment 表没有 updatetime 列
```

`common/schema.py:60-75` 里 `comment` 只有 `createtime`。SQLAlchemy 抛 `TypeError`，被 `controler/comment.py:117-120` 吞掉返回 `reply-fail`——没有回复、没有积分、没有日志。

实测：`POST /reply -> reply-fail`，评论数不变。

```diff
-        if info is not None:
-            info = info
         now = datetime.now()
         comment = Comment(userid=session.get("userid"), articleid=articleid, content=content, ipaddr=ipaddr,
-                          replyid=commentid, createtime=now, updatetime=now, info=info)
+                          replyid=commentid, createtime=now, info=info)
```

**P0-4 收藏过文章的用户，个人中心必 500** — `database/favorite.py:78`

该文件自己复制了一份 `Article`（`:10-19`），方法叫 `searchHeadlineByArticleId`；`:78` 调的是 `searchHeadlineByArticleid`。零收藏时循环不执行 → 200，所以看起来"偶发"。

实测：`GET /userManage with 1 favorite -> 500`。

```diff
-class Article(DBase):
-    __table__ = md.tables["article"]
-
-    def searchHeadlineByArticleId(self, articleid):
-        row = dbsession.query(Article.headline).filter_by(articleid=articleid).first()
-        return row.headline
-instanceArticle = Article()
+from database.article import Article      # 顶部
+instanceArticle = Article()
```

（`database/article.py:203` 已有同名方法，`controler/userManage.py:115` 也依赖它。）

**P0-5 管理员打开一次后台，全进程付费发文就废了** — `controler/adminManage.py:78-81`

为了拼展示字符串，**就地**把常量列表从 int 改成 str：

```python
for i in range(len(creditListForReleaseArticle)):
    creditListForReleaseArticle[i] = str(creditListForReleaseArticle[i])
```

`controler/article.py:224` 随后判 `credit not in {0, *creditListForReleaseArticle}`，int 永远不匹配 → `abort(400)`。进程内一直坏到重启。

实测：访问 `/adminManage` 后 `creditListForReleaseArticle == ['1','2','5','10','20','50']`，`POST /article credit=1 -> 400`。

```diff
-    for i in range(len(creditListForReleaseArticle)):
-        creditListForReleaseArticle[i] = str(creditListForReleaseArticle[i])
-    for i in range(len(recommendedNumOfSide)):
-        recommendedNumOfSide[i] = str(recommendedNumOfSide[i])
+    credit_text = " ".join(str(i) for i in creditListForReleaseArticle)
+    side_text = " ".join(str(i) for i in recommendedNumOfSide)
...
-    webInfo["creditListForReleaseArticle"] = " ".join(creditListForReleaseArticle)
+    webInfo["creditListForReleaseArticle"] = credit_text
-    webInfo["recommendedNumOfSide"] = " ".join(recommendedNumOfSide)
+    webInfo["recommendedNumOfSide"] = side_text
```

### P1 — 功能坏 / 上线前必修

1. **取消收藏无效** — `controler/favorite.py:75-77`：先 `cancelFavorite()` 又 `insertFavorite()`，后者把同一行 `canceled` 改回 0（实测 `cancel-pass` 但 `canceled=0`）。删掉 `:77` 即可；顺带给 `cancelFavorite` 加 `row is None` 保护（现在未收藏时 `AttributeError`）。
2. **`flask db upgrade` 与默认配置冲突** — `app.py:69,90-91`：默认 `AUTO_INIT_DB=True` → `create_all()` 抢先建表，Alembic 随后撞 `table log already exists`，`alembic_version` 永远为空。把默认改 `False`，首启走 `flask db upgrade`（README:83 已经是这条路）。
3. **历史 `.env` 泄露真实口令** — `git show 2e80bb7:.env` 可读到 `MYSQL_PASSWORD`、`ADMIN/EDITOR/USER_PASSWORD`、`EMAIL_PASSWORD`。当前文件已删，但历史还在：必须**轮换**这些口令，并 `git filter-repo` 清历史；只删文件没有意义。
4. **`myBlog.sql` 已不可用** — `password varchar(32)`（schema 是 255，scrypt 约 160 字符，注册必截断）、`favorite` 缺 `updatetime`、无外键/唯一键、`articlelog` 与 `articleLog` 大小写不一致。建议直接删，迁移是唯一真源。
5. **没有事务边界** — `database/credit.py`、`controler/comment.py:60-64` 每步各自 `commit()`：中途失败就是"扣了分没文章/评论数虚高"。做法：DAL 只 `flush()`，控制器入口开事务、出口一次 `commit()`、异常 `rollback()`。
6. **限流名不副实** — 只有 5 个端点有 `@limiter.limit`（`user.py:61,73,91,119,138`）；发文、评论、收藏、上传、搜索全裸。且 `get_remote_address` 无 `ProxyFix`（`extensions.py:10`），上反代后所有客户端共享一个桶。
7. **上传次数到顶 → 500 而不是提示** — `controler/ueditor.py:75` 写 `listLogger(userid, info, 8)`，`common/myLog.py:174-177` 直接 `for logNum in 8`。改 `[8]`。
8. **前端 4xx 全静默** — `static/js/myFunction.js` 里 `.fail(` 数量为 0；密码错（401）、验证码错（400）、邮箱重复（409）用户看不到任何反馈。
9. **评论时间全空** — `templates/article.html:248,325` 写的是 `comment.createment`，数据里是 `createtime`。
10. **删回复删错对象** — `templates/article.html:331` 传的是父评论 `comment.commentid`，后端按父评论作者鉴权 → 要么整条线程被隐藏，要么 403。
11. **保存昵称必失败** — `templates/userManage.html:53` `onclick="modifyNickname(this,{{ myInfo["myNickname"] }})"` 没加引号，`owner` 被当 JS 变量 → ReferenceError。
12. **搜索结果缩略图全裂** — `templates/search.html:40` 少 `/thumb`（其余页面是 `/static/img/thumb/...`）。
13. **草稿修改限额从未生效** — `database/articleLog.py:53` 匹配中文 `"修改文章"`，实际写入英文 `"Modify article"`（`controler/article.py:344`）。

### P2 — 体验与健壮性（摘要）

- 非法 id 一路 500：`comment.py:94,267`、`favorite.py:48`、`adminManage.py:131,152`、`user.py:206,213`；应 400/404。
- 只有 404/500 有品牌页；`abort(400/401/403)` 是裸 Werkzeug 页（`app.py:116-127`）。
- 积分不足购买静默失败：后端 409（`article.py:138`），前端只认 `"1"`。
- "登录记录"页永远空：`logs.py:54-55` 过滤的分类没有任何代码写入。
- 每日登录加分判断过宽：`credit.py:165-166` 当天有任何积分记录就跳过。
- 作者分成 `math.ceil(0.5*credit)`（`credit.py:103`）：1 分文章作者拿满 100%。
- 分页 `range(1,total)` 少最后一页（`article.html:393`）；每页条数硬编码 10，与 `howArticleInWeb` 不一致。
- UEditor 写入的图片是 `http://127.0.0.1:<port>/...` 绝对地址（`ueditorConf.py:24,30-46`），换机器/换端口即失效。
- CSP 仍含 `script-src 'unsafe-inline'`，模板里大量 `onclick`；jQuery 3.5.1 与 1.11.1 并存，UEditor 已停维护。
- SQLite 未开 WAL/`timeout`，而每次阅读都 `updateReadCount`；多线程 waitress 下会撞 `database is locked`。
- 三份 schema 真源（`schema.py` / 迁移 / `myBlog.sql`）+ `create_all` 绕过迁移 → 未来必然漂移。
- N+1 遍布 `database/*`（循环里再查）；缺 `comment.userid`、`favorite.userid`、`log(category,target)` 索引。
- 路径拼接用 `"\\"`（`myLog.py:62` 等），Windows-only。
- 7 个测试一条 P0 都没覆盖到。

---

## 4. README 声明核对

（先纠正：我上一轮说"17 条"是数错了，README 实际列了 **11 条**。）

| 声明 | 判定 |
| --- | --- |
| 应用工厂、配置解耦 | **属实** |
| 零配置 SQLite、`DATABASE_URL` 切 MySQL | **属实**（MySQL 未实测） |
| pyproject + uv.lock | **属实**，但本机无 uv，README 首启会断 |
| Alembic 迁移 + CLI | **部分属实**：迁移与 schema 逐列一致，但默认路径被 `create_all` 抢先，`db upgrade` 直接失败 |
| scrypt + 旧 MD5 自动升级 | **属实**；但 MD5 通道永不过期，默认盐是公开字符串 |
| 管理员 RBAC / 所有权 / 封禁 | **属实**（未发现 IDOR，写操作都取 `session["userid"]`） |
| 全站 CSRF / 限流 / 安全头 / 生产密钥检查 | **部分属实**：CSRF 确为全站（UEditor 例外走 query token）；限流只覆盖 5 个端点；密钥检查可被公开占位值绕过 |
| 文章 HTML 白名单 / 付费正文不下发 | **属实**（服务端 500 字纯文本预览）；`target` 未强制 `rel=noopener` |
| 图片真实格式/大小/像素/随机名/重编码 | **属实**（`utility.py:168-187`） |
| SQLite/MySQL 时间与随机排序兼容 | **属实**（`func.random/rand` 有分支） |
| pytest + Ruff | **属实**（7 passed / 0 error），覆盖面很窄 |

---

## 5. 遗留物处置

**可删**
- `myBlog.sql`（陈旧且误导，见 P1-4）
- `.img/`（2.2 MB 截图素材，非运行时资源）
- `database/favorite.py` 里重复的 `Article` 类、`static/js/admin-scripts.js`、`templates/exampleArticle.html`
- 死代码：`/userInfo`、`/adminMail`、`/toTransmitParam`、`searchAllFavorite`、`modifyCredit`（赋值给 Query，永不生效）

**可改**
- `controler/` → `controllers/`：一次全仓替换 + 改 import，顺带 `ininLogDir`、`erroe-404.html`
- 5 处重复的 `class Users/Article/Comment(DBase)` 收敛成单一模型模块
- `"\\"` 拼接 → `pathlib`
- `creditListForReleaseArticle` 等改成 tuple/frozenset，从根上杜绝 P0-5

**必须保留**
- `migrations/`（唯一可信的 schema 来源）
- MD5 校验分支（迁移通道，但要加"下次登录强制改密"）
- `static/ue/`（发文页依赖；换编辑器是另一个项目）
- `logs/`、`instance/` 已被 ignore，属运行时产物

---

## 6. 建议顺序（批次 1–3 已执行，此处保留为复盘顺序）

**今天（半天，5 个 P0，都是几行）**
1. P0-3 回复评论（删 1 行）
2. P0-4 用户中心（删 10 行副本类）
3. P0-5 常量就地改写（4 行）
4. P0-2 密钥守卫（6 行）+ `.env.example` 置空
5. 取消收藏（删 1 行）+ 昵称引号 + `createtime`

**本周**
6. P0-1 验证码改服务端存储（新表 + 一次迁移，唯一的"大改"）
7. 事务边界 + 积分并发（`UPDATE ... SET c = c + 1`）
8. `AUTO_INIT_DB` 默认 `False`、删 `myBlog.sql`、补迁移
9. 轮换历史泄露口令 + `git filter-repo`

**之后**
10. 限流覆盖写操作、上 `ProxyFix` + 共享存储
11. 给每条 P0 补一个回归用例（现有 7 个测试没覆盖到任何一条）
12. 前端：CSP 收紧到 nonce，把 `onclick` 迁走；再谈换 UEditor

---

## 7. 附：复现命令（本次实跑）

```powershell
python -m venv .venv ; .\.venv\Scripts\python.exe -m pip install -r requirements.txt pytest ruff
.\.venv\Scripts\python.exe -m pytest -q           # 7 passed
.\.venv\Scripts\python.exe -m ruff check .        # All checks passed
$env:AUTO_INIT_DB="True"; .\.venv\Scripts\python.exe -m flask --app app db upgrade   # table log already exists
.\.venv\Scripts\waitress-serve.exe --host=127.0.0.1 --port=5099 --call app:create_app
```

> 说明：P0-1 的复现把 `send_email` stub 掉了（等价于"已配好邮箱的正常部署"），否则 `/ecode` 会先 500；这恰好说明未配 SMTP 时注册/找回整条链路不可用。
