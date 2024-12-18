@echo off
:restart
echo Resuming...
python start.py --name test29 --resume --step 1 --stride 60

echo The start.py is stop, wait for resume...
timeout /t 5 > nul
goto restart