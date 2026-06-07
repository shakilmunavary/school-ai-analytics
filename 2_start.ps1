Write-Host ""
Write-Host "====================================="
Write-Host " School AI Workspace Ecosystem - Start"
Write-Host "====================================="
Write-Host ""

$ProjectRoot = "D:\shakil-ai-project"
Set-Location $ProjectRoot

# ------------------------------------------------
# Clean and close preceding lifecycle bounds
# ------------------------------------------------
if(Test-Path "$ProjectRoot\app.pid")
{
    try {
        $OldPid = Get-Content "$ProjectRoot\app.pid"
        taskkill /PID $OldPid /F 2>$null
        Remove-Item "$ProjectRoot\app.pid" -Force -ErrorAction SilentlyContinue
    } catch {}
}
taskkill /F /IM python.exe 2>$null

# ------------------------------------------------
# Initialize isolated script environments
# ------------------------------------------------
if(!(Test-Path "$ProjectRoot\venv"))
{
    Write-Host "Building Virtual Environment Workspace..."
    python -m venv venv
}
& "$ProjectRoot\venv\Scripts\Activate.ps1"

# ------------------------------------------------
# Manage installation dependencies
# ------------------------------------------------
if(!(Test-Path "$ProjectRoot\venv\.installed"))
{
    Write-Host "Installing Core Component Requirements..."
    python -m pip install --upgrade pip
    python -m pip install `
        fastapi `
        uvicorn `
        requests `
        chromadb `
        sentence-transformers `
        numpy `
        pandas `
        openpyxl `
        pypdf `
        reportlab `
        python-multipart `
        jinja2

    New-Item "$ProjectRoot\venv\.installed" -ItemType File | Out-Null
}

# ------------------------------------------------
# Synchronize data index vectors
# ------------------------------------------------
Write-Host "Rebuilding Index spaces..."
if(Test-Path "$ProjectRoot\vector_db") {
    Remove-Item "$ProjectRoot\vector_db" -Recurse -Force -ErrorAction SilentlyContinue
}
python index.py

# ------------------------------------------------
# Execute background worker server process
# ------------------------------------------------
Write-Host "Starting School Analytics Web application Engine..."
$Process = Start-Process `
    "$ProjectRoot\venv\Scripts\python.exe" `
    -ArgumentList "-m uvicorn server:app --host 0.0.0.0 --port 8000" `
    -PassThru `
    -WindowStyle Hidden

# Fix: Force cast process identification values explicitly to avoid runtime printing blocks
$ActivePid = [string]$Process.Id
$ActivePid | Set-Content "$ProjectRoot\app.pid"
Start-Sleep 4

Write-Host "====================================="
Write-Host " Workspace Application Ready"
Write-Host "====================================="
Write-Host "Access Link: http://localhost:8000"
Write-Host "Process PID: $ActivePid"
Write-Host ""