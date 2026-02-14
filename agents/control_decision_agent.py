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
    """
    AI agent that decides fan control actions.
    
    Uses LLM to:
    - Consider current sensor values
    - Factor in smoke predictions
    - Account for air type classification
    - Decide optimal fan control (ON/OFF, intensity)
    - Provide reasoning for decisions
    """
    
    def get_system_prompt(self) -> str:
        """Define system prompt for control decisions."""
        return """You are an intelligent air quality control system making fan control decisions.

Your task is to decide whether to turn the fan ON/OFF and at what intensity (0-100).

Decision guidelines:
- Turn fan ON if PM2.5 > 35 OR CO > 50 OR VOC > 200
- Higher intensity for worse air quality
- If smoke peak is predicted, preemptively increase intensity
- For cigarette smoke: high intensity (75-100)
- For cooking smoke: moderate intensity (50-75)
- For vehicle exhaust: high intensity (75-100)
- For chemical fumes: maximum intensity (100)
- Turn fan OFF if all values are low and no peak predicted

Available fan intensities: 0, 25, 50, 75, 100

Output MUST be valid JSON with this exact structure:
{
    "fan_on": true/false,
    "fan_intensity": 0-100,
    "reasoning": "brief explanation of decision",
    "override_reason": "explanation if overriding normal logic" or null
}

Make intelligent decisions that balance air quality improvement with energy efficiency."""
    
    def format_user_prompt(self, context: Dict[str, Any]) -> str:
        """Format user prompt with all available context."""
        current: SensorReading = context.get("current_reading")
        prediction: SmokePrediction = context.get("prediction")
        classification: AirTypeClassification = context.get("classification")
        
        prompt = f"""Make a fan control decision based on this information:

Current Sensor Readings:
- PM2.5: {current.pm25} µg/m³
- CO2: {current.co2} ppm
- CO: {current.co} ppm
- VOC: {current.voc} ppb

Smoke Prediction:
- Will peak: {prediction.will_peak}
- Confidence: {prediction.confidence}
- Reasoning: {prediction.reasoning}

Air Type Classification:
- Type: {classification.air_type.value}
- Confidence: {classification.confidence}
- Reasoning: {classification.reasoning}

Should the fan be ON or OFF? At what intensity? Provide your decision in JSON format."""
        
        return prompt
    
    def parse_response(self, response: str) -> ControlDecision:
        """Parse LLM response into ControlDecision model."""
        data = self._safe_json_parse(response)
        
        # Validate fan_intensity is in allowed levels
        fan_intensity = data.get("fan_intensity", 0)
        allowed_levels = [0, 25, 50, 75, 100]
        
        # Round to nearest allowed level
        fan_intensity = min(allowed_levels, key=lambda x: abs(x - fan_intensity))
        
        return ControlDecision(
            fan_on=data.get("fan_on", False),
            fan_intensity=fan_intensity,
            reasoning=data.get("reasoning", "No reasoning provided"),
            override_reason=data.get("override_reason")
        )
    
    def _generate_mock_response(self, context: Dict[str, Any]) -> ControlDecision:
        """Generate intelligent mock control decision based on sensor data."""
        current: SensorReading = context.get("current_reading")
        prediction: SmokePrediction = context.get("prediction")
        classification: AirTypeClassification = context.get("classification")
        
        pm25, co2, co, voc = current.pm25, current.co2, current.co, current.voc
        
        # Decision logic
        fan_on = False
        fan_intensity = 0
        reasoning_parts = []
        
        # Check thresholds
        if pm25 > 35:
            fan_on = True
            reasoning_parts.append(f"PM2.5 elevated ({pm25:.1f})")
        
        if co > 50:
            fan_on = True
            reasoning_parts.append(f"CO high ({co:.1f})")
        
        if voc > 200:
            fan_on = True
            reasoning_parts.append(f"VOC elevated ({voc:.1f})")
        
        # Determine intensity based on severity and air type
        if fan_on:
            # Base intensity on worst pollutant
            max_pm25_ratio = pm25 / 150  # 150 is very high
            max_co_ratio = co / 100
            max_voc_ratio = voc / 500
            severity = max(max_pm25_ratio, max_co_ratio, max_voc_ratio)
            
            # Adjust for air type
            air_type = classification.air_type.value
            if air_type == "chemical":
                fan_intensity = 100
                reasoning_parts.append("Chemical fumes detected - max ventilation")
            elif air_type == "cigarette" or air_type == "vehicle":
                fan_intensity = 75 if severity < 0.8 else 100
                reasoning_parts.append(f"{air_type.capitalize()} smoke - high ventilation")
            elif air_type == "cooking":
                fan_intensity = 50 if severity < 0.6 else 75
                reasoning_parts.append("Cooking smoke - moderate ventilation")
            else:
                # General intensity based on severity
                if severity > 0.8:
                    fan_intensity = 100
                elif severity > 0.6:
                    fan_intensity = 75
                elif severity > 0.4:
                    fan_intensity = 50
                else:
                    fan_intensity = 25
            
            # Boost if peak predicted
            if prediction.will_peak and prediction.confidence > 0.6:
                if fan_intensity < 100:
                    fan_intensity = min(100, fan_intensity + 25)
                    reasoning_parts.append("Boosted for predicted peak")
        else:
            reasoning_parts.append("Air quality good - fan off")
        
        reasoning = "; ".join(reasoning_parts)
        
        return ControlDecision(
            fan_on=fan_on,
            fan_intensity=fan_intensity,
            reasoning=reasoning,
            override_reason=None
        )
