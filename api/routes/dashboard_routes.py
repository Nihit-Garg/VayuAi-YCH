"""
API Routes for Dashboard Data
Provides aggregated data for frontend visualization
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging

from models.schemas import DashboardData, BlockchainLog
from services.shared import sensor_service, blockchain_logger

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/data/{device_id}")
async def get_dashboard_data(device_id: str):
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
        # Get current sensor reading
        current_reading = sensor_service.get_latest_reading(device_id)
        if not current_reading:
            raise HTTPException(status_code=404, detail=f"No data found for device {device_id}")
        
        # Get cached AI decisions
        from services.shared import get_latest_decisions
        cached_decisions = get_latest_decisions(device_id)
        
        if not cached_decisions:
            raise HTTPException(status_code=404, detail=f"No AI decisions found for device {device_id}. Send sensor data first.")
        
        # Get recent blockchain logs for this device
        blockchain_logs = blockchain_logger.get_logs_by_device(device_id, limit=10)
        
        # Get recent faults
        recent_faults = []
        if cached_decisions.get("fault"):
            recent_faults = [cached_decisions["fault"]]
        
        # Build control response
        decision = cached_decisions["decision"]
        control_response = {
            "fan_on": decision.fan_on,
            "fan_intensity": decision.fan_intensity,
            "timestamp": current_reading.timestamp
        }
        
        # Build dashboard data
        dashboard_data = {
            "device_id": device_id,
            "current_reading": current_reading.dict(),
            "prediction": cached_decisions["prediction"].dict(),
            "classification": cached_decisions["classification"].dict(),
            "control_status": control_response,
            "recent_faults": [f.dict() for f in recent_faults],
            "recent_logs": [log.dict() for log in blockchain_logs],
            "system_health": {
                "status": "healthy",
                "ai_mode": "mock",
                "blockchain": "connected" if blockchain_logger.enabled else "simulated"
            }
        }
        
        return dashboard_data
        
    except HTTPException:
        raise
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
