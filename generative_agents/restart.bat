@echo off
setlocal enabledelayedexpansion

REM 设置检测时间间隔（秒）和最大超时时间（秒）
set "check_interval=10"
set "timeout_threshold=100"

:restart
echo 正在运行程序...
start "" python start.py --name J-test04 --resume

REM 记录程序启动时间
set /a start_time=%time:~0,2%*3600 + %time:~3,2%*60 + %time:~6,2%

:check
REM 等待一段时间进行检测
timeout /t %check_interval% > nul

REM 检查程序是否还在运行
tasklist | findstr /i "python.exe" > nul
if %errorlevel% equ 0 (
    REM 计算当前时间与启动时间的差值
    set /a current_time=%time:~0,2%*3600 + %time:~3,2%*60 + %time:~6,2%
    set /a elapsed_time=!current_time! - !start_time!

    REM 如果程序运行时间超过阈值，强制重启
    if !elapsed_time! geq %timeout_threshold% (
        echo 程序无响应，正在强制停止...
        taskkill /im python.exe /f > nul
        echo 程序已停止，等待 5 秒后重启...
        timeout /t 5 > nul
        goto restart
    )
    goto check
) else (
    echo 程序已停止，等待 5 秒后重启...
    timeout /t 5 > nul
    goto restart
)