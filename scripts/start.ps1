# 启动博客。默认开发模式（改代码自动重载）；-Mode prod 用 waitress 常驻。
param(
    [int]$Port = 5000,
    [ValidateSet("dev", "prod")]
    [string]$Mode = "dev"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

uv sync --frozen
if ($Mode -eq "dev") {
    $env:DEBUG_MODE = "True"
    uv run flask --app app run --debug --port $Port
}
else {
    $env:DEBUG_MODE = "False"
    uv run python -m waitress --host=127.0.0.1 --port=$Port --call app:create_app
}
