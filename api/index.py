import sys
import os
import traceback
from pathlib import Path

# Add backend directory to sys.path so imports resolve
ROOT_DIR = Path(__file__).parent.parent
backend_dir = str(ROOT_DIR / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from server import app
except Exception as e:
    err_tb = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Gagan Engineering Works API - Error Handler")
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    async def vercel_error_handler(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Server initialization failed",
                "exception": str(e),
                "traceback": err_tb,
            }
        )

