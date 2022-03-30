@echo off
:loop
set arg1=%1
python locator.py %arg1% 
timeout /t 10
goto loop