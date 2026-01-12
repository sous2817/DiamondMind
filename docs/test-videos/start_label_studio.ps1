# Label Studio Startup Script
# Starts Label Studio with local file access enabled

Write-Host "Starting Label Studio with local file access..." -ForegroundColor Cyan

# Set environment variables for local file serving
$env:LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED = "true"
$env:LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT = "C:\Training Data\BaseballSwings"

# Start Label Studio
Write-Host "Local files directory: C:\Training Data\BaseballSwings" -ForegroundColor Green
Write-Host "Opening Label Studio at http://localhost:8080" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop Label Studio" -ForegroundColor Yellow
Write-Host ""

label-studio start
