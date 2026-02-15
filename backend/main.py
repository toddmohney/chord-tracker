from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.health import router as health_router
from routers.projects import router as projects_router

app = FastAPI(title="Chord Tracker API", version="0.1.0")

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
