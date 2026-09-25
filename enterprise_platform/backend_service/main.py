from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import websocket_translation, enterprise_portal, academy

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise API & Real-time WebSocket Broker for SignTalk Platform ($0 Cost Budget)."
)

# Enable Universal CORS for Web Portal & Mobile Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Service Routers
app.include_router(websocket_translation.router)
app.include_router(enterprise_portal.router)
app.include_router(academy.router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }
