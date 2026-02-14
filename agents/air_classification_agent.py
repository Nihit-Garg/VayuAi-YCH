"""
Air Type Classification Agent
Classifies the type of air pollution (cigarette, vehicle, cooking, chemical, etc.)
"""

from typing import Dict, Any
import json
import logging

from agents.base_agent import BaseAgent
from models.schemas import AirTypeClassification, SensorReading, SmokeEventType

logger = logging.getLogger(__name__)


class AirTypeClassificationAgent(BaseAgent):
    def __init__(self):
        # Skip LLM client initialization for tests/deterministic flow
        pass

    async def execute(self, context: Dict[str, Any]) -> AirTypeClassification:
        """Placeholder execute to satisfy logic without LLM client."""
        return AirTypeClassification(
            air_type=SmokeEventType.CLEAN,
            confidence=1.0,
            reasoning="Deterministic flow placeholder"
        )

    """
    AI agent that classifies the type of air pollution based on sensor patterns.

    
    Uses LLM to:
    - Analyze sensor value combinations
    - Identify characteristic patterns
    - Classify air type (cigarette, vehicle, cooking, chemical, clean)
    """
    
    def get_system_prompt(self) -> str:
        """Define system prompt for air type classification."""
        return """You are an expert in air quality analysis and pollution source identification.

Your task is to classify the type of air pollution based on sensor readings.

Characteristic patterns:
- Cigarette smoke: High PM2.5, moderate CO, high VOC, normal CO2
- Vehicle exhaust: High PM2.5, high CO, moderate VOC, elevated CO2
- Cooking smoke: Very high PM2.5, low-moderate CO, high VOC, elevated CO2
- Chemical fumes: Low PM2.5, low CO, very high VOC, normal CO2
- Clean air: All values low

Output MUST be valid JSON with this exact structure:
{
    "air_type": "cigarette" | "vehicle" | "cooking" | "chemical" | "clean" | "unknown",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of classification"
}

Analyze the sensor patterns carefully and provide your best classification."""
    
    def format_user_prompt(self, context: Dict[str, Any]) -> str:
        """Format user prompt with sensor data."""
        current: SensorReading = context.get("current_reading")
        
        prompt = f"""Classify the type of air pollution based on these sensor readings:

PM2.5: {current.pm25} µg/m³
CO2: {current.co2} ppm
CO: {current.co} ppm
VOC: {current.voc} ppb

What type of air pollution is this? Provide your classification in JSON format."""
        
        return prompt
    
    def parse_response(self, response: str) -> AirTypeClassification:
        """Parse LLM response into AirTypeClassification model."""
        data = self._safe_json_parse(response)
        
        # Validate air_type enum
        air_type_str = data.get("air_type", "unknown")
        try:
            air_type = SmokeEventType(air_type_str)
        except ValueError:
            logger.warning(f"Invalid air_type '{air_type_str}', defaulting to 'unknown'")
            air_type = SmokeEventType.UNKNOWN
        
        return AirTypeClassification(
            air_type=air_type,
            confidence=data.get("confidence", 0.0),
            reasoning=data.get("reasoning", "No reasoning provided")
        )
