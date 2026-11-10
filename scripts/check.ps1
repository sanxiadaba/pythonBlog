# 本地检查：lint + 格式 + 测试。没有 CI，提交前跑这一条就行。
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

uv run ruff check .
uv run ruff format --check .
uv run pytest
