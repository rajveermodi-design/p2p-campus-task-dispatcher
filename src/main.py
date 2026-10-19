import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.routes.students import router as students_router
from src.routes.tasks import router as tasks_router
from src.routes.bids import router as bids_router
from src.routes.system import router as system_router

app = FastAPI(
    title="Peer-to-Peer Campus Errand Dispatcher API",
    description="High-concurrency, ACID-compliant errand dispatch system with escrow isolation.",
    version="1.0.0"
)

# Enable CORS for frontend/mobile clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include modular API routers
app.include_router(students_router)
app.include_router(tasks_router)
app.include_router(bids_router)
app.include_router(system_router)


# ============================================================================
# SYSTEM HEALTH & UI MOUNT
# ============================================================================

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Campus Errand Dispatcher",
        "engine": "MySQL 8.0 InnoDB",
        "docs_url": "/docs"
    }


# Static Frontend setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Ensure directory exists before mounting
os.makedirs(FRONTEND_DIR, exist_ok=True)
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.get("/", tags=["UI"])
def serve_ui():
    """Serves the Dispatcher Web App interface."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return health_check()