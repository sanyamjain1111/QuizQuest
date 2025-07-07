@echo off
echo Starting Quiz Master Services...

:: Start Redis in WSL on port 6380
echo Starting Redis server (WSL port 6380)...
start "Redis Server" wsl redis-server --port 6380 --bind 0.0.0.0
timeout /t 3 /nobreak > nul

:: Start Flask backend (in backend directory)
echo Starting Flask backend...
start "Flask Backend" cmd /k "python main.py"

:: Start Celery worker (in backend directory)
echo Starting Celery worker...
start "Celery Worker" cmd /k "python -m celery -A main.celery worker --loglevel=info --pool=solo"

:: Start Celery beat (in backend directory)
echo Starting Celery beat...
start "Celery Beat" cmd /k "python -m celery -A main.celery beat --loglevel=debug"

:: Start frontend (from root to frontend directory)
echo Starting Frontend...
start "Frontend" cmd /k "cd.. && cd frontend && npm run serve"

echo.
echo All services started successfully!
echo --------------------------------
echo Redis: Running in WSL (port 6380)
echo Flask: Running on http://localhost:5000
echo Celery Worker: Processing tasks
echo Celery Beat: Running scheduled tasks
echo Frontend: Running on http://localhost:8080
echo.
echo To stop services, run stop_services.bat
pause