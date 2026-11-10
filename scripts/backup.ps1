# 备份博客数据：数据库 + 上传的图片，按时间戳存一份。
param([string]$Destination = "$env:USERPROFILE\blog-backup")

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$instance = Join-Path $root "instance"

if (-not (Test-Path (Join-Path $instance "blog.db"))) {
    throw "找不到数据库：$instance\blog.db（先启动一次博客）"
}

$target = Join-Path $Destination (Get-Date -Format "yyyyMMdd-HHmmss")
New-Item -ItemType Directory -Force $target | Out-Null

# SQLite 在 WAL 模式下还有单独的日志文件，一起拷走才算一致快照。
foreach ($name in "blog.db", "blog.db-wal", "blog.db-shm") {
    $file = Join-Path $instance $name
    if (Test-Path $file) { Copy-Item $file $target }
}

$upload = Join-Path $root "static\img\upload"
if (Test-Path $upload) {
    Copy-Item $upload (Join-Path $target "upload") -Recurse
}

$size = [math]::Round(((Get-ChildItem $target -Recurse -File | Measure-Object Length -Sum).Sum / 1KB), 1)
Write-Output "已备份到 $target（$size KB）"
