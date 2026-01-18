# Move PNG files from labels to images directory
# Label Studio sometimes exports images to the wrong folder

$sourceDir = "C:\Annotations\train\labels"
$destDir = "C:\Annotations\train\images"

# Check if source directory exists
if (-not (Test-Path $sourceDir)) {
    Write-Host "Error: Source directory not found: $sourceDir" -ForegroundColor Red
    exit 1
}

# Check if destination directory exists
if (-not (Test-Path $destDir)) {
    Write-Host "Creating destination directory: $destDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $destDir -Force
}

# Find all PNG files in source
$pngFiles = Get-ChildItem -Path $sourceDir -Filter "*.png"

if ($pngFiles.Count -eq 0) {
    Write-Host "No PNG files found in $sourceDir" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($pngFiles.Count) PNG files to move" -ForegroundColor Cyan

# Move each file
$movedCount = 0
foreach ($file in $pngFiles) {
    try {
        Move-Item -Path $file.FullName -Destination $destDir -Force
        $movedCount++
        Write-Host "Moved: $($file.Name)" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to move: $($file.Name) - $_" -ForegroundColor Red
    }
}

Write-Host "`nCompleted: Moved $movedCount of $($pngFiles.Count) files" -ForegroundColor Cyan
