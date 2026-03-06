Write-Host "Stopping all Nginx processes..." -ForegroundColor Red
# Forcefully terminate any running nginx instances
Stop-Process -Name "nginx" -ErrorAction SilentlyContinue
Write-Host "Nginx stopped." -ForegroundColor Gray