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
    
    def _generate_mock_response(self, context: Dict[str, Any]) -> AirTypeClassification:
        """Generate intelligent mock response based on sensor patterns."""
        current: SensorReading = context.get("current_reading")
        
        # Classification logic based on sensor patterns
        pm25, co2, co, voc = current.pm25, current.co2, current.co, current.voc
        
        # Clean air
        if pm25 < 35 and co < 10 and voc < 100:
            return AirTypeClassification(
                air_type=SmokeEventType.CLEAN,
                confidence=0.9,
                reasoning=f"All values low: PM2.5={pm25:.1f}, CO={co:.1f}, VOC={voc:.1f}"
            )
        
        # Cigarette smoke: High PM2.5, moderate CO, high VOC
        if pm25 > 100 and 20 < co < 60 and voc > 200:
            return AirTypeClassification(
                air_type=SmokeEventType.CIGARETTE,
                confidence=0.85,
                reasoning=f"Pattern matches cigarette: High PM2.5={pm25:.1f}, moderate CO={co:.1f}, high VOC={voc:.1f}"
            )
        
        # Vehicle exhaust: High PM2.5, high CO, elevated CO2
        if pm25 > 80 and co > 50 and co2 > 600:
            return AirTypeClassification(
                air_type=SmokeEventType.VEHICLE,
                confidence=0.8,
                reasoning=f"Pattern matches vehicle: PM2.5={pm25:.1f}, high CO={co:.1f}, elevated CO2={co2:.1f}"
            )
        
        # Cooking smoke: Very high PM2.5, high VOC
        if pm25 > 150 and voc > 250:
            return AirTypeClassification(
                air_type=SmokeEventType.COOKING,
                confidence=0.75,
                reasoning=f"Pattern matches cooking: Very high PM2.5={pm25:.1f}, high VOC={voc:.1f}"
            )
        
        # Chemical fumes: Low PM2.5, very high VOC
        if pm25 < 50 and voc > 400:
            return AirTypeClassification(
                air_type=SmokeEventType.CHEMICAL,
                confidence=0.7,
                reasoning=f"Pattern matches chemical: Low PM2.5={pm25:.1f}, very high VOC={voc:.1f}"
            )
        
        # Unknown/mixed
        return AirTypeClassification(
            air_type=SmokeEventType.UNKNOWN,
            confidence=0.5,
            reasoning=f"Mixed or unclear pattern: PM2.5={pm25:.1f}, CO={co:.1f}, VOC={voc:.1f}"
        )
