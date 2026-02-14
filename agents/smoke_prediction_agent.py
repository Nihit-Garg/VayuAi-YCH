"""
Smoke Prediction Agent
Predicts if smoke levels will peak in the near future based on recent trends
"""

from typing import Dict, Any, List
import json
import logging

from agents.base_agent import BaseAgent
from models.schemas import SmokePrediction, SensorReading

logger = logging.getLogger(__name__)


class SmokePredictionAgent(BaseAgent):
    """
    AI agent that analyzes recent sensor trends to predict smoke events.
    
    Uses LLM to:
    - Analyze PM2.5, CO, VOC trends
    - Detect rising patterns
    - Predict if levels will peak soon
    - Estimate peak value
    """
    
    def get_system_prompt(self) -> str:
        """Define system prompt for smoke prediction."""
        return """You are an expert air quality analyst specializing in smoke event prediction.

Your task is to analyze recent sensor readings and predict if smoke levels will peak in the next few readings.

Consider:
- PM2.5 trends (primary smoke indicator)
- CO and VOC levels (supporting indicators)
- Rate of change in values
- Historical patterns

Output MUST be valid JSON with this exact structure:
{
    "will_peak": true/false,
    "confidence": 0.0-1.0,
    "estimated_peak_value": number or null,
    "reasoning": "brief explanation of your prediction"
}

Be conservative with predictions. Only predict a peak if you see clear rising trends."""
    
    def format_user_prompt(self, context: Dict[str, Any]) -> str:
        """Format user prompt with sensor data."""
        readings: List[SensorReading] = context.get("recent_readings", [])
        current: SensorReading = context.get("current_reading")
        
        # Format readings for LLM
        readings_text = []
        for i, reading in enumerate(readings):
            readings_text.append(
                f"Reading {i+1}: PM2.5={reading.pm25}, CO2={reading.co2}, "
                f"CO={reading.co}, VOC={reading.voc}"
            )
        
        prompt = f"""Analyze these recent sensor readings and predict if smoke levels will peak soon:

{chr(10).join(readings_text)}

Current reading: PM2.5={current.pm25}, CO2={current.co2}, CO={current.co}, VOC={current.voc}

Based on these trends, will smoke levels peak in the next few readings?
Provide your prediction in JSON format."""
        
        return prompt
    
    def parse_response(self, response: str) -> SmokePrediction:
        """Parse LLM response into SmokePrediction model."""
        data = self._safe_json_parse(response)
        
        return SmokePrediction(
            will_peak=data.get("will_peak", False),
            confidence=data.get("confidence", 0.0),
            estimated_peak_value=data.get("estimated_peak_value"),
            reasoning=data.get("reasoning", "No reasoning provided")
        )
    
    def _generate_mock_response(self, context: Dict[str, Any]) -> SmokePrediction:
        """Generate intelligent mock response based on sensor trends."""
        readings: List[SensorReading] = context.get("recent_readings", [])
        current: SensorReading = context.get("current_reading")
        
        # Analyze PM2.5 trend
        if len(readings) >= 3:
            recent_pm25 = [r.pm25 for r in readings[-3:]]
            avg_increase = (recent_pm25[-1] - recent_pm25[0]) / len(recent_pm25)
            
            # Predict peak if PM2.5 is rising rapidly
            will_peak = avg_increase > 10 and current.pm25 > 100
            confidence = min(0.95, 0.6 + (avg_increase / 50))
            estimated_peak = current.pm25 + (avg_increase * 2) if will_peak else None
            
            reasoning = f"PM2.5 trend: {recent_pm25[0]:.1f} → {current.pm25:.1f} ({'rising' if avg_increase > 0 else 'stable/falling'})"
        else:
            # Not enough data
            will_peak = current.pm25 > 150
            confidence = 0.5
            estimated_peak = current.pm25 * 1.2 if will_peak else None
            reasoning = "Limited historical data, prediction based on current level"
        
        return SmokePrediction(
            will_peak=will_peak,
            confidence=confidence,
            estimated_peak_value=estimated_peak,
            reasoning=reasoning
        )
