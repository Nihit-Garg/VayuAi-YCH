"""
Shared Service Instances
Provides singleton instances of services to ensure consistency across modules
"""

from services.sensor_service.ingestion import SensorIngestionService
from blockchain.logger import BlockchainLogger
from core.decision_engine.orchestrator import DecisionOrchestrator

# Singleton instances - shared across all routes and modules
sensor_service = SensorIngestionService()
blockchain_logger = BlockchainLogger()
decision_orchestrator = DecisionOrchestrator(blockchain_logger=blockchain_logger)

# Helper function to get latest AI decisions
def get_latest_decisions(device_id: str):
    """Get cached AI decisions for a device"""
    return decision_orchestrator.latest_decisions.get(device_id)

__all__ = ['sensor_service', 'blockchain_logger', 'decision_orchestrator', 'get_latest_decisions']
