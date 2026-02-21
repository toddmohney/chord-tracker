from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.chords import router as chords_router
from routers.collaborators import router as collaborators_router
from routers.collaborators import status_router as collaborator_status_router
from routers.health import router as health_router
from routers.projects import router as projects_router
from routers.sequence import router as sequence_router
from routers.songs import router as songs_router

app = FastAPI(title="Chord Tracker API", version="0.1.0")

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(collaborators_router, prefix="/api/projects", tags=["collaborators"])
app.include_router(collaborator_status_router, prefix="/api", tags=["collaborators"])
app.include_router(songs_router, prefix="/api", tags=["songs"])
app.include_router(chords_router, prefix="/api", tags=["chords"])
app.include_router(sequence_router, prefix="/api", tags=["sequence"])
