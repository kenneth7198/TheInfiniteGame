@echo off
setlocal enabledelayedexpansion

REM Set the check interval (seconds) and timeout threshold (seconds)
set "check_interval=10"
set "timeout_threshold=100"

:restart
echo Starting start.py...
start "" python start.py --name test29 --resume

REM Record the program start time
set /a start_time=%time:~0,2%*3600 + %time:~3,2%*60 + %time:~6,2%

:check
REM Wait for a short period before checking
timeout /t %check_interval% > nul

REM Check if start.py is still running
tasklist /v | findstr /i "start.py" > nul
if %errorlevel% equ 0 (
    REM Calculate the elapsed time since start
    set /a current_time=%time:~0,2%*3600 + %time:~3,2%*60 + %time:~6,2%
    set /a elapsed_time=!current_time! - !start_time!

    REM If the elapsed time exceeds the threshold, force stop start.py
    if !elapsed_time! geq %timeout_threshold% (
        echo start.py is not responding. Forcing it to stop...
        for /f "tokens=2 delims=," %%A in ('tasklist /v /fi "imagename eq python.exe" /fo csv /nh ^| findstr /i "start.py"') do (
            taskkill /pid %%A /f > nul
        )
        echo start.py has been stopped. Restarting in 5 seconds...
        timeout /t 5 > nul
        goto restart
    )
    goto check
) else (
    echo start.py has stopped. Restarting in 5 seconds...
    timeout /t 5 > nul
    goto restart
)