@echo off
chcp 65001 >nul
title PWA Connection Info
echo ==============================
echo   PWA Connection Info
echo ==============================
echo.
for /f "tokens=3 delims=: " %%i in ('netsh interface ip show address "Wi-Fi" ^| findstr "IP"') do set MY_IP=%%i
if defined MY_IP (
    echo.
    echo PWA 拍照頁面 + 上傳接收:
    echo   http://%MY_IP%:8080
    echo.
    echo 手機同步頁面請填入:
    echo   %MY_IP%:8080
) else (
    echo Cannot find WiFi IP. Check network.
)
echo.
pause
