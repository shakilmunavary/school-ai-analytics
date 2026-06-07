Write-Host ""
Write-Host "====================================="
Write-Host " School AI - Stop"
Write-Host "====================================="
Write-Host ""

$ProjectRoot = "D:\shakil-ai-project"
$PidFile = "$ProjectRoot\app.pid"

# Stop by PID if available

if(Test-Path $PidFile)
{
    try
    {
        $AppPid = Get-Content $PidFile

        Write-Host "Stopping PID $AppPid"

        taskkill /PID $AppPid /F | Out-Null

        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue

        Write-Host "Application stopped."
    }
    catch
    {
        Write-Host "PID stop failed."
    }
}

# Extra safety: stop any uvicorn/python process

Write-Host ""
Write-Host "Stopping any remaining Python processes..."

taskkill /F /IM python.exe 2>$null
taskkill /F /IM pythonw.exe 2>$null

Write-Host ""
Write-Host "Cleanup complete."
Write-Host ""