param(
    [ValidateSet("development", "production")]
    [string]$Mode = "development",
    [int]$Port = 5000
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Install it from https://docs.astral.sh/uv/."
}

if ($Mode -eq "production") {
    uv sync --frozen --no-dev
    $env:DEBUG_MODE = "False"
    uv run waitress-serve --host=127.0.0.1 --port=$Port --call app:create_app
} else {
    uv sync --frozen
    uv run flask --app app run --debug --host=127.0.0.1 --port=$Port
}
