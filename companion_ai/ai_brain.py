"""
AI brain - handles conversation and OpenAI integration
"""
import json
from typing import List, Dict, Optional
from openai import OpenAI
try:
    from .config import Config
    from .utils import logger
except ImportError:
    from config import Config
    from utils import logger

class AIBrain:
    """Handles AI conversation logic and OpenAI integration"""
    
    def __init__(self):
        """Initialize the AI brain"""
        self.client = None
        self.conversation_history: List[Dict[str, str]] = []
        self.user_context: Dict[str, str] = {}
        
        self._initialize_openai()
        self._initialize_conversation()
    
    def _initialize_openai(self) -> None:
        """Initialize OpenAI client"""
        try:
            if not Config.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not found in environment variables")
            
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            logger.info("OpenAI client initialized successfully")
            
            # Test the connection
            self._test_connection()
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    def _test_connection(self) -> None:
        """Test OpenAI connection with a simple request"""
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            logger.info("OpenAI connection test successful")
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            raise
    
    def _initialize_conversation(self) -> None:
        """Initialize conversation with system prompt"""
        system_message = {
            "role": "system",
            "content": Config.AI_PERSONALITY
        }
        self.conversation_history.append(system_message)
        logger.info("Conversation initialized with AI personality")
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and generate AI response
        
        Args:
            user_input: The user's spoken input
            
        Returns:
            AI response text
        """
        try:
            logger.info(f"Processing user input: '{user_input}'")
            
            # Add user message to conversation history
            user_message = {"role": "user", "content": user_input}
            self.conversation_history.append(user_message)
            
            # Generate AI response
            response = self._generate_response()
            
            # Add AI response to conversation history
            ai_message = {"role": "assistant", "content": response}
            self.conversation_history.append(ai_message)
            
            # Manage conversation history size
            self._manage_conversation_history()
            
            logger.info(f"Generated response: '{response}'")
            return response
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return self._get_error_response()
    
    def _generate_response(self) -> str:
        """Generate AI response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=self.conversation_history,
                max_tokens=150,  # Keep responses concise for speech
                temperature=0.7,  # Balanced creativity
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            raise
    
    def _manage_conversation_history(self) -> None:
        """Manage conversation history to stay within limits"""
        # Keep system message + recent exchanges
        max_messages = (Config.MAX_CONVERSATION_HISTORY * 2) + 1  # user + assistant pairs + system
        
        if len(self.conversation_history) > max_messages:
            # Keep system message and most recent exchanges
            system_msg = self.conversation_history[0]
            recent_messages = self.conversation_history[-(max_messages-1):]
            self.conversation_history = [system_msg] + recent_messages
            logger.debug(f"Trimmed conversation history to {len(self.conversation_history)} messages")
    
    def _get_error_response(self) -> str:
        """Get a fallback response when AI processing fails"""
        error_responses = [
            "I'm sorry, I'm having trouble understanding right now. Could you try again?",
            "I seem to be experiencing some technical difficulties. Please give me a moment.",
            "I'm not quite sure how to respond to that. Could you rephrase your question?",
        ]
        import random
        return random.choice(error_responses)
    
    def get_conversation_summary(self) -> Dict[str, any]:
        """Get a summary of the current conversation"""
        return {
            "total_exchanges": (len(self.conversation_history) - 1) // 2,  # Exclude system message
            "history_length": len(self.conversation_history),
            "ai_name": Config.AI_NAME,
            "model": Config.OPENAI_MODEL
        }
    
    def reset_conversation(self) -> None:
        """Reset the conversation history"""
        logger.info("Resetting conversation history")
        self.conversation_history = []
        self._initialize_conversation()
    
    def set_user_context(self, key: str, value: str) -> None:
        """Set user context information"""
        self.user_context[key] = value
        logger.debug(f"Set user context: {key} = {value}")
    
    def get_user_context(self, key: str) -> Optional[str]:
        """Get user context information"""
        return self.user_context.get(key)
    
    def analyze_intent(self, user_input: str) -> Dict[str, any]:
        """
        Analyze user intent for better response handling
        
        Args:
            user_input: User's input text
            
        Returns:
            Dictionary with intent analysis
        """
        try:
            prompt = f"""Analyze the following user input and determine the intent. 
            Respond with JSON in this format:
            {{"intent": "category", "confidence": 0.8, "entities": ["entity1", "entity2"], "requires_action": false}}
            
            Intent categories: greeting, question, request, goodbye, casual_chat, command
            
            User input: "{user_input}" """
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=100
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.debug(f"Intent analysis: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": [],
                "requires_action": False
            }
