"""
AI Analysis Module
Processes transcribed text and provides intelligent responses using AI models
"""

import os
import openai
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# Optional GROQ import
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAnalyzer:
    """
    AI Analysis class for processing transcribed text and generating intelligent responses
    """
    
    def __init__(self, model: str = None, max_tokens: int = None, temperature: float = None):
        """
        Initialize AI analyzer

        Args:
            model (str): AI model to use (default from env)
            max_tokens (int): Maximum tokens for response (default from env)
            temperature (float): Response creativity (default from env)
        """
        # Determine AI provider
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()

        # Initialize based on provider
        if self.provider == 'groq' and GROQ_AVAILABLE:
            self.groq_api_key = os.getenv('GROQ_API_KEY')
            if not self.groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable is required for GROQ provider")
            self.client = Groq(api_key=self.groq_api_key)
            self.default_model = 'llama3-8b-8192'
        else:
            # Default to OpenAI
            self.provider = 'openai'
            self.api_key = os.getenv('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            self.client = openai.OpenAI(api_key=self.api_key)
            self.default_model = 'gpt-3.5-turbo'
        
        # Configuration
        self.model = model or os.getenv('AI_MODEL', self.default_model)
        self.max_tokens = max_tokens or int(os.getenv('MAX_TOKENS', '500'))
        self.temperature = temperature or float(os.getenv('TEMPERATURE', '0.7'))

        # Analysis context and history
        self.conversation_history = []
        self.analysis_context = {
            'session_start': datetime.now().isoformat(),
            'total_interactions': 0,
            'topics_discussed': [],
            'user_preferences': {}
        }

        logger.info(f"AI Analyzer initialized with {self.provider.upper()} provider, model: {self.model}")
    
    def analyze_text(self, text: str, analysis_type: str = 'general') -> Dict[str, Any]:
        """
        Analyze transcribed text and generate intelligent response
        
        Args:
            text (str): Transcribed text to analyze
            analysis_type (str): Type of analysis ('general', 'sentiment', 'intent', 'summary')
            
        Returns:
            Dict containing analysis results and AI response
        """
        if not text.strip():
            return {
                'error': 'Empty text provided',
                'response': 'I didn\'t hear anything. Could you please speak again?',
                'analysis': {}
            }
        
        try:
            # Update context
            self.analysis_context['total_interactions'] += 1
            
            # Perform analysis based on type
            if analysis_type == 'general':
                return self._general_analysis(text)
            elif analysis_type == 'sentiment':
                return self._sentiment_analysis(text)
            elif analysis_type == 'intent':
                return self._intent_analysis(text)
            elif analysis_type == 'summary':
                return self._summary_analysis(text)
            else:
                return self._general_analysis(text)
                
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                'error': str(e),
                'response': 'I encountered an error while analyzing your speech. Please try again.',
                'analysis': {}
            }
    
    def _general_analysis(self, text: str) -> Dict[str, Any]:
        """Perform general AI analysis and response generation"""
        
        # Create system prompt for general analysis
        system_prompt = """You are an intelligent AI assistant that analyzes speech input and provides helpful responses.
        
        Your tasks:
        1. Understand the user's speech content and intent
        2. Provide relevant, helpful, and contextual responses
        3. Identify key topics, emotions, and any actionable items
        4. Be conversational and engaging
        5. If the user asks questions, provide informative answers
        6. If the user makes statements, acknowledge and expand on the topic appropriately
        
        Respond in a natural, conversational manner as if you're having a real conversation."""
        
        # Build conversation context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history for context
        for interaction in self.conversation_history[-5:]:  # Last 5 interactions
            messages.append({"role": "user", "content": interaction['user_text']})
            messages.append({"role": "assistant", "content": interaction['ai_response']})
        
        # Add current user input
        messages.append({"role": "user", "content": text})
        
        try:
            # Get AI response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Extract analysis information
            analysis = self._extract_analysis_info(text, ai_response)
            
            # Update conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_text': text,
                'ai_response': ai_response,
                'analysis': analysis
            })
            
            # Update topics discussed
            topics = self._extract_topics(text)
            self.analysis_context['topics_discussed'].extend(topics)
            
            return {
                'response': ai_response,
                'analysis': analysis,
                'confidence': response.choices[0].finish_reason == 'stop',
                'model_used': self.model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return {
                'error': str(e),
                'response': 'I\'m having trouble connecting to my AI services. Please try again in a moment.',
                'analysis': {}
            }
    
    def _sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Perform sentiment analysis on the text"""
        
        prompt = f"""Analyze the sentiment of the following text and provide a detailed breakdown:

Text: "{text}"

Please provide:
1. Overall sentiment (positive, negative, neutral)
2. Confidence score (0-1)
3. Specific emotions detected
4. Key phrases that indicate sentiment
5. A brief explanation of the sentiment analysis

Format your response as a structured analysis."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return {
                'response': ai_response,
                'analysis': {
                    'type': 'sentiment',
                    'text_analyzed': text,
                    'detailed_breakdown': ai_response
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                'error': str(e),
                'response': 'Unable to perform sentiment analysis at this time.',
                'analysis': {}
            }
    
    def _intent_analysis(self, text: str) -> Dict[str, Any]:
        """Analyze user intent from the text"""
        
        prompt = f"""Analyze the intent behind the following user speech:

Text: "{text}"

Identify:
1. Primary intent (question, request, statement, command, etc.)
2. Specific action requested (if any)
3. Topic or domain
4. Urgency level
5. Required follow-up actions

Provide a clear analysis of what the user wants or is trying to communicate."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.2
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return {
                'response': ai_response,
                'analysis': {
                    'type': 'intent',
                    'text_analyzed': text,
                    'intent_breakdown': ai_response
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {
                'error': str(e),
                'response': 'Unable to analyze intent at this time.',
                'analysis': {}
            }
    
    def _summary_analysis(self, text: str) -> Dict[str, Any]:
        """Create a summary of the conversation or text"""
        
        if len(self.conversation_history) > 0:
            # Summarize conversation history
            all_text = " ".join([item['user_text'] for item in self.conversation_history])
            all_text += " " + text
            
            prompt = f"""Summarize the following conversation:

{all_text}

Provide:
1. Key topics discussed
2. Main points raised
3. Any decisions or conclusions
4. Action items (if any)
5. Overall conversation theme"""
        else:
            # Summarize just the current text
            prompt = f"""Summarize the following text:

"{text}"

Provide a concise summary highlighting the main points and key information."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return {
                'response': ai_response,
                'analysis': {
                    'type': 'summary',
                    'text_analyzed': text,
                    'summary': ai_response
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Summary analysis failed: {e}")
            return {
                'error': str(e),
                'response': 'Unable to create summary at this time.',
                'analysis': {}
            }
    
    def _extract_analysis_info(self, user_text: str, ai_response: str) -> Dict[str, Any]:
        """Extract analysis information from the interaction"""
        
        return {
            'word_count': len(user_text.split()),
            'character_count': len(user_text),
            'contains_question': '?' in user_text,
            'contains_exclamation': '!' in user_text,
            'response_length': len(ai_response.split()),
            'topics': self._extract_topics(user_text)
        }
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract potential topics from text using simple keyword analysis"""
        
        # Simple topic extraction - can be enhanced with NLP libraries
        common_topics = [
            'weather', 'food', 'work', 'family', 'health', 'technology', 
            'sports', 'music', 'movies', 'travel', 'education', 'business',
            'science', 'politics', 'entertainment', 'shopping', 'cooking'
        ]
        
        text_lower = text.lower()
        found_topics = [topic for topic in common_topics if topic in text_lower]
        
        return found_topics
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of the current conversation session"""
        
        return {
            'session_info': self.analysis_context,
            'total_interactions': len(self.conversation_history),
            'recent_topics': list(set(self.analysis_context['topics_discussed'][-10:])),
            'session_duration': datetime.now().isoformat()
        }
    
    def clear_history(self):
        """Clear conversation history and reset context"""
        
        self.conversation_history = []
        self.analysis_context = {
            'session_start': datetime.now().isoformat(),
            'total_interactions': 0,
            'topics_discussed': [],
            'user_preferences': {}
        }
        logger.info("Conversation history cleared")
