# Install backend dependencies into backend\venv (same Python as uvicorn).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".\venv\Scripts\pip.exe")) {
    Write-Error "venv not found. Create it first: python -m venv venv"
}
& ".\venv\Scripts\pip.exe" install -r requirements.txt -i "https://pypi.tuna.tsinghua.edu.cn/simple"
Write-Host "Done. Prefer: .\run_dev.ps1   (or: .\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000)"
