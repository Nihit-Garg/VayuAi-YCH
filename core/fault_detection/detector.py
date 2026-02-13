"""
Fault Detection Module
Detects hardware and sensor faults using rule-based logic
"""

from typing import List, Dict, Optional
import logging
from collections import Counter

from models.schemas import (
    SensorReading, 
    FaultDetectionResult, 
    FaultType
)
from config.settings import settings

logger = logging.getLogger(__name__)


class FaultDetector:
    """
    Detects faults in sensor hardware and readings.
    
    Fault types:
    1. Sensor stuck (same value repeated multiple times)
    2. Out of range (values outside physical limits)
    3. Inconsistent readings (impossible combinations)
    4. Fan not working (control sent but no effect on readings)
    """
    
    def __init__(self):
        """Initialize fault detector."""
        self.stuck_value_threshold = settings.STUCK_VALUE_THRESHOLD
        logger.info("FaultDetector initialized")
    
    def detect_faults(
        self, 
        current_reading: SensorReading,
        recent_readings: List[SensorReading]
    ) -> FaultDetectionResult:
        """
        Detect faults in sensor data.
        
        Args:
            current_reading: Latest sensor reading
            recent_readings: Recent historical readings
        
        Returns:
            FaultDetectionResult with fault information
        """
        # Check for out-of-range values
        range_fault = self._check_out_of_range(current_reading)
        if range_fault:
            return range_fault
        
        # Check for stuck sensors
        if len(recent_readings) >= self.stuck_value_threshold:
            stuck_fault = self._check_stuck_sensor(current_reading, recent_readings)
            if stuck_fault:
                return stuck_fault
        
        # Check for inconsistent readings
        inconsistent_fault = self._check_inconsistent_readings(current_reading)
        if inconsistent_fault:
            return inconsistent_fault
        
        # No fault detected
        return FaultDetectionResult(
            has_fault=False,
            fault_type=FaultType.NO_FAULT,
            severity="low",
            details="All sensors operating normally"
        )
    
    def _check_out_of_range(self, reading: SensorReading) -> Optional[FaultDetectionResult]:
        """
        Check if any sensor value is outside physical limits.
        
        Args:
            reading: Sensor reading to check
        
        Returns:
            FaultDetectionResult if fault detected, None otherwise
        """
        faults = []
        
        if not (settings.PM25_MIN <= reading.pm25 <= settings.PM25_MAX):
            faults.append(f"PM2.5={reading.pm25} out of range [{settings.PM25_MIN}, {settings.PM25_MAX}]")
        
        if not (settings.CO2_MIN <= reading.co2 <= settings.CO2_MAX):
            faults.append(f"CO2={reading.co2} out of range [{settings.CO2_MIN}, {settings.CO2_MAX}]")
        
        if not (settings.CO_MIN <= reading.co <= settings.CO_MAX):
            faults.append(f"CO={reading.co} out of range [{settings.CO_MIN}, {settings.CO_MAX}]")
        
        if not (settings.VOC_MIN <= reading.voc <= settings.VOC_MAX):
            faults.append(f"VOC={reading.voc} out of range [{settings.VOC_MIN}, {settings.VOC_MAX}]")
        
        if faults:
            return FaultDetectionResult(
                has_fault=True,
                fault_type=FaultType.OUT_OF_RANGE,
                affected_sensor=faults[0].split("=")[0],  # First faulty sensor
                severity="high",
                details="; ".join(faults)
            )
        
        return None
    
    def _check_stuck_sensor(
        self, 
        current: SensorReading, 
        recent: List[SensorReading]
    ) -> Optional[FaultDetectionResult]:
        """
        Check if any sensor is stuck (repeating same value).
        
        Args:
            current: Current reading
            recent: Recent readings
        
        Returns:
            FaultDetectionResult if stuck sensor detected, None otherwise
        """
        # Check each sensor type
        sensors = {
            "pm25": [r.pm25 for r in recent[-self.stuck_value_threshold:]],
            "co2": [r.co2 for r in recent[-self.stuck_value_threshold:]],
            "co": [r.co for r in recent[-self.stuck_value_threshold:]],
            "voc": [r.voc for r in recent[-self.stuck_value_threshold:]]
        }
        
        for sensor_name, values in sensors.items():
            # If all values are identical, sensor is stuck
            if len(set(values)) == 1:
                return FaultDetectionResult(
                    has_fault=True,
                    fault_type=FaultType.SENSOR_STUCK,
                    affected_sensor=sensor_name,
                    severity="medium",
                    details=f"{sensor_name.upper()} sensor stuck at value {values[0]}"
                )
        
        return None
    
    def _check_inconsistent_readings(
        self, 
        reading: SensorReading
    ) -> Optional[FaultDetectionResult]:
        """
        Check for physically impossible sensor combinations.
        
        Examples:
        - Very high PM2.5 but all other values normal (unlikely)
        - High CO but normal CO2 (combustion produces both)
        
        Args:
            reading: Sensor reading to check
        
        Returns:
            FaultDetectionResult if inconsistency detected, None otherwise
        """
        # Rule: Very high PM2.5 (>200) but CO and VOC both very low (<10)
        # This is unlikely - smoke should have some CO or VOC
        if reading.pm25 > 200 and reading.co < 10 and reading.voc < 10:
            return FaultDetectionResult(
                has_fault=True,
                fault_type=FaultType.INCONSISTENT_READING,
                affected_sensor="pm25",
                severity="medium",
                details=f"High PM2.5 ({reading.pm25}) but very low CO ({reading.co}) and VOC ({reading.voc})"
            )
        
        # Rule: Very high CO (>100) but normal CO2 (<500)
        # Combustion produces both, so high CO should mean elevated CO2
        if reading.co > 100 and reading.co2 < 500:
            return FaultDetectionResult(
                has_fault=True,
                fault_type=FaultType.INCONSISTENT_READING,
                affected_sensor="co",
                severity="medium",
                details=f"High CO ({reading.co}) but normal CO2 ({reading.co2})"
            )
        
        return None
    
    def check_fan_fault(
        self,
        recent_readings: List[SensorReading],
        fan_was_on: bool
    ) -> Optional[FaultDetectionResult]:
        """
        Check if fan is not working (control sent but no effect).
        
        This requires comparing readings before and after fan activation.
        If fan was ON but PM2.5 didn't decrease, fan might be faulty.
        
        Args:
            recent_readings: Recent sensor readings
            fan_was_on: Whether fan was commanded ON
        
        Returns:
            FaultDetectionResult if fan fault detected, None otherwise
        """
        # TODO: Implement fan effectiveness check
        # This requires tracking control commands and their effects
        # For hackathon, this can be a placeholder
        
        return None
