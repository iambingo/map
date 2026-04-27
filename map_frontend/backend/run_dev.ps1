# 始终用 backend\venv 里的解释器启动，避免 (conda base + venv) 混用时 PATH 抢到 Anaconda 的 uvicorn。
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".\venv\Scripts\uvicorn.exe")) {
    Write-Error "venv\Scripts\uvicorn.exe missing. Run: python -m venv venv  then  .\install_deps.ps1"
}
& ".\venv\Scripts\uvicorn.exe" app.main:app --reload --port 8000
