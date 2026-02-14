"""
AI Agent Base Class
Provides common interface for all AI agents using LLM
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    All agents follow the same pattern:
    1. Receive sensor context
    2. Format prompt with system instructions
    3. Call LLM with structured output
    4. Parse and validate response
    5. Return typed result
    """
    
    def __init__(self):
        """Initialize LLM client based on provider."""
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        
        if self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=settings.LLM_API_KEY)
            self.client = genai.GenerativeModel(
                model_name=self.model,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }
            )
        elif self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.LLM_API_KEY)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        logger.info(f"{self.__class__.__name__} initialized with {self.provider} model {self.model}")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Define the system prompt for this agent.
        Should describe the agent's role and output format.
        
        Returns:
            System prompt string
        """
        pass
    
    @abstractmethod
    def format_user_prompt(self, context: Dict[str, Any]) -> str:
        """
        Format the user prompt with sensor data context.
        
        Args:
            context: Dictionary containing sensor readings and other data
        
        Returns:
            Formatted user prompt string
        """
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Any:
        """
        Parse and validate LLM response.
        
        Args:
            response: Raw LLM response string
        
        Returns:
            Parsed and validated response object
        """
        pass
    
    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the agent with given context.
        
        Args:
            context: Sensor data and other contextual information
        
        Returns:
            Agent-specific output (SmokePrediction, AirTypeClassification, etc.)
        """
        try:
            # Check if using mock AI
            if settings.USE_MOCK_AI:
                logger.info(f"{self.__class__.__name__} using MOCK response (USE_MOCK_AI=True)")
                return self._generate_mock_response(context)
            
            # Format prompts
            system_prompt = self.get_system_prompt()
            user_prompt = self.format_user_prompt(context)
            
            logger.debug(f"{self.__class__.__name__} executing with context: {context}")
            
            # Call LLM based on provider
            if self.provider == "gemini":
                # Gemini API call
                full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nRespond with valid JSON only."
                response = self.client.generate_content(full_prompt)
                raw_response = response.text
                
            elif self.provider == "openai":
                # OpenAI API call
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"}
                )
                raw_response = response.choices[0].message.content
            
            logger.debug(f"{self.__class__.__name__} raw response: {raw_response}")
            
            # Parse and validate
            result = self.parse_response(raw_response)
            
            logger.info(f"{self.__class__.__name__} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"{self.__class__.__name__} error: {str(e)}")
            raise
    
    @abstractmethod
    def _generate_mock_response(self, context: Dict[str, Any]) -> Any:
        """
        Generate mock response for testing (when USE_MOCK_AI=True).
        Each agent must implement this with intelligent mock logic.
        
        Args:
            context: Sensor data and other contextual information
        
        Returns:
            Agent-specific mock response
        """
        pass
    
    def _safe_json_parse(self, response: str) -> Dict:
        """
        Safely parse JSON response with error handling.
        Handles Gemini's tendency to wrap JSON in markdown code blocks.
        
        Args:
            response: Raw LLM response
        
        Returns:
            Parsed JSON dictionary
        """
        try:
            # Strip markdown code blocks if present (Gemini often does this)
            cleaned_response = response.strip()
            
            # Remove ```json and ``` markers
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]  # Remove ```
            
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}, response: {response[:200]}")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
