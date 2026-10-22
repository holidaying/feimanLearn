# Feynman Lab Class - one-click launcher
# Starts the Python backend, which ALSO serves the built frontend (web/dist).
# After it starts, open: http://localhost:8000
#
# Note: the built frontend must exist. If web/dist is missing, run in web/:
#   npm install && npm run build

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$server = Join-Path $root "server"

if (-not $env:DASHSCOPE_API_KEY) {
    $env:DASHSCOPE_API_KEY = Read-Host "Enter Qwen API Key (kept in this session only, never written to disk)"
}

$distIndex = Join-Path $root "web\dist\index.html"
if (-not (Test-Path $distIndex)) {
    Write-Host "WARNING: web\dist\index.html not found - frontend not built yet." -ForegroundColor Yellow
    Write-Host "Please run in web\ : npm install && npm run build" -ForegroundColor Yellow
}

$py = $null
foreach ($c in @("python", "py", "python3")) {
    try {
        $v = & $c --version 2>$null
        if ($v) { $py = $c; break }
    } catch {}
}
if (-not $py) {
    $managed = "C:\Users\28907\.workbuddy\binaries\python\versions\3.13.12\python.exe"
    if (Test-Path $managed) { $py = $managed }
}
if (-not $py) {
    Write-Host "ERROR: no python found. Install Python 3 or add it to PATH." -ForegroundColor Red
    exit 1
}

Write-Host "Using python: $py" -ForegroundColor Cyan
Write-Host "Open http://localhost:8000 after it starts. Ctrl+C to stop." -ForegroundColor Cyan
Set-Location $server
& $py app.py
