"""
Main application entry point for Companion AI
"""
import sys
import signal
import time
import threading
from typing import Optional

try:
    from .config import Config
    from .voice_handler import VoiceHandler
    from .speech_engine import SpeechEngine
    from .ai_brain import AIBrain
    from .local_ai_brain import LocalAIBrain
    from .utils import (
        logger, print_banner, print_status, 
        validate_audio_setup, get_system_info, 
        check_raspberry_pi, PerformanceMonitor
    )
except ImportError:
    from config import Config
    from voice_handler import VoiceHandler
    from speech_engine import SpeechEngine
    from ai_brain import AIBrain
    from local_ai_brain import LocalAIBrain
    from utils import (
        logger, print_banner, print_status, 
        validate_audio_setup, get_system_info, 
        check_raspberry_pi, PerformanceMonitor
    )

class HaroAI:
    """Main Haro AI application class"""
    
    def __init__(self):
        """Initialize the Haro AI system"""
        self.voice_handler: Optional[VoiceHandler] = None
        self.speech_engine: Optional[SpeechEngine] = None
        self.ai_brain: Optional[AIBrain] = None
        self.is_running = False
        self.performance_monitor = PerformanceMonitor()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def initialize(self) -> bool:
        """Initialize all system components"""
        try:
            print_banner()
            print_status("Initializing Haro AI...", "INFO")
            
            # Validate configuration
            if not Config.validate():
                print_status("Configuration validation failed", "ERROR")
                return False
            
            # Print system information
            self._print_system_info()
            
            # Validate audio setup
            print_status("Validating audio setup...", "INFO")
            if not validate_audio_setup():
                print_status("Audio setup validation failed", "ERROR")
                return False
            
            # Initialize components based on AI mode
            if Config.AI_MODE == "local":
                print_status("Initializing local AI brain (FREE mode)...", "INFO")
                self.ai_brain = LocalAIBrain()
            else:
                print_status("Initializing OpenAI brain...", "INFO")
                self.ai_brain = AIBrain()
            
            print_status("Initializing speech engine...", "INFO")
            self.speech_engine = SpeechEngine()
            
            print_status("Initializing voice handler...", "INFO")
            self.voice_handler = VoiceHandler(self._on_speech_detected)
            
            print_status("Initialization complete!", "SUCCESS")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            print_status(f"Initialization failed: {e}", "ERROR")
            return False
    
    def _print_system_info(self):
        """Print system information"""
        Config.print_config()
        
        system_info = get_system_info()
        if system_info:
            print("=== System Information ===")
            for key, value in system_info.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        if check_raspberry_pi():
            print_status("Running on Raspberry Pi detected", "INFO")
        else:
            print_status("Not running on Raspberry Pi", "WARNING")
        
        print("=" * 30)
    
    def _on_speech_detected(self, text: str):
        """Handle detected speech from voice handler"""
        try:
            self.performance_monitor.start("response_time")
            
            print_status(f"You said: '{text}'", "LISTENING")
            
            # Process input with AI brain
            print_status("Thinking...", "THINKING")
            response = self.ai_brain.process_input(text)
            
            # Speak the response
            print_status(f"Response: '{response}'", "SPEAKING")
            self.speech_engine.speak(response)
            
            # Log performance
            duration = self.performance_monitor.stop("response_time")
            logger.debug(f"Response generated in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing speech: {e}")
            error_msg = "I'm sorry, I encountered an error processing your request."
            self.speech_engine.speak(error_msg)
    
    def start(self):
        """Start the Haro AI system"""
        if not self.initialize():
            return False
        
        try:
            self.is_running = True
            
            # Greet the user
            greeting = f"Hello! I'm {Config.AI_NAME}, your AI assistant. How can I help you today?"
            print_status(greeting, "SPEAKING")
            self.speech_engine.speak(greeting)
            
            # Start voice recognition
            print_status("Starting voice recognition...", "INFO")
            self.voice_handler.start_listening()
            
            print_status("Haro AI is now active! Say wake words to interact.", "SUCCESS")
            print_status(f"Wake words: {', '.join(Config.WAKE_WORDS)}", "INFO")
            
            # Main loop
            self._main_loop()
            
        except Exception as e:
            logger.error(f"Error starting Haro AI: {e}")
            return False
        
        return True
    
    def _main_loop(self):
        """Main application loop"""
        try:
            while self.is_running:
                time.sleep(1)
                
                # Optional: Add periodic health checks here
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the Haro AI system"""
        if not self.is_running:
            return
        
        print_status("Shutting down Haro AI...", "INFO")
        self.is_running = False
        
        try:
            # Stop voice recognition
            if self.voice_handler:
                self.voice_handler.stop_listening()
            
            # Farewell message
            if self.speech_engine:
                farewell = "Goodbye! It was nice talking with you."
                self.speech_engine.speak_immediately(farewell)
                self.speech_engine.wait_until_done(timeout=3)
                self.speech_engine.shutdown()
            
            print_status("Shutdown complete", "SUCCESS")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def test_mode(self):
        """Run in test mode for debugging"""
        if not self.initialize():
            return False
        
        print_status("Running in test mode", "INFO")
        print("Type 'quit' to exit test mode")
        
        try:
            while True:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    break
                
                if not user_input:
                    continue
                
                # Process input
                self.performance_monitor.start("test_response")
                response = self.ai_brain.process_input(user_input)
                duration = self.performance_monitor.stop("test_response")
                
                print(f"AI: {response}")
                print(f"(Response time: {duration:.2f}s)")
                
                # Optional: speak the response
                speak_response = input("Speak response? (y/n): ").lower().strip()
                if speak_response == 'y':
                    self.speech_engine.speak(response)
                    self.speech_engine.wait_until_done()
        
        except KeyboardInterrupt:
            print("\nTest mode interrupted")
        finally:
            self.shutdown()
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Haro AI - Voice-activated AI assistant")
    parser.add_argument("--test", action="store_true", help="Run in test mode (text input)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", action="store_true", help="Show configuration and exit")
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logger.setLevel(10)  # DEBUG level
        print_status("Debug logging enabled", "INFO")
    
    # Show configuration if requested
    if args.config:
        Config.print_config()
        return
    
    # Create and start the Companion AI
    haro = HaroAI()
    
    try:
        if args.test:
            success = haro.test_mode()
        else:
            success = haro.start()
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
