"""
Local AI brain - handles conversation without external APIs
Provides free, offline AI functionality with expandable knowledge base
"""
import json
import random
import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from .config import Config
from .utils import logger

class LocalAIBrain:
    """Local AI brain that works completely offline"""
    
    def __init__(self):
        """Initialize the local AI brain"""
        self.conversation_history: List[Dict[str, str]] = []
        self.user_context: Dict[str, Any] = {}
        self.knowledge_base: Dict[str, Any] = {}
        self.response_patterns: Dict[str, List[str]] = {}
        
        self._load_knowledge_base()
        self._load_response_patterns()
        self._initialize_conversation()
    
    def _load_knowledge_base(self) -> None:
        """Load the local knowledge base"""
        # Default knowledge base - you can expand this
        self.knowledge_base = {
            "personal_info": {
                "name": Config.AI_NAME,
                "purpose": "I'm your personal AI assistant designed to help with daily tasks",
                "capabilities": [
                    "Answer questions about various topics",
                    "Help with calculations and conversions", 
                    "Provide weather information (when connected)",
                    "Assist with scheduling and reminders",
                    "Control smart home devices (when configured)",
                    "Engage in friendly conversation"
                ]
            },
            "topics": {
                "weather": {
                    "responses": [
                        "I'd love to help with weather information, but I need internet connectivity for current conditions.",
                        "For accurate weather data, I'd need to connect to a weather service."
                    ]
                },
                "time": {
                    "responses": [
                        f"The current time is {datetime.now().strftime('%H:%M %p')}",
                        f"It's {datetime.now().strftime('%I:%M %p')} right now"
                    ]
                },
                "date": {
                    "responses": [
                        f"Today is {datetime.now().strftime('%A, %B %d, %Y')}",
                        f"The date is {datetime.now().strftime('%m/%d/%Y')}"
                    ]
                },
                "math": {
                    "responses": [
                        "I can help with basic calculations. What would you like me to calculate?",
                        "I'm good with math! What calculation do you need?"
                    ]
                },
                "robot": {
                    "responses": [
                        "I'm designed to be part of a robot companion! Right now I can talk, but in the future I could move around and interact with the physical world.",
                        "My robot capabilities are currently in development. For now, I focus on being a great conversational companion!"
                    ]
                },
                "capabilities": {
                    "responses": [
                        "I can have conversations, answer questions, help with basic calculations, tell you the time and date, and much more! What would you like help with?",
                        "My main skills include conversation, basic information lookup, time/date queries, and being a friendly companion. How can I assist you today?"
                    ]
                }
            },
            "facts": {
                "raspberry_pi": "I'm running on a Raspberry Pi, which is a small but powerful computer perfect for robotics and AI projects!",
                "open_source": "I'm built with open-source technologies and can work completely offline for privacy and independence.",
                "expandable": "My knowledge base can be easily expanded by adding new topics and responses to my configuration files."
            }
        }
        
        logger.info("Local knowledge base loaded successfully")
    
    def _load_response_patterns(self) -> None:
        """Load response patterns for different types of conversations"""
        self.response_patterns = {
            "greeting": [
                "Hello! Great to see you again!",
                "Hi there! How can I help you today?",
                "Hey! What's on your mind?",
                "Good to see you! What would you like to talk about?"
            ],
            "goodbye": [
                "Goodbye! It was great talking with you!",
                "See you later! Have a wonderful day!",
                "Take care! I'll be here when you need me.",
                "Until next time! Stay safe!"
            ],
            "thanks": [
                "You're very welcome!",
                "Happy to help!",
                "My pleasure!",
                "Anytime! That's what I'm here for."
            ],
            "unknown": [
                "That's an interesting question! I'm still learning about that topic.",
                "I don't have specific information about that right now, but I'd love to help in other ways!",
                "Hmm, that's not in my current knowledge base. Is there something else I can help you with?",
                "I'm not sure about that particular topic, but I'm always eager to learn! What else can I assist you with?"
            ],
            "conversation": [
                "Tell me more about that!",
                "That sounds interesting! What else?",
                "I'd love to hear more about your thoughts on that.",
                "That's fascinating! Can you share more details?"
            ]
        }
        
        logger.info("Response patterns loaded successfully")
    
    def _initialize_conversation(self) -> None:
        """Initialize conversation with system context"""
        system_message = {
            "role": "system",
            "content": f"You are {Config.AI_NAME}, a helpful AI assistant running locally."
        }
        self.conversation_history.append(system_message)
        logger.info("Local conversation initialized")
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and generate response
        
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
            
            # Analyze input and generate response
            response = self._generate_local_response(user_input)
            
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
    
    def _generate_local_response(self, user_input: str) -> str:
        """Generate response using local knowledge and patterns"""
        user_input_lower = user_input.lower().strip()
        
        # Check for specific patterns first
        
        # Greetings
        if any(word in user_input_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return random.choice(self.response_patterns["greeting"])
        
        # Goodbyes
        if any(word in user_input_lower for word in ["goodbye", "bye", "see you", "farewell", "quit", "exit"]):
            return random.choice(self.response_patterns["goodbye"])
        
        # Thanks
        if any(word in user_input_lower for word in ["thank", "thanks", "appreciate"]):
            return random.choice(self.response_patterns["thanks"])
        
        # Time queries
        if any(word in user_input_lower for word in ["time", "clock", "hour"]):
            return random.choice(self.knowledge_base["topics"]["time"]["responses"])
        
        # Date queries  
        if any(word in user_input_lower for word in ["date", "day", "today", "calendar"]):
            return random.choice(self.knowledge_base["topics"]["date"]["responses"])
        
        # Weather queries
        if any(word in user_input_lower for word in ["weather", "temperature", "rain", "sunny", "cloudy"]):
            return random.choice(self.knowledge_base["topics"]["weather"]["responses"])
        
        # Math/calculations
        if any(word in user_input_lower for word in ["calculate", "math", "plus", "minus", "multiply", "divide", "+", "-", "*", "/", "times"]):
            return self._handle_math(user_input)
        
        # Robot/capabilities questions
        if any(word in user_input_lower for word in ["robot", "move", "walk", "drive"]):
            return random.choice(self.knowledge_base["topics"]["robot"]["responses"])
        
        # Capability questions
        if any(word in user_input_lower for word in ["can you", "what can", "help", "do", "abilities", "capabilities"]):
            return random.choice(self.knowledge_base["topics"]["capabilities"]["responses"])
        
        # Personal questions about the AI
        if any(word in user_input_lower for word in ["who are you", "what are you", "tell me about yourself", "introduce yourself"]):
            return f"I'm {Config.AI_NAME}, {self.knowledge_base['personal_info']['purpose']}. I can help you with many things like answering questions, basic calculations, and friendly conversation!"
        
        # Default conversational response
        return random.choice(self.response_patterns["unknown"])
    
    def _handle_math(self, user_input: str) -> str:
        """Handle basic math calculations"""
        try:
            # Extract numbers and basic operators
            math_pattern = r'([\d\.\+\-\*/\(\)\s]+)'
            match = re.search(math_pattern, user_input)
            
            if match:
                expression = match.group(1).strip()
                # Only allow safe math operations
                allowed_chars = set('0123456789+-*/.() ')
                if all(c in allowed_chars for c in expression):
                    try:
                        result = eval(expression)
                        return f"The answer is {result}"
                    except:
                        pass
            
            return "I can help with basic math! Try asking me something like 'what is 15 plus 7' or '10 times 3'"
            
        except Exception as e:
            logger.error(f"Error in math handling: {e}")
            return "I had trouble with that calculation. Could you rephrase it?"
    
    def _manage_conversation_history(self) -> None:
        """Manage conversation history to stay within limits"""
        max_messages = (Config.MAX_CONVERSATION_HISTORY * 2) + 1
        
        if len(self.conversation_history) > max_messages:
            # Keep system message and recent exchanges
            system_msg = self.conversation_history[0]
            recent_messages = self.conversation_history[-(max_messages-1):]
            self.conversation_history = [system_msg] + recent_messages
            logger.debug(f"Trimmed conversation history to {len(self.conversation_history)} messages")
    
    def _get_error_response(self) -> str:
        """Get a fallback response when processing fails"""
        error_responses = [
            "I'm sorry, I'm having trouble understanding right now. Could you try again?",
            "I seem to be experiencing some technical difficulties. Please give me a moment.",
            "I'm not quite sure how to respond to that. Could you rephrase your question?",
        ]
        return random.choice(error_responses)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation"""
        return {
            "total_exchanges": (len(self.conversation_history) - 1) // 2,
            "history_length": len(self.conversation_history),
            "ai_name": Config.AI_NAME,
            "model": "Local Knowledge Base",
            "mode": "offline"
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
    
    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user intent for better response handling
        
        Args:
            user_input: User's input text
            
        Returns:
            Dictionary with intent analysis
        """
        user_input_lower = user_input.lower()
        
        # Simple intent classification
        if any(word in user_input_lower for word in ["hello", "hi", "hey"]):
            intent = "greeting"
            confidence = 0.9
        elif any(word in user_input_lower for word in ["goodbye", "bye"]):
            intent = "goodbye" 
            confidence = 0.9
        elif any(word in user_input_lower for word in ["time", "clock"]):
            intent = "time_query"
            confidence = 0.8
        elif any(word in user_input_lower for word in ["date", "today"]):
            intent = "date_query"
            confidence = 0.8
        elif any(word in user_input_lower for word in ["calculate", "math", "+", "-", "*", "/"]):
            intent = "calculation"
            confidence = 0.7
        elif any(word in user_input_lower for word in ["weather"]):
            intent = "weather_query"
            confidence = 0.8
        elif "?" in user_input:
            intent = "question"
            confidence = 0.6
        else:
            intent = "casual_chat"
            confidence = 0.5
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": [],
            "requires_action": intent in ["calculation", "time_query", "date_query"]
        }
    
    def add_knowledge(self, topic: str, information: str) -> None:
        """Add new knowledge to the knowledge base"""
        if "custom" not in self.knowledge_base:
            self.knowledge_base["custom"] = {}
        
        self.knowledge_base["custom"][topic] = information
        logger.info(f"Added knowledge for topic: {topic}")
    
    def get_knowledge(self, topic: str) -> Optional[str]:
        """Retrieve knowledge about a specific topic"""
        # Check custom knowledge first
        if "custom" in self.knowledge_base and topic in self.knowledge_base["custom"]:
            return self.knowledge_base["custom"][topic]
        
        # Check built-in knowledge
        if topic in self.knowledge_base.get("topics", {}):
            responses = self.knowledge_base["topics"][topic].get("responses", [])
            return random.choice(responses) if responses else None
        
        if topic in self.knowledge_base.get("facts", {}):
            return self.knowledge_base["facts"][topic]
        
        return None