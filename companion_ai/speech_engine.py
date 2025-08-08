"""
Text-to-speech engine for the Companion AI
"""
import pyttsx3
import threading
from queue import Queue
from typing import Optional
try:
    from .config import Config
    from .utils import logger
except ImportError:
    from config import Config
    from utils import logger

class SpeechEngine:
    """Handles text-to-speech output"""
    
    def __init__(self):
        """Initialize the speech engine"""
        self.engine = None
        self.speech_queue = Queue()
        self.is_speaking = False
        self.speech_thread = None
        self.is_running = False
        
        self._initialize_engine()
        self._start_speech_worker()
    
    def _initialize_engine(self) -> None:
        """Initialize the pyttsx3 engine with configuration"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure speech rate
            self.engine.setProperty('rate', Config.TTS_RATE)
            
            # Configure volume
            self.engine.setProperty('volume', Config.TTS_VOLUME)
            
            # Configure voice (if available)
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > Config.TTS_VOICE_INDEX:
                self.engine.setProperty('voice', voices[Config.TTS_VOICE_INDEX].id)
                logger.info(f"Using voice: {voices[Config.TTS_VOICE_INDEX].name}")
            else:
                logger.warning("Requested voice index not available, using default")
            
            logger.info("Speech engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize speech engine: {e}")
            raise
    
    def _start_speech_worker(self) -> None:
        """Start the speech worker thread"""
        self.is_running = True
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        logger.info("Speech worker thread started")
    
    def _speech_worker(self) -> None:
        """Worker thread to handle speech queue"""
        while self.is_running:
            try:
                # Get text from queue (blocks until available)
                text = self.speech_queue.get(timeout=1)
                
                if text is None:  # Shutdown signal
                    break
                
                self._speak_now(text)
                self.speech_queue.task_done()
                
            except Exception as e:
                if self.is_running:  # Only log if not shutting down
                    logger.error(f"Error in speech worker: {e}")
    
    def _speak_now(self, text: str) -> None:
        """Immediately speak the given text"""
        try:
            self.is_speaking = True
            logger.info(f"Speaking: '{text}'")
            
            self.engine.say(text)
            self.engine.runAndWait()
            
            self.is_speaking = False
            logger.debug("Finished speaking")
            
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            self.is_speaking = False
    
    def speak(self, text: str, interrupt: bool = False) -> None:
        """
        Add text to the speech queue
        
        Args:
            text: Text to speak
            interrupt: If True, clear queue and speak immediately
        """
        if not text.strip():
            return
        
        if interrupt:
            # Clear the queue and stop current speech
            self.stop_speaking()
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except:
                    break
        
        self.speech_queue.put(text)
        logger.debug(f"Added to speech queue: '{text[:50]}...'")
    
    def speak_immediately(self, text: str) -> None:
        """Speak text immediately, bypassing the queue"""
        if not text.strip():
            return
        
        # Stop current speech and clear queue
        self.stop_speaking()
        
        # Speak in a separate thread to avoid blocking
        speech_thread = threading.Thread(
            target=self._speak_now, 
            args=(text,), 
            daemon=True
        )
        speech_thread.start()
    
    def stop_speaking(self) -> None:
        """Stop current speech"""
        try:
            if self.engine and self.is_speaking:
                self.engine.stop()
                logger.debug("Stopped current speech")
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
    
    def is_busy(self) -> bool:
        """Check if the speech engine is currently speaking"""
        return self.is_speaking or not self.speech_queue.empty()
    
    def wait_until_done(self, timeout: Optional[float] = None) -> bool:
        """
        Wait until all queued speech is complete
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if completed, False if timeout
        """
        try:
            self.speech_queue.join()  # Wait for all tasks to complete
            return True
        except Exception as e:
            logger.error(f"Error waiting for speech completion: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown the speech engine"""
        logger.info("Shutting down speech engine...")
        
        self.is_running = False
        
        # Clear queue and add shutdown signal
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except:
                break
        
        self.speech_queue.put(None)  # Shutdown signal
        
        # Wait for worker thread to finish
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=2)
        
        # Cleanup engine
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        
        logger.info("Speech engine shutdown complete")
