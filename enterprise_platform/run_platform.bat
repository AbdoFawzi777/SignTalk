@echo off
TITLE SignTalk Enterprise Platform Launcher ($0 Cost Budget)
COLOR 0A

echo =======================================================
echo     SignTalk Enterprise Platform Launcher (100%% Free)
echo =======================================================
echo.

:: 1. Validate Python Installation & Start FastAPI Backend Server
echo [+] Launching FastAPI Backend & WebSocket Server on http://localhost:8000 ...
start "SignTalk Backend Server" cmd /k "cd /d %~dp0backend_service && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: 2. Launch Enterprise Web Portal
echo [+] Launching Enterprise Web Portal (React/Vite) on http://localhost:5173 ...
start "SignTalk Web Portal" cmd /k "cd /d %~dp0web_portal && npm run dev -- --host"

:: 3. Inform User
echo.
echo =======================================================
echo  [+] All Enterprise Microservices Started Successfully!
echo  [+] FastAPI Backend Docs : http://localhost:8000/docs
echo  [+] WebSocket Stream     : ws://localhost:8000/ws/translation
echo  [+] Web Counter Portal   : http://localhost:5173
echo =======================================================
echo.
pause
