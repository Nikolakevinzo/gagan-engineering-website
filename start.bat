@echo off
echo Starting Gagan Engineering Works Website...
start "Gagan Engineering Backend" cmd /k "cd backend && python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload"
start "Gagan Engineering Frontend" cmd /k "cd frontend && npm start"
echo Both servers are starting!
echo Website: http://localhost:3000
echo Admin:   http://localhost:3000/admin/login
echo Backend: http://127.0.0.1:8000
