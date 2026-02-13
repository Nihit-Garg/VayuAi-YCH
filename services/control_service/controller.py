"""
Control Service
Manages fan control logic and manual overrides
"""

from typing import Dict, Optional
from datetime import datetime
import logging

from models.schemas import ControlResponse, ControlDecision

logger = logging.getLogger(__name__)


class ControlService:
    """
    Service for managing control commands and overrides.
    
    Responsibilities:
    - Track current control state per device
    - Handle manual overrides
    - Provide control status
    """
    
    def __init__(self):
        """Initialize control state storage."""
        # Store current control state per device
        self.control_state: Dict[str, ControlResponse] = {}
        
        # Store manual override state
        self.manual_overrides: Dict[str, Dict] = {}
        
        logger.info("ControlService initialized")
    
    def update_control_state(
        self, 
        device_id: str, 
        decision: ControlDecision
    ) -> ControlResponse:
        """
        Update control state based on AI decision.
        
        Args:
            device_id: Target ESP32 device
            decision: Control decision from AI agent
        
        Returns:
            ControlResponse to send to ESP32
        """
        # Check if manual override is active
        if device_id in self.manual_overrides:
            logger.info(f"Manual override active for {device_id}, ignoring AI decision")
            return self.control_state[device_id]
        
        # Create control response
        response = ControlResponse(
            fan_on=decision.fan_on,
            fan_intensity=decision.fan_intensity,
            timestamp=datetime.utcnow()
        )
        
        # Store state
        self.control_state[device_id] = response
        
        logger.info(f"Updated control state for {device_id}: {response.dict()}")
        return response
    
    def set_manual_override(
        self,
        device_id: str,
        fan_on: bool,
        fan_intensity: int
    ) -> ControlResponse:
        """
        Set manual override for a device.
        
        Args:
            device_id: Target ESP32 device
            fan_on: Force fan ON/OFF
            fan_intensity: Force fan intensity (0-100)
        
        Returns:
            ControlResponse with override values
        """
        response = ControlResponse(
            fan_on=fan_on,
            fan_intensity=fan_intensity,
            timestamp=datetime.utcnow()
        )
        
        self.manual_overrides[device_id] = {
            "active": True,
            "set_at": datetime.utcnow(),
            "response": response
        }
        
        self.control_state[device_id] = response
        
        logger.info(f"Manual override set for {device_id}: fan_on={fan_on}, intensity={fan_intensity}")
        return response
    
    def clear_manual_override(self, device_id: str) -> None:
        """
        Clear manual override and return to automatic control.
        
        Args:
            device_id: Target ESP32 device
        """
        if device_id in self.manual_overrides:
            del self.manual_overrides[device_id]
            logger.info(f"Manual override cleared for {device_id}")
    
    def get_status(self, device_id: str) -> Dict:
        """
        Get current control status for a device.
        
        Args:
            device_id: Target ESP32 device
        
        Returns:
            Control status including override state
        """
        if device_id not in self.control_state:
            raise ValueError(f"No control state for device {device_id}")
        
        current_state = self.control_state[device_id]
        is_override = device_id in self.manual_overrides
        
        return {
            "device_id": device_id,
            "fan_on": current_state.fan_on,
            "fan_intensity": current_state.fan_intensity,
            "last_update": current_state.timestamp,
            "manual_override_active": is_override,
            "override_info": self.manual_overrides.get(device_id) if is_override else None
        }
