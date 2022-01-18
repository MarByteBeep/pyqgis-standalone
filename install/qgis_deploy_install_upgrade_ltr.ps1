#Requires -RunAsAdministrator

<#
.Synopsis
   Download the OSGeo4W installer then download and install QGIS LTR (through the 'full' meta-package).
.DESCRIPTION
   This script will:
      1. change the current directory to the user downloads folder
      2. download the OSGeo4W installer
      3. launch it passing command-line parameters to DOWNLOAD packages required to QGIS LTR FULL
      4. launch it passing command-line parameters to INSTALL QGIS LTR

    Documentation reference: https://trac.osgeo.org/osgeo4w/wiki/CommandLine
#>

# Save current working directory
$starter_path = Get-Location

# Move into the user download directory
Set-Location -Path "$env:USERPROFILE/Downloads"

# Download installer if not exists
if (-Not (Test-Path "osgeo4w_v2-setup.exe" -PathType leaf )) {
   Write-Host "= Start downloading the OSGeo4W installer" -ForegroundColor Yellow
   Invoke-WebRequest -Uri "https://download.osgeo.org/osgeo4w/v2/osgeo4w-setup.exe" -OutFile "osgeo4w_v2-setup.exe"
   Write-Host "== Installer downloaded into $env:USERPROFILE/Downloads" -ForegroundColor Yellow
}
else
{ Write-Host "= OSGeo4W installer already exists. Let's use it!" -ForegroundColor Blue }


# Download and install (same command to upgrade with clean up)
Write-Host "=== Start installing / upgrading QGIS LTR..." -ForegroundColor Yellow
& .\osgeo4w_v2-setup.exe `
    --advanced `
    --arch x86_64 `
    --autoaccept `
    --delete-orphans `
    --local-package-dir "$env:APPDATA/OSGeo4W_v2-Packages" `
    --menu-name "QGIS LTR" `
    --no-desktop `
    --packages qgis-ltr-full `
    --quiet-mode `
    --site "http://www.norbit.de/osgeo4w/v2" `
    --site "http://download.osgeo.org/osgeo4w/v2" `
    --site "http://ftp.osuosl.org/pub/osgeo/download/osgeo4w/v2" `
    --upgrade-also `
 | out-null

# Return to the initial directory
Set-Location -Path $starter_path
Write-Host "==== Work is done!" -ForegroundColor Green