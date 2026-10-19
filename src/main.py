from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.students import router as students_router
from src.routes.tasks import router as tasks_router
from src.routes.bids import router as bids_router

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


# ============================================================================
# SYSTEM HEALTH CHECK
# ============================================================================

@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
def health_check():
    """Root & Health check endpoint."""
    return {
        "status": "online",
        "service": "Campus Errand Dispatcher",
        "engine": "MySQL 8.0 InnoDB",
        "docs_url": "/docs"
    }