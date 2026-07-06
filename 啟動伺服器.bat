@echo off
chcp 65001 >nul
title 啟動 PWA 整合伺服器
echo ==============================
echo   啟動 PWA 整合伺服器
echo ==============================
echo.

:: 查 IP
for /f "tokens=3 delims=: " %%i in ('netsh interface ip show address "Wi-Fi" ^| findstr "IP"') do set MY_IP=%%i
if defined MY_IP (
    echo ✅ 本機 IP: %MY_IP%
) else (
    echo ⚠️ 找不到 WiFi IP，請確認已連線網路
)

:: 背景啟動 PWA 整合伺服器 (port 8080，同時提供頁面 + 上傳)
start /B python pwa_server.py
if %errorlevel% equ 0 (
    echo ✅ PWA 整合伺服器啟動中...
    echo.
    echo   PWA 拍照頁面: http://%MY_IP%:8080
    echo   上傳端點:     http://%MY_IP%:8080/api/upload
)

echo.
echo ==============================
echo 📱 手機同步頁面填入 IP:
echo    %MY_IP%:8080
echo ==============================
echo.
echo 按任一鍵關閉此視窗（伺服器會在背景繼續跑）
pause >nul
