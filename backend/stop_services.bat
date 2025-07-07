@echo off
echo Stopping Quiz Master Services...

:: Stop Redis in WSL
echo Stopping Redis server...
wsl redis-cli -p 6380 shutdown

:: Stop Python processes
echo Stopping Python services...
taskkill /F /IM python.exe /T > nul 2>&1

:: Stop Node processes
echo Stopping Frontend...
taskkill /F /IM node.exe /T > nul 2>&1

echo All services stopped successfully!
timeout /t 2 /nobreak > nul