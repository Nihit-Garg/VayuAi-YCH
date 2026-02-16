"""
Sensor Data Ingestion Service
Handles storage and retrieval of sensor readings in memory
"""

from typing import List, Dict, Optional
from collections import deque, defaultdict
from datetime import datetime, timedelta
import logging

from models.schemas import SensorReading
from config.settings import settings

logger = logging.getLogger(__name__)


class SensorIngestionService:
    """
    Service for managing sensor data ingestion and context storage.
    
    Responsibilities:
    - Store incoming sensor readings in memory
    - Maintain rolling window of recent readings per device
    - Provide context for AI agents
    - Track device connection status
    """
    
    def __init__(self):
        """
        Initialize in-memory storage for sensor data.
        
        Storage structure:
        {
            "ESP32_001": deque([reading1, reading2, ...], maxlen=MAX_CONTEXT_SIZE),
            "ESP32_002": deque([...]),
            ...
        }
        """
        self.device_readings: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=settings.MAX_CONTEXT_SIZE)
        )
        self.device_last_seen: Dict[str, datetime] = {}
        logger.info("SensorIngestionService initialized")
    
    def store_reading(self, reading: SensorReading) -> None:
        """
        Store a sensor reading in the context buffer.
        
        Args:
            reading: Validated sensor reading from ESP32
        """
        device_id = reading.device_id
        self.device_readings[device_id].append(reading)
        self.device_last_seen[device_id] = datetime.utcnow()
        
        logger.debug(f"Stored reading for {device_id}, buffer size: {len(self.device_readings[device_id])}")
    
    def get_recent_context(
        self, 
        device_id: str, 
        window_size: Optional[int] = None
    ) -> List[SensorReading]:
        """
        Get recent sensor readings for AI agent context.
        
        Args:
            device_id: ESP32 device identifier
            window_size: Number of recent readings (default: PREDICTION_WINDOW_SIZE)
        
        Returns:
            List of recent sensor readings, ordered oldest to newest
        """
        if window_size is None:
            window_size = settings.PREDICTION_WINDOW_SIZE
        
        readings = list(self.device_readings[device_id])
        return readings[-window_size:] if len(readings) > window_size else readings
    
    def get_device_status(self, device_id: str) -> Dict:
        """
        Get current status of a sensor device.
        
        Args:
            device_id: ESP32 device identifier
        
        Returns:
            Device status including last seen time and reading count
        """
        if device_id not in self.device_readings:
            raise ValueError(f"Device {device_id} not found")
        
        last_seen = self.device_last_seen.get(device_id)
        is_online = False
        if last_seen:
            is_online = (datetime.utcnow() - last_seen) < timedelta(minutes=5)
        
        return {
            "device_id": device_id,
            "is_online": is_online,
            "last_seen": last_seen,
            "reading_count": len(self.device_readings[device_id]),
            "buffer_size": settings.MAX_CONTEXT_SIZE
        }
    
    def get_history(self, device_id: str, limit: int = 50) -> List[Dict]:
        """
        Get historical sensor readings.
        
        Args:
            device_id: ESP32 device identifier
            limit: Maximum number of readings to return
        
        Returns:
            List of sensor readings as dictionaries
        """
        if device_id not in self.device_readings:
            return []
        
        readings = list(self.device_readings[device_id])
        recent_readings = readings[-limit:] if len(readings) > limit else readings
        
        return [reading.dict() for reading in recent_readings]
    
    def get_history_by_time_range(self, device_id: str, hours: float) -> List[Dict]:
        """
        Get historical sensor readings within a time range.
        
        Args:
            device_id: ESP32 device identifier
            hours: Number of hours to look back from now
        
        Returns:
            List of sensor readings as dictionaries, filtered by time range
        """
        if device_id not in self.device_readings:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        readings = list(self.device_readings[device_id])
        
        # Filter readings within the time range
        filtered_readings = [
            reading for reading in readings 
            if reading.timestamp >= cutoff_time
        ]
        
        return [reading.dict() for reading in filtered_readings]
    
    def get_latest_reading(self, device_id: str) -> Optional[SensorReading]:
        """
        Get the most recent sensor reading for a device.
        
        Args:
            device_id: ESP32 device identifier
        
        Returns:
            Latest sensor reading or None if no readings exist
        """
        if device_id not in self.device_readings or len(self.device_readings[device_id]) == 0:
            return None
        
        return list(self.device_readings[device_id])[-1]
    
    def list_devices(self) -> List[str]:
        """
        List all registered device IDs.
        
        Returns:
            List of device IDs
        """
        return list(self.device_readings.keys())
    
    def clear_device_data(self, device_id: str) -> None:
        """
        Clear all data for a specific device.
        Useful for testing or device reset.
        
        Args:
            device_id: ESP32 device identifier
        """
        if device_id in self.device_readings:
            del self.device_readings[device_id]
            del self.device_last_seen[device_id]
            logger.info(f"Cleared data for device {device_id}")
