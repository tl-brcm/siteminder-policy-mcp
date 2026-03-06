#!/bin/bash

NGINX_VERSION="1.26.2"
DEST_DIR="../nginx-portable"

# This script assumes you are running on Windows via Git Bash / WSL
# If on true Linux/macOS, you'd use 'apt-get' or 'brew' to install nginx instead of downloading a zip.

if [ ! -d "$DEST_DIR" ]; then
    echo "Nginx portable directory not found. Please run the PowerShell script first to download or install nginx on your system."
    exit 1
fi

# Sync configuration and certificates
cp nginx.conf "$DEST_DIR/conf/nginx.conf"
cp ../cert.pem "$DEST_DIR/conf/cert.pem"
cp ../key.pem "$DEST_DIR/conf/key.pem"

echo "Starting Nginx on port 8443..."
cd "$DEST_DIR"
./nginx.exe
