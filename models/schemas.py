"""
Pydantic Models for Request/Response Validation
Defines the data structures used throughout the application
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


# ============= SENSOR DATA MODELS =============

class SensorReading(BaseModel):
    """
    Incoming sensor data from ESP32.
    
    Expected JSON format from ESP32:
    {
        "device_id": "ESP32_001",
        "pm25": 45.2,
        "co2": 850.0,
        "co": 12.5,
        "voc": 120.0,
        "timestamp": "2026-02-13T10:30:00"
    }
    """
    device_id: str = Field(..., description="Unique identifier for the ESP32 device")
    pm25: float = Field(..., ge=0, le=500, description="PM2.5 concentration (µg/m³)")
    co2: float = Field(..., ge=0, le=5000, description="CO2 concentration (ppm)")
    co: float = Field(..., ge=0, le=1000, description="CO concentration (ppm)")
    voc: float = Field(..., ge=0, le=1000, description="VOC concentration (ppb)")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, v):
        return v or datetime.utcnow()


# ============= AI AGENT OUTPUTS =============

class SmokeEventType(str, Enum):
    """Types of smoke/air pollution events"""
    CIGARETTE = "cigarette"
    VEHICLE = "vehicle"
    COOKING = "cooking"
    CHEMICAL = "chemical"
    CLEAN = "clean"
    UNKNOWN = "unknown"


class SmokePrediction(BaseModel):
    """
    Output from smoke prediction agent.
    Predicts if smoke event will occur in next few readings.
    """
    will_peak: bool = Field(..., description="Whether smoke levels will peak soon")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    estimated_peak_value: Optional[float] = Field(None, description="Estimated peak PM2.5 value")
    reasoning: str = Field(..., description="AI reasoning for the prediction")


class AirTypeClassification(BaseModel):
    """
    Output from air type classification agent.
    Classifies the type of air pollution.
    """
    air_type: SmokeEventType = Field(..., description="Classified air type")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    reasoning: str = Field(..., description="AI reasoning for classification")


class ControlDecision(BaseModel):
    """
    Output from control decision agent.
    Decides fan control action based on sensor data and predictions.
    """
    fan_on: bool = Field(..., description="Whether to turn fan ON or OFF")
    fan_intensity: int = Field(..., ge=0, le=100, description="Fan intensity (0-100)")
    reasoning: str = Field(..., description="AI reasoning for control decision")
    override_reason: Optional[str] = Field(None, description="Reason for overriding normal logic")


# ============= FAULT DETECTION MODELS =============

class FaultType(str, Enum):
    """Types of faults detected"""
    SENSOR_STUCK = "sensor_stuck"
    INCONSISTENT_READING = "inconsistent_reading"
    FAN_NOT_WORKING = "fan_not_working"
    OUT_OF_RANGE = "out_of_range"
    NO_FAULT = "no_fault"


class FaultDetectionResult(BaseModel):
    """
    Output from fault detection module.
    Identifies hardware or sensor faults.
    """
    has_fault: bool = Field(..., description="Whether a fault was detected")
    fault_type: FaultType = Field(..., description="Type of fault detected")
    affected_sensor: Optional[str] = Field(None, description="Which sensor is faulty (pm25, co2, etc.)")
    severity: Literal["low", "medium", "high"] = Field("low", description="Fault severity")
    details: str = Field(..., description="Detailed fault description")


class SelfHealingAction(BaseModel):
    """
    Output from self-healing module.
    Describes corrective action taken.
    """
    action_taken: str = Field(..., description="Description of healing action")
    ignored_sensors: List[str] = Field(default_factory=list, description="Sensors being ignored")
    fallback_logic: Optional[str] = Field(None, description="Fallback control logic being used")
    success: bool = Field(..., description="Whether healing action was successful")


# ============= CONTROL RESPONSE =============

class ControlResponse(BaseModel):
    """
    Response sent back to ESP32 with control commands.
    
    ESP32 expects:
    {
        "fan_on": true,
        "fan_intensity": 75,
        "timestamp": "2026-02-13T10:30:05"
    }
    """
    fan_on: bool
    fan_intensity: int = Field(..., ge=0, le=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============= BLOCKCHAIN MODELS =============

class BlockchainLog(BaseModel):
    """
    Data structure for blockchain logging.
    Critical decisions and faults are logged to blockchain.
    """
    event_type: Literal["decision", "fault", "healing"] = Field(..., description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    device_id: str
    data: dict = Field(..., description="Event-specific data")
    hash: Optional[str] = Field(None, description="Transaction hash (if real blockchain)")


# ============= DASHBOARD MODELS =============

class DashboardData(BaseModel):
    """
    Aggregated data for frontend dashboard.
    """
    current_reading: SensorReading
    prediction: SmokePrediction
    classification: AirTypeClassification
    control_status: ControlResponse
    recent_faults: List[FaultDetectionResult]
    recent_logs: List[BlockchainLog]
    system_health: dict
