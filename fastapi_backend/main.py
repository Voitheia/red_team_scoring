from typing import Union
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_backend.routes import login, admin, scoreboard, details
from fastapi_backend.core.orchestrator import CompetitionOrchestrator

API_VERSION = "1.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Global orchestrator instance
orchestrator: CompetitionOrchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global orchestrator

    # Startup
    logging.info("Starting FastAPI application...")
    orchestrator = CompetitionOrchestrator()
    await orchestrator.initialize()

    yield

    # Shutdown
    logging.info("Shutting down FastAPI application...")
    if orchestrator:
        await orchestrator.shutdown()

app = FastAPI(lifespan=lifespan, title="Red Team Scoring API", version=API_VERSION)

# CORS alert
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:5173"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Red Team Scoring": API_VERSION}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

app.include_router(login.router)
app.include_router(admin.router)
app.include_router(scoreboard.router)
app.include_router(details.router)