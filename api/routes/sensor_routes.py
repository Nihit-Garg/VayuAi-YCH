"""
API Routes for Sensor Data Ingestion
Handles incoming sensor data from ESP32 devices
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict
import logging

from models.schemas import SensorReading, ControlResponse
from services.sensor_service.ingestion import SensorIngestionService
from core.decision_engine.orchestrator import DecisionOrchestrator

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services (in production, use dependency injection)
sensor_service = SensorIngestionService()
decision_orchestrator = DecisionOrchestrator()


@router.post("/ingest", response_model=ControlResponse)
async def ingest_sensor_data(
    reading: SensorReading,
    background_tasks: BackgroundTasks
) -> ControlResponse:
    """
    Main endpoint for ESP32 to send sensor data.
    
    Flow:
    1. Validate incoming sensor data
    2. Store in context buffer
    3. Trigger AI agent orchestration
    4. Get control decision
    5. Log critical events to blockchain (background)
    6. Return control command to ESP32
    
    Args:
        reading: Validated sensor reading from ESP32
        background_tasks: FastAPI background tasks for async blockchain logging
    
    Returns:
        ControlResponse with fan control commands
    """
    try:
        logger.info(f"Received sensor data from {reading.device_id}")
        
        # Step 1: Store sensor reading in context
        sensor_service.store_reading(reading)
        
        # Step 2: Get recent context for AI agents
        context = sensor_service.get_recent_context(reading.device_id)
        
        # Step 3: Run decision orchestration (AI agents + fault detection + control)
        control_decision = await decision_orchestrator.process(reading, context)
        
        # Step 4: Log critical decisions to blockchain (background task)
        if control_decision.fan_on or control_decision.override_reason:
            background_tasks.add_task(
                decision_orchestrator.log_to_blockchain,
                reading.device_id,
                control_decision
            )
        
        # Step 5: Return control response
        response = ControlResponse(
            fan_on=control_decision.fan_on,
            fan_intensity=control_decision.fan_intensity
        )
        
        logger.info(f"Control decision: fan_on={response.fan_on}, intensity={response.fan_intensity}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/status/{device_id}")
async def get_sensor_status(device_id: str) -> Dict:
    """
    Get current status of a specific sensor device.
    
    Returns:
        - Last reading timestamp
        - Connection status
        - Fault status
    """
    try:
        status = sensor_service.get_device_status(device_id)
        return status
    except Exception as e:
        logger.error(f"Error getting sensor status: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")


@router.get("/history/{device_id}")
async def get_sensor_history(device_id: str, limit: int = 50) -> Dict:
    """
    Get historical sensor readings for a device.
    
    Args:
        device_id: ESP32 device identifier
        limit: Number of recent readings to return (default 50)
    
    Returns:
        List of recent sensor readings
    """
    try:
        history = sensor_service.get_history(device_id, limit)
        return {"device_id": device_id, "readings": history}
    except Exception as e:
        logger.error(f"Error getting sensor history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
