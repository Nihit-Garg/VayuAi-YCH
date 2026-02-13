# AeroLedger Backend

Gen-AI + Blockchain based Air Safety System

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your LLM_API_KEY

# Run server
python main.py
```

Server will start at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

See [ARCHITECTURE.md](../ARCHITECTURE.md) for detailed documentation.

## Key Features

✅ Real-time sensor data processing from ESP32
✅ AI-powered smoke prediction and air classification
✅ Intelligent fan control decisions
✅ Fault detection and self-healing
✅ Blockchain logging (simulated or real)
✅ REST API for frontend dashboard

## Project Structure

```
backend/
├── main.py              # FastAPI entry point
├── api/                 # REST API routes
├── core/                # Decision engine, fault detection, self-healing
├── agents/              # AI agents (LLM-powered)
├── services/            # Sensor and control services
├── models/              # Pydantic data models
├── blockchain/          # Blockchain logger
├── config/              # Configuration
└── utils/               # Utilities
```

## Environment Variables

Required:
- `LLM_API_KEY` - OpenAI or compatible API key

Optional (see `.env.example` for all options):
- `BLOCKCHAIN_ENABLED` - Enable real blockchain (default: False)
- `LLM_MODEL` - LLM model (default: gpt-4)
- `PORT` - Server port (default: 8000)

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Send sensor data
curl -X POST http://localhost:8000/api/v1/sensor/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32_001",
    "pm25": 45.2,
    "co2": 850.0,
    "co": 12.5,
    "voc": 120.0
  }'
```

## License

MIT
