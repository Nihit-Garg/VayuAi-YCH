"""
API Routes for Dashboard Data
Provides aggregated data for frontend visualization
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging

from models.schemas import DashboardData, BlockchainLog
from services.sensor_service.ingestion import SensorIngestionService
from blockchain.logger import BlockchainLogger

router = APIRouter()
logger = logging.getLogger(__name__)

sensor_service = SensorIngestionService()
blockchain_logger = BlockchainLogger()


@router.get("/data/{device_id}", response_model=DashboardData)
async def get_dashboard_data(device_id: str) -> DashboardData:
    """
    Get comprehensive dashboard data for a device.
    
    Returns:
        - Current sensor reading
        - Latest prediction
        - Air type classification
        - Control status
        - Recent faults
        - Recent blockchain logs
        - System health
    """
    try:
        # TODO: Implement aggregation logic
        # This should gather data from:
        # - Sensor service (current reading)
        # - Decision orchestrator (latest prediction & classification)
        # - Control service (current control state)
        # - Fault detector (recent faults)
        # - Blockchain logger (recent logs)
        
        raise HTTPException(status_code=501, detail="Dashboard aggregation not yet implemented")
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices")
async def list_devices() -> Dict[str, List[str]]:
    """
    List all registered ESP32 devices.
    
    Returns:
        List of device IDs with their status
    """
    try:
        devices = sensor_service.list_devices()
        return {"devices": devices}
    except Exception as e:
        logger.error(f"Error listing devices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blockchain/logs")
async def get_blockchain_logs(limit: int = 20) -> Dict[str, List[BlockchainLog]]:
    """
    Get recent blockchain transaction logs.
    
    Args:
        limit: Number of recent logs to return
    
    Returns:
        List of blockchain logs
    """
    try:
        logs = blockchain_logger.get_recent_logs(limit)
        return {"logs": logs}
    except Exception as e:
        logger.error(f"Error getting blockchain logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{device_id}")
async def get_analytics(device_id: str, hours: int = 24) -> Dict:
    """
    Get analytics and statistics for a device.
    
    Args:
        device_id: Target device
        hours: Time window for analytics (default 24 hours)
    
    Returns:
        - Average sensor values
        - Peak values
        - Number of control actions
        - Fault count
        - Air type distribution
    """
    try:
        # TODO: Implement analytics aggregation
        raise HTTPException(status_code=501, detail="Analytics not yet implemented")
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
