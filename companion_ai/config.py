"""
Configuration settings for the Companion AI
"""
import os
from typing import Optional

class Config:
    """Configuration class for Companion AI settings"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
    
    # Voice Recognition Settings
    MICROPHONE_INDEX: Optional[int] = None  # Auto-detect by default
    ENERGY_THRESHOLD: int = 4000  # Adjust based on environment noise
    TIMEOUT: float = 1.0  # Seconds to wait for speech
    PHRASE_TIMEOUT: float = 0.3  # Seconds of silence to end phrase
    
    # Text-to-Speech Settings
    TTS_RATE: int = 150  # Words per minute
    TTS_VOLUME: float = 0.9  # Volume level (0.0 to 1.0)
    TTS_VOICE_INDEX: int = 0  # Voice selection index
    
    # Conversation Settings
    MAX_CONVERSATION_HISTORY: int = 10  # Number of exchanges to remember
    WAKE_WORDS: list = ["hey haro", "haro", "ai"]
    
    # AI Personality Settings
    AI_NAME: str = "Haro"
    AI_PERSONALITY: str = """You are Haro, a helpful and friendly AI assistant. You are:
    - Conversational and engaging
    - Supportive and encouraging
    - Curious about the user's day and interests
    - Able to help with various tasks and questions
    - Designed to be a loyal companion
    Keep responses concise but warm, as they will be spoken aloud."""
    
    # Hardware Settings (for future robot integration)
    ENABLE_GPIO: bool = False  # Set to True when running on actual Raspberry Pi
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings"""
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. Please set environment variable.")
            return False
        return True
    
    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (excluding sensitive data)"""
        print("=== Haro AI Configuration ===")
        print(f"AI Name: {cls.AI_NAME}")
        print(f"OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"TTS Rate: {cls.TTS_RATE} WPM")
        print(f"Energy Threshold: {cls.ENERGY_THRESHOLD}")
        print(f"Max History: {cls.MAX_CONVERSATION_HISTORY}")
        print(f"Wake Words: {', '.join(cls.WAKE_WORDS)}")
        print(f"GPIO Enabled: {cls.ENABLE_GPIO}")
        print("=" * 35)
