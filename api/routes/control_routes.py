"""
API Routes for Control Commands
Handles manual control overrides and control status queries
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
import logging

from models.schemas import ControlResponse, ControlDecision
from services.control_service.controller import ControlService

router = APIRouter()
logger = logging.getLogger(__name__)

control_service = ControlService()


@router.post("/override", response_model=ControlResponse)
async def manual_override(
    device_id: str,
    fan_on: bool,
    fan_intensity: int
) -> ControlResponse:
    """
    Manual override of automatic control.
    Useful for testing or emergency situations.
    
    Args:
        device_id: Target ESP32 device
        fan_on: Force fan ON/OFF
        fan_intensity: Force fan intensity (0-100)
    
    Returns:
        ControlResponse confirming the override
    """
    try:
        logger.info(f"Manual override for {device_id}: fan_on={fan_on}, intensity={fan_intensity}")
        
        response = control_service.set_manual_override(
            device_id=device_id,
            fan_on=fan_on,
            fan_intensity=fan_intensity
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error setting manual override: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/override/{device_id}")
async def clear_override(device_id: str) -> Dict:
    """
    Clear manual override and return to automatic control.
    
    Args:
        device_id: Target ESP32 device
    
    Returns:
        Confirmation message
    """
    try:
        control_service.clear_manual_override(device_id)
        return {"status": "success", "message": f"Override cleared for {device_id}"}
    except Exception as e:
        logger.error(f"Error clearing override: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{device_id}")
async def get_control_status(device_id: str) -> Dict:
    """
    Get current control status for a device.
    
    Returns:
        - Current fan state
        - Whether in manual override mode
        - Last control decision
    """
    try:
        status = control_service.get_status(device_id)
        return status
    except Exception as e:
        logger.error(f"Error getting control status: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
