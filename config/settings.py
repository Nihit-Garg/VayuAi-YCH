"""
Configuration Settings for AeroLedger
Loads environment variables and provides centralized configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Environment variables should be defined in .env file:
    - API keys for LLM providers
    - Blockchain configuration
    - Server settings
    - Thresholds and parameters
    """
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # LLM Configuration
    LLM_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"  # "gemini" or "openai"
    LLM_MODEL: str = "gemini-1.5-flash"  # or "gpt-4" for OpenAI
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 500
    
    # Blockchain Configuration
    BLOCKCHAIN_ENABLED: bool = False  # Set to True for real blockchain
    BLOCKCHAIN_NETWORK: str = "sepolia"  # Ethereum testnet
    BLOCKCHAIN_RPC_URL: str = ""
    BLOCKCHAIN_PRIVATE_KEY: str = ""
    BLOCKCHAIN_CONTRACT_ADDRESS: str = ""
    
    # Sensor Thresholds (for fault detection)
    PM25_MAX: float = 500.0
    PM25_MIN: float = 0.0
    CO2_MAX: float = 5000.0
    CO2_MIN: float = 300.0
    CO_MAX: float = 1000.0
    CO_MIN: float = 0.0
    VOC_MAX: float = 1000.0
    VOC_MIN: float = 0.0
    
    # Control Parameters
    FAN_INTENSITY_LEVELS: List[int] = [0, 25, 50, 75, 100]
    PREDICTION_WINDOW_SIZE: int = 10  # Number of recent readings for trend analysis
    
    # Fault Detection Parameters
    STUCK_VALUE_THRESHOLD: int = 5  # Number of identical readings to consider stuck
    INCONSISTENCY_THRESHOLD: float = 0.3  # Threshold for detecting inconsistent readings
    
    # Context Storage
    MAX_CONTEXT_SIZE: int = 100  # Maximum number of readings to keep in memory
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
