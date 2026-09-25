#!/bin/bash

echo "======================================================="
echo "    SignTalk Enterprise Platform Launcher (100% Free)  "
echo "======================================================="
echo ""

# 1. Start FastAPI Backend Microservice
echo "[+] Starting FastAPI & WebSocket Broker on http://localhost:8000 ..."
cd backend_service
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 2. Start Enterprise Web Portal
echo "[+] Starting Enterprise React Web Portal on http://localhost:5173 ..."
cd web_portal
npm run dev -- --host &
WEB_PID=$!
cd ..

echo ""
echo "[+] Enterprise Services Active!"
echo "[+] Backend OpenAPI Specs: http://localhost:8000/docs"
echo "[+] Web Portal Dashboard : http://localhost:5173"
echo ""

wait $BACKEND_PID $WEB_PID
