@echo off
cd /d "%~dp0"
echo === OpenWrt TR3000 repo push ===
git init
git config user.name "lixiaoke6661"
git config user.email "lixiaoke6661@users.noreply.github.com"
git config core.autocrlf false
git add -A
git add -f .github
git commit -m "OpenWrt 25.12.6 for TR3000 256MB"
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/lixiaoke6661/openwrt-tr3000-256mb.git
set http_proxy=
set https_proxy=
set all_proxy=
echo.
echo When prompted:
echo   Username: lixiaoke6661
echo   Password: your Personal Access Token (repo scope), NOT your account password
echo.
git -c http.proxy= -c https.proxy= push -u origin main
echo.
echo Done. Press any key to close.
pause >nul
