# Minimal FastAPI backend for Ambulon webchat

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.webchat.backend.routers import rag

app = FastAPI()
app.include_router(rag.router)

@app.get("/", response_class=HTMLResponse)
async def root():
    # Load the simple frontend HTML file
    html_path = Path(__file__).resolve().parent.parent / "frontend" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


