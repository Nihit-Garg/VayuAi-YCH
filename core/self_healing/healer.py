"""
Self-Healing Module
Implements corrective actions when faults are detected
"""

from typing import List, Optional
import logging

from models.schemas import (
    FaultDetectionResult,
    SelfHealingAction,
    FaultType,
    SensorReading,
    ControlDecision
)

logger = logging.getLogger(__name__)


class SelfHealingModule:
    """
    Implements self-healing strategies when faults are detected.
    
    Healing strategies:
    1. Ignore faulty sensor and use others
    2. Use fallback control logic
    3. Apply sensor value interpolation
    4. Switch to safe mode (fan always ON)
    """
    
    def __init__(self):
        """Initialize self-healing module."""
        self.ignored_sensors: List[str] = []
        self.safe_mode_active: bool = False
        logger.info("SelfHealingModule initialized")
    
    def heal(
        self,
        fault: FaultDetectionResult,
        current_reading: SensorReading
    ) -> SelfHealingAction:
        """
        Apply healing strategy based on detected fault.
        
        Args:
            fault: Detected fault information
            current_reading: Current sensor reading
        
        Returns:
            SelfHealingAction describing what was done
        """
        if not fault.has_fault:
            return SelfHealingAction(
                action_taken="No healing needed",
                success=True
            )
        
        # Handle different fault types
        if fault.fault_type == FaultType.SENSOR_STUCK:
            return self._heal_stuck_sensor(fault)
        
        elif fault.fault_type == FaultType.OUT_OF_RANGE:
            return self._heal_out_of_range(fault)
        
        elif fault.fault_type == FaultType.INCONSISTENT_READING:
            return self._heal_inconsistent_reading(fault)
        
        elif fault.fault_type == FaultType.FAN_NOT_WORKING:
            return self._heal_fan_fault(fault)
        
        else:
            return SelfHealingAction(
                action_taken="Unknown fault type, no healing applied",
                success=False
            )
    
    def _heal_stuck_sensor(self, fault: FaultDetectionResult) -> SelfHealingAction:
        """
        Heal stuck sensor by ignoring it.
        
        Args:
            fault: Fault information
        
        Returns:
            SelfHealingAction
        """
        affected_sensor = fault.affected_sensor
        
        if affected_sensor not in self.ignored_sensors:
            self.ignored_sensors.append(affected_sensor)
            logger.warning(f"Ignoring stuck sensor: {affected_sensor}")
        
        return SelfHealingAction(
            action_taken=f"Ignoring stuck {affected_sensor} sensor",
            ignored_sensors=self.ignored_sensors.copy(),
            fallback_logic="Using remaining sensors for control decisions",
            success=True
        )
    
    def _heal_out_of_range(self, fault: FaultDetectionResult) -> SelfHealingAction:
        """
        Heal out-of-range sensor by clamping or ignoring.
        
        Args:
            fault: Fault information
        
        Returns:
            SelfHealingAction
        """
        affected_sensor = fault.affected_sensor
        
        if affected_sensor not in self.ignored_sensors:
            self.ignored_sensors.append(affected_sensor)
            logger.warning(f"Ignoring out-of-range sensor: {affected_sensor}")
        
        return SelfHealingAction(
            action_taken=f"Ignoring out-of-range {affected_sensor} sensor",
            ignored_sensors=self.ignored_sensors.copy(),
            fallback_logic="Using remaining sensors for control decisions",
            success=True
        )
    
    def _heal_inconsistent_reading(self, fault: FaultDetectionResult) -> SelfHealingAction:
        """
        Heal inconsistent readings by ignoring suspect sensor.
        
        Args:
            fault: Fault information
        
        Returns:
            SelfHealingAction
        """
        affected_sensor = fault.affected_sensor
        
        if affected_sensor not in self.ignored_sensors:
            self.ignored_sensors.append(affected_sensor)
            logger.warning(f"Ignoring inconsistent sensor: {affected_sensor}")
        
        return SelfHealingAction(
            action_taken=f"Ignoring inconsistent {affected_sensor} sensor",
            ignored_sensors=self.ignored_sensors.copy(),
            fallback_logic="Using remaining sensors for control decisions",
            success=True
        )
    
    def _heal_fan_fault(self, fault: FaultDetectionResult) -> SelfHealingAction:
        """
        Heal fan fault by activating safe mode.
        
        Args:
            fault: Fault information
        
        Returns:
            SelfHealingAction
        """
        self.safe_mode_active = True
        logger.error("Fan fault detected, activating safe mode")
        
        return SelfHealingAction(
            action_taken="Activated safe mode due to fan fault",
            fallback_logic="Manual intervention required",
            success=True
        )
    
    def get_corrected_reading(self, reading: SensorReading) -> SensorReading:
        """
        Get corrected sensor reading with faulty sensors ignored.
        
        For ignored sensors, we can:
        - Use last known good value
        - Use average of other sensors
        - Use a safe default value
        
        Args:
            reading: Original sensor reading
        
        Returns:
            Corrected sensor reading
        """
        # For hackathon simplicity, just return original reading
        # In production, implement interpolation or averaging
        return reading
    
    def should_use_safe_mode(self) -> bool:
        """
        Check if system should operate in safe mode.
        
        Safe mode: Fan always ON at medium intensity
        
        Returns:
            True if safe mode is active
        """
        return self.safe_mode_active
    
    def get_safe_mode_control(self) -> ControlDecision:
        """
        Get safe mode control decision.
        
        Returns:
            ControlDecision for safe mode (fan ON at 50%)
        """
        return ControlDecision(
            fan_on=True,
            fan_intensity=50,
            reasoning="Safe mode active due to system fault",
            override_reason="System fault detected"
        )
    
    def reset(self) -> None:
        """
        Reset self-healing state.
        Useful for testing or after manual intervention.
        """
        self.ignored_sensors.clear()
        self.safe_mode_active = False
        logger.info("Self-healing module reset")
