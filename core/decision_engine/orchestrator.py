"""
Decision Engine Orchestrator
Coordinates all AI agents, fault detection, and self-healing
"""

from typing import List
import logging

from models.schemas import (
    SensorReading,
    ControlDecision,
    SmokePrediction,
    AirTypeClassification,
    FaultDetectionResult,
    SelfHealingAction
)
from agents.smoke_prediction_agent import SmokePredictionAgent
from agents.air_classification_agent import AirTypeClassificationAgent
from agents.control_decision_agent import ControlDecisionAgent
from core.fault_detection.detector import FaultDetector
from core.self_healing.healer import SelfHealingModule
from blockchain.logger import BlockchainLogger

logger = logging.getLogger(__name__)


class DecisionOrchestrator:
    """
    Orchestrates the entire decision-making pipeline.
    
    Pipeline:
    1. Fault Detection
    2. Self-Healing (if fault detected)
    3. Smoke Prediction (AI Agent)
    4. Air Type Classification (AI Agent)
    5. Control Decision (AI Agent)
    6. Blockchain Logging (critical events)
    
    This is the central brain of the system.
    """
    
    def __init__(self, blockchain_logger=None):
        """Initialize all components."""
        self.smoke_predictor = SmokePredictionAgent()
        self.air_classifier = AirTypeClassificationAgent()
        self.control_agent = ControlDecisionAgent()
        self.fault_detector = FaultDetector()
        self.self_healer = SelfHealingModule()
        
        # Use provided blockchain_logger or create new one
        if blockchain_logger is not None:
            self.blockchain_logger = blockchain_logger
        else:
            from blockchain.logger import BlockchainLogger
            self.blockchain_logger = BlockchainLogger()
        
        # Cache for latest AI decisions per device
        self.latest_decisions = {}  # {device_id: {prediction, classification, decision}}
        
        logger.info("DecisionOrchestrator initialized with all agents")
    
    async def process(
        self,
        current_reading: SensorReading,
        recent_readings: List[SensorReading]
    ) -> ControlDecision:
        """
        Process sensor data through the entire pipeline.
        
        Args:
            current_reading: Latest sensor reading
            recent_readings: Recent historical readings for context
        
        Returns:
            ControlDecision to send to ESP32
        """
        device_id = current_reading.device_id
        logger.info(f"Processing decision pipeline for {device_id}")
        
        # STEP 1: Fault Detection
        fault = self.fault_detector.detect_faults(current_reading, recent_readings)
        
        if fault.has_fault:
            logger.warning(f"Fault detected: {fault.details}")
            
            # STEP 2: Self-Healing
            healing_action = self.self_healer.heal(fault, current_reading)
            logger.info(f"Healing action: {healing_action.action_taken}")
            
            # Log fault and healing to blockchain
            await self._log_fault_to_blockchain(device_id, fault, healing_action)
            
            # If safe mode is active, return safe mode control
            if self.self_healer.should_use_safe_mode():
                return self.self_healer.get_safe_mode_control()
        
        # STEP 3: Smoke Prediction
        prediction_context = {
            "current_reading": current_reading,
            "recent_readings": recent_readings
        }
        prediction: SmokePrediction = await self.smoke_predictor.execute(prediction_context)
        logger.info(f"Smoke prediction: will_peak={prediction.will_peak}, confidence={prediction.confidence}")
        
        # STEP 4: Air Type Classification
        classification_context = {
            "current_reading": current_reading
        }
        classification: AirTypeClassification = await self.air_classifier.execute(classification_context)
        logger.info(f"Air classification: {classification.air_type.value}, confidence={classification.confidence}")
        
        # STEP 5: Control Decision
        control_context = {
            "current_reading": current_reading,
            "prediction": prediction,
            "classification": classification
        }
        decision: ControlDecision = await self.control_agent.execute(control_context)
        logger.info(f"Control decision: fan_on={decision.fan_on}, intensity={decision.fan_intensity}")
        
        # Cache the latest decisions for dashboard
        self.latest_decisions[device_id] = {
            "prediction": prediction,
            "classification": classification,
            "decision": decision,
            "fault": fault if fault.has_fault else None
        }
        
        return decision
    
    async def log_to_blockchain(
        self,
        device_id: str,
        decision: ControlDecision
    ) -> None:
        """
        Log critical control decision to blockchain.
        
        Args:
            device_id: ESP32 device identifier
            decision: Control decision to log
        """
        try:
            await self.blockchain_logger.log_decision(device_id, decision)
            logger.info(f"Logged decision to blockchain for {device_id}")
        except Exception as e:
            logger.error(f"Failed to log to blockchain: {str(e)}")
    
    async def _log_fault_to_blockchain(
        self,
        device_id: str,
        fault: FaultDetectionResult,
        healing: SelfHealingAction
    ) -> None:
        """
        Log fault and healing action to blockchain.
        
        Args:
            device_id: ESP32 device identifier
            fault: Detected fault
            healing: Healing action taken
        """
        try:
            await self.blockchain_logger.log_fault(device_id, fault, healing)
            logger.info(f"Logged fault to blockchain for {device_id}")
        except Exception as e:
            logger.error(f"Failed to log fault to blockchain: {str(e)}")
