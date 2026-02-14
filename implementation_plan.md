# AeroLedger Backend Implementation Plan

## Goal
Complete the AeroLedger backend by implementing missing components and ensuring alignment with MQ2 (CO/Smoke) sensor data.

## User Review Required
> [!IMPORTANT]
> **Sensor Data Alignment**: The system will be updated to prioritize `CO` readings for smoke detection, matching the MQ2 sensor capabilities.

## Proposed Changes

### 1. Data & Model Alignment
#### [MODIFY] [train_smoke_model.py](file:///d:/VayuAi-YCH/train_smoke_model.py)
- Update synthetic data generation to simulate CO levels (MQ2).
- Train model on CO data instead of generic "value".

#### [MODIFY] [service.../smoke_model_service.py](file:///d:/VayuAi-YCH/services/smoke_model_service.py)
- Rename/update helper methods to clarify CO usage.
- Ensure feature extraction matches training data.

#### [MODIFY] [agents.../smoke_prediction_agent.py](file:///d:/VayuAi-YCH/agents/smoke_prediction_agent.py)
- Implement `execute` method required by `DecisionOrchestrator`.
- Extract `co` from `SensorReading` for prediction.

### 2. Implementation of Missing Agents
#### [NEW] [agents.../air_classification_agent.py](file:///d:/VayuAi-YCH/agents/air_classification_agent.py)
- Implement `AirTypeClassificationAgent` class.
- Logic to classify air quality events (e.g., Clean, Cooking, Fire) based on CO and CO2 levels.

#### [NEW] [agents.../control_decision_agent.py](file:///d:/VayuAi-YCH/agents/control_decision_agent.py)
- Implement `ControlDecisionAgent` class.
- Logic to determine fan speed based on prediction and classification outputs.

### 3. Implementation of Missing Services
#### [NEW] [services.../ingestion.py](file:///d:/VayuAi-YCH/services/sensor_service/ingestion.py)
- Implement `SensorIngestionService` class.
- In-memory storage for recent sensor readings (context window).

### 4. System Integration
#### [MODIFY] [main.py](file:///d:/VayuAi-YCH/main.py)
- verify routes and initialization.

## Verification Plan
1.  **Train Model**: Run `python train_smoke_model.py` to generate `smoke_model.pkl`.
2.  **Run Server**: Start the application with `python main.py`.
3.  **Test Endpoint**: Send mock `SensorReading` to `/api/v1/sensor/ingest` and verify:
    - 200 OK response.
    - Correct control decision (Fan ON/OFF).
    - Logs indicating successful agent execution.
