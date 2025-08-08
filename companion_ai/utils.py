"""
Utility functions and helpers for the Companion AI
"""
import logging
import sys
import time
from datetime import datetime
from typing import Optional

# Configure logging
def setup_logger(name: str = "companion_ai", level: int = logging.INFO) -> logging.Logger:
    """Setup and configure logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

# Global logger instance
logger = setup_logger()

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════╗
    ║             HARO v1.0                ║
    ║      Voice-Activated AI Assistant    ║
    ║        Raspberry Pi Optimized       ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

def print_status(message: str, status_type: str = "INFO"):
    """Print formatted status message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {
        "INFO": "ℹ",
        "SUCCESS": "✓",
        "WARNING": "⚠",
        "ERROR": "✗",
        "LISTENING": "🎤",
        "SPEAKING": "🔊",
        "THINKING": "🤔"
    }
    
    symbol = symbols.get(status_type, "•")
    print(f"[{timestamp}] {symbol} {message}")

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"

def safe_float_convert(value: str, default: float = 0.0) -> float:
    """Safely convert string to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int_convert(value: str, default: int = 0) -> int:
    """Safely convert string to int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def validate_audio_setup() -> bool:
    """Validate audio setup on the system"""
    try:
        import pyaudio
        import speech_recognition as sr
        import pyttsx3
        
        # Test microphone access
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
        
        # Test text-to-speech
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.stop()
        
        logger.info("Audio setup validation successful")
        return True
        
    except Exception as e:
        logger.error(f"Audio setup validation failed: {e}")
        return False

def get_system_info() -> dict:
    """Get system information for debugging"""
    import platform
    import psutil
    
    try:
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
            "memory_available": f"{psutil.virtual_memory().available / (1024**3):.1f} GB",
        }
        return info
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {}

def check_raspberry_pi() -> bool:
    """Check if running on Raspberry Pi"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
    except:
        return False

class PerformanceMonitor:
    """Simple performance monitoring utility"""
    
    def __init__(self):
        self.start_time = None
        self.measurements = {}
    
    def start(self, name: str = "default"):
        """Start timing measurement"""
        self.start_time = time.time()
        self.measurements[name] = {"start": self.start_time}
    
    def stop(self, name: str = "default") -> float:
        """Stop timing measurement and return duration"""
        if name not in self.measurements:
            return 0.0
        
        end_time = time.time()
        duration = end_time - self.measurements[name]["start"]
        self.measurements[name]["duration"] = duration
        return duration
    
    def get_measurement(self, name: str = "default") -> Optional[float]:
        """Get measurement duration"""
        return self.measurements.get(name, {}).get("duration")
    
    def reset(self):
        """Reset all measurements"""
        self.measurements.clear()
        self.start_time = None
