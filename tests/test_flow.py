import asyncio
from typing import List
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import core components
from models.schemas import SensorReading
from core.decision_engine.orchestrator import DecisionOrchestrator
from services.sensor_service.ingestion import SensorIngestionService
from services.smoke_model_service import SmokeModelService

# Mock data
MOCK_READING = SensorReading(
    device_id="ESP32_TEST",
    pm25=15.0,
    co2=450.0,
    co=250.0, # Dangerous CO > 200
    voc=50.0,
    timestamp=datetime.utcnow()
)

async def test_decision_flow():
    """
    Test the full decision pipeline with mock data.
    """
    print("\n--- Starting Decision Flow Test ---")
    
    # 1. Initialize Services
    ingestion = SensorIngestionService()
    orchestrator = DecisionOrchestrator()
    
    # 2. Ingest Data
    print(f"Ingesting reading: CO={MOCK_READING.co}")
    ingestion.store_reading(MOCK_READING)
    
    # 3. Get Context
    context = ingestion.get_recent_context(MOCK_READING.device_id)
    assert len(context) == 1
    
    # 4. Process
    decision, prediction = await orchestrator.process(MOCK_READING, context)
    
    # 5. Verify Output
    print(f"Decision: Fan={decision.fan_on}, Intensity={decision.fan_intensity}")
    print(f"Reasoning: {decision.reasoning}")
    
    # 6. Verify Blockchain Logging
    await orchestrator.log_to_blockchain(MOCK_READING.device_id, decision, prediction)
    logs = orchestrator.blockchain_logger.get_recent_logs(1)
    assert len(logs) > 0
    last_log = logs[-1]
    print(f"Blockchain Log Data: {last_log.data}")
    
    # Check if prediction value is in log
    if prediction:
        assert "predicted_smoke_peak" in last_log.data
        print(f"Verified: Predicted peak {last_log.data['predicted_smoke_peak']} logged to blockchain.")

    # Assertions
    assert decision.fan_on is True
    assert decision.fan_intensity > 0
    
    print("--- Test Passed ---")


if __name__ == "__main__":
    # Manual run wrapper
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_decision_flow())
