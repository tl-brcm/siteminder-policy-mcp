
$NGINX_VERSION = "1.26.2"
$NGINX_ZIP = "nginx-$NGINX_VERSION.zip"
$NGINX_URL = "https://nginx.org/download/$NGINX_ZIP"
# We put the portable install in the root but manage it from here
$DEST_DIR = "../nginx-portable"

if (-not (Test-Path $DEST_DIR)) {
    Write-Host "Nginx not found. Downloading version $NGINX_VERSION..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $NGINX_URL -OutFile $NGINX_ZIP
    
    Write-Host "Extracting Nginx..." -ForegroundColor Cyan
    Expand-Archive -Path $NGINX_ZIP -DestinationPath $DEST_DIR
    
    $subfolder = Get-ChildItem -Path $DEST_DIR -Directory | Where-Object { $_.Name -like "nginx-*" }
    if ($subfolder) {
        Get-ChildItem -Path $subfolder.FullName | Move-Item -Destination $DEST_DIR
        Remove-Item $subfolder.FullName
    }
    Remove-Item $NGINX_ZIP
}

# Sync configuration and certificates (certs are in project root)
Copy-Item "nginx.conf" -Destination "$DEST_DIR/conf/nginx.conf" -Force
Copy-Item "../cert.pem" -Destination "$DEST_DIR/conf/cert.pem" -Force
Copy-Item "../key.pem" -Destination "$DEST_DIR/conf/key.pem" -Force

Write-Host "Starting Nginx on port 8443..." -ForegroundColor Green
Write-Host "URL: https://mcp.vm.demo:8443/sm-policy/mcp" -ForegroundColor Yellow

Push-Location $DEST_DIR
try {
    Start-Process ./nginx.exe
} finally {
    Pop-Location
}
