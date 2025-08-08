"""
Voice recognition handler for the Companion AI
"""
import speech_recognition as sr
import threading
import time
from typing import Optional, Callable
try:
    from .config import Config
    from .utils import logger
except ImportError:
    from config import Config
    from utils import logger

class VoiceHandler:
    """Handles voice recognition and audio input processing"""
    
    def __init__(self, on_speech_detected: Callable[[str], None]):
        """
        Initialize the voice handler
        
        Args:
            on_speech_detected: Callback function to handle recognized speech
        """
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.on_speech_detected = on_speech_detected
        self.is_listening = False
        self.listen_thread = None
        
        # Configure recognizer settings
        self.recognizer.energy_threshold = Config.ENERGY_THRESHOLD
        self.recognizer.timeout = Config.TIMEOUT
        self.recognizer.phrase_timeout = Config.PHRASE_TIMEOUT
        
        self._setup_microphone()
    
    def _setup_microphone(self) -> None:
        """Setup and configure the microphone"""
        try:
            # List available microphones for debugging
            mic_list = sr.Microphone.list_microphone_names()
            logger.info(f"Available microphones: {len(mic_list)} found")
            
            # Use specified microphone index or default
            if Config.MICROPHONE_INDEX is not None:
                self.microphone = sr.Microphone(device_index=Config.MICROPHONE_INDEX)
                logger.info(f"Using microphone index: {Config.MICROPHONE_INDEX}")
            else:
                self.microphone = sr.Microphone()
                logger.info("Using default microphone")
            
            # Adjust for ambient noise
            logger.info("Adjusting for ambient noise... Please wait.")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            logger.info(f"Ambient noise adjustment complete. Energy threshold: {self.recognizer.energy_threshold}")
            
        except Exception as e:
            logger.error(f"Failed to setup microphone: {e}")
            raise
    
    def start_listening(self) -> None:
        """Start continuous voice recognition in a separate thread"""
        if self.is_listening:
            logger.warning("Voice handler is already listening")
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_continuously, daemon=True)
        self.listen_thread.start()
        logger.info("Voice recognition started")
    
    def stop_listening(self) -> None:
        """Stop voice recognition"""
        self.is_listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        logger.info("Voice recognition stopped")
    
    def _listen_continuously(self) -> None:
        """Continuously listen for voice input"""
        while self.is_listening:
            try:
                # Listen for audio input
                with self.microphone as source:
                    logger.debug("Listening for speech...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech in a separate thread to avoid blocking
                recognition_thread = threading.Thread(
                    target=self._process_audio, 
                    args=(audio,), 
                    daemon=True
                )
                recognition_thread.start()
                
            except sr.WaitTimeoutError:
                # No speech detected within timeout - this is normal
                continue
            except Exception as e:
                logger.error(f"Error in continuous listening: {e}")
                time.sleep(1)  # Brief pause before retrying
    
    def _process_audio(self, audio: sr.AudioData) -> None:
        """Process audio data and recognize speech"""
        try:
            logger.debug("Processing audio...")
            
            # Use Google Speech Recognition (free)
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized speech: '{text}'")
            
            # Check if wake word is present or if we're in active conversation
            if self._contains_wake_word(text.lower()):
                # Remove wake word and process the command
                cleaned_text = self._remove_wake_words(text.lower()).strip()
                if cleaned_text:
                    self.on_speech_detected(cleaned_text)
                else:
                    # Just wake word, acknowledge
                    self.on_speech_detected("Hello! How can I help you?")
            
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
        except sr.RequestError as e:
            logger.error(f"Speech recognition request failed: {e}")
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
    
    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains any wake words"""
        return any(wake_word in text for wake_word in Config.WAKE_WORDS)
    
    def _remove_wake_words(self, text: str) -> str:
        """Remove wake words from text"""
        for wake_word in Config.WAKE_WORDS:
            text = text.replace(wake_word, "").strip()
        return text
    
    def listen_once(self) -> Optional[str]:
        """Listen for a single phrase (for testing purposes)"""
        try:
            logger.info("Listening for single phrase...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: '{text}'")
            return text
            
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in single listen: {e}")
            return None
