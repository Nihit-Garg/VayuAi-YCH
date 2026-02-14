"""
Control Decision Agent
Makes intelligent fan control decisions based on sensor data and predictions
"""

from typing import Dict, Any, List
import json
import logging

from agents.base_agent import BaseAgent
from models.schemas import ControlDecision, SensorReading, SmokePrediction, AirTypeClassification

logger = logging.getLogger(__name__)



class ControlDecisionAgent(BaseAgent):
    def __init__(self):
        # Skip LLM client initialization
        pass

    async def execute(self, context: Dict[str, Any]) -> ControlDecision:
        """
        Execute control logic. 
        Prioritizes deterministic safety rules over LLM for speed and reliability in emergencies.
        """
        current: SensorReading = context.get("current_reading")
        prediction: SmokePrediction = context.get("prediction")
        classification: AirTypeClassification = context.get("classification")
        
        # ---------------------------------------------------------
        # 1. Critical Safety Overrides (Deterministic)
        # ---------------------------------------------------------
        reasons = []
        fan_intensity = 0
        
        # High CO/Smoke (Immediate Danger)
        # Using .co or .mq2_raw if available (assuming SensorReading has them)
        co_val = getattr(current, 'co', 0)
        mq2_val = getattr(current, 'mq2_raw', 0)
        
        if co_val > 200 or mq2_val > 400:
            fan_intensity = 100
            reasons.append("CRITICAL: High Smoke/CO levels detected.")

        # Predicted Peak (Pre-emptive)
        if prediction and prediction.will_peak and prediction.confidence > 0.8:
            fan_intensity = max(fan_intensity, 100)
            reasons.append(f"PRE-EMPTIVE: Smoke peak predicted ({prediction.estimated_peak_value:.0f}).")

        # PM2.5 Thresholds
        if current.pm25 > 150:
            fan_intensity = max(fan_intensity, 100)
            reasons.append("Hazardous PM2.5 levels.")
        elif current.pm25 > 75:
            fan_intensity = max(fan_intensity, 75)
            reasons.append("Unhealthy PM2.5 levels.")
            
        # ---------------------------------------------------------
        # 2. Return Decision if Safety Logic Triggered
        # ---------------------------------------------------------
        if fan_intensity > 0:
            return ControlDecision(
                fan_on=True,
                fan_intensity=fan_intensity,
                reasoning="; ".join(reasons),
                override_reason="Safety Protocol Activated"
            )

        # ---------------------------------------------------------
        # 3. Fallback to LLM for Complex/Nuanced Decisions (Comfort)
        # ---------------------------------------------------------
        # If air is relatively clean but maybe needs adjustment (e.g. VOCs, slight stuffiness)
        # This section is removed as per instruction to replace LLM methods with deterministic ones.
        # The instruction implies that if no safety logic is triggered, the agent should return a default
        # or no action, rather than deferring to an LLM.
        
        # If no critical safety or pre-emptive conditions met, and no other deterministic rules apply,
        # the fan remains off or at a default state.
        return ControlDecision(
            fan_on=False,
            fan_intensity=0,
            reasoning="No critical conditions detected. Fan off.",
            override_reason=None
        )

    # placeholder implementations to satisfy BaseAgent contract
    def get_system_prompt(self) -> str: return ""
    def format_user_prompt(self, context: Dict[str, Any]) -> str: return ""
    def parse_response(self, response: str) -> Any: return None

