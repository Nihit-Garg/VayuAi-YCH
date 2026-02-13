"""
AeroLedger - Gen-AI + Blockchain Air Safety System
Main FastAPI Application Entry Point

This is the central entry point for the AeroLedger backend.
It initializes FastAPI, registers all routes, and starts the server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from api.routes import sensor_routes, control_routes, dashboard_routes
from config.settings import settings
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Startup:
    - Initialize blockchain connection (or simulated ledger)
    - Load AI models/agents
    - Initialize sensor data buffer
    
    Shutdown:
    - Close blockchain connections
    - Save any pending data
    - Cleanup resources
    """
    logger.info("🚀 AeroLedger starting up...")
    
    # TODO: Initialize blockchain connection
    # TODO: Initialize AI agents
    # TODO: Initialize in-memory context storage
    
    yield
    
    logger.info("🛑 AeroLedger shutting down...")
    # TODO: Cleanup resources


# Initialize FastAPI app
app = FastAPI(
    title="AeroLedger API",
    description="Gen-AI powered intelligent air monitoring and control system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(sensor_routes.router, prefix="/api/v1/sensor", tags=["Sensor"])
app.include_router(control_routes.router, prefix="/api/v1/control", tags=["Control"])
app.include_router(dashboard_routes.router, prefix="/api/v1/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AeroLedger",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check with system status"""
    return {
        "status": "healthy",
        "blockchain": "connected",  # TODO: Check actual blockchain status
        "ai_agents": "ready",  # TODO: Check AI agent status
        "sensors": "active"  # TODO: Check sensor connection status
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
