"""
Smoke Prediction Agent (Multivariate ML Model)
Predicts smoke density using trained XGBoost model.
"""

from typing import Dict, Any, List
import logging

from agents.base_agent import BaseAgent
from models.schemas import SmokePrediction, SensorReading
from services.smoke_model_service import SmokeModelService

logger = logging.getLogger(__name__)


class SmokePredictionAgent(BaseAgent):
    """
    Agent that uses a trained XGBoost model for multivariate smoke prediction.
    Replaces the LLM approach for speed and accuracy in smoke event detection.
    """
    
    def __init__(self):
        # We don't call super().__init__() because we don't need LLM initialization
        self.model_service = SmokeModelService()
        logger.info("SmokePredictionAgent initialized with SmokeModelService")

    async def execute(self, context: Dict[str, Any]) -> SmokePrediction:
        """
        Execute prediction logic using trained multivariate model.
        """
        readings: List[SensorReading] = context.get("recent_readings", [])
        current_reading: SensorReading = context.get("current_reading")
        
        if not readings and current_reading:
            readings = [current_reading]
            
        # The service handles checking attributes like .co, .pm25 etc on the objects
        predicted_value = self.model_service.predict(readings)
        
        # Analyze trend for heuristic binary flag
        last_val = getattr(readings[-1], 'co', 0) if readings else 0
            
        # Heuristic for "Will Peak" based on predicted value vs current
        will_peak = predicted_value > (last_val * 1.05) and predicted_value > 250
        
        # Confidence calculation
        confidence = 0.95 if predicted_value > 400 else (0.85 if will_peak else 0.60)
        
        reasoning = f"Predicted MQ2 level: {predicted_value:.2f}. "
        if will_peak:
            reasoning += "Rising trend predicted based on multivariate analysis."
        else:
            reasoning += "Stable or decreasing trend."

        return SmokePrediction(
            will_peak=will_peak,
            confidence=confidence,
            estimated_peak_value=predicted_value,
            reasoning=reasoning
        )

    # placeholder implementations to satisfy BaseAgent contract
    def get_system_prompt(self) -> str: return ""
    def format_user_prompt(self, context: Dict[str, Any]) -> str: return ""
    def parse_response(self, response: str) -> Any: return None


