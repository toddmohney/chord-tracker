from fastapi import FastAPI

from routers.health import router as health_router

app = FastAPI(title="Chord Tracker API", version="0.1.0")

app.include_router(health_router, prefix="/api", tags=["health"])
