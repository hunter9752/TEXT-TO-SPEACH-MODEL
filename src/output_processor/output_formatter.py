"""
Output Formatter Module
Formats and presents AI analysis results in user-friendly ways
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import textwrap
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FormattedOutput:
    """Data class for formatted output"""
    transcribed_text: str
    ai_response: str
    analysis_data: Dict[str, Any]
    timestamp: str
    formatted_display: str
    json_data: str


class OutputFormatter:
    """
    Output formatter for presenting speech-to-text AI analysis results
    """
    
    def __init__(self, output_style: str = 'conversational'):
        """
        Initialize output formatter
        
        Args:
            output_style (str): Output style ('conversational', 'detailed', 'minimal', 'json')
        """
        self.output_style = output_style
        self.session_outputs = []
        
        # Display configuration
        self.max_line_width = 80
        self.indent_size = 2
        
        logger.info(f"Output formatter initialized with style: {output_style}")
    
    def format_response(self, transcribed_text: str, ai_analysis: Dict[str, Any]) -> str:
        """
        Format the complete response for display
        
        Args:
            transcribed_text (str): Original transcribed text
            ai_analysis (dict): AI analysis results
            
        Returns:
            str: Formatted output string
        """
        try:
            # Create formatted output object
            formatted_output = FormattedOutput(
                transcribed_text=transcribed_text,
                ai_response=ai_analysis.get('response', ''),
                analysis_data=ai_analysis.get('analysis', {}),
                timestamp=ai_analysis.get('timestamp', datetime.now().isoformat()),
                formatted_display='',
                json_data=''
            )
            
            # Format based on style
            if self.output_style == 'conversational':
                formatted_output.formatted_display = self._format_conversational(formatted_output)
            elif self.output_style == 'detailed':
                formatted_output.formatted_display = self._format_detailed(formatted_output)
            elif self.output_style == 'minimal':
                formatted_output.formatted_display = self._format_minimal(formatted_output)
            elif self.output_style == 'json':
                formatted_output.formatted_display = self._format_json(formatted_output)
            else:
                formatted_output.formatted_display = self._format_conversational(formatted_output)
            
            # Store in session history
            self.session_outputs.append(formatted_output)
            
            return formatted_output.formatted_display
            
        except Exception as e:
            logger.error(f"Output formatting failed: {e}")
            return f"Error formatting output: {str(e)}"
    
    def _format_conversational(self, output: FormattedOutput) -> str:
        """Format output in conversational style"""
        
        lines = []
        
        # Header with timestamp
        time_str = datetime.fromisoformat(output.timestamp.replace('Z', '+00:00')).strftime('%H:%M:%S')
        lines.append(f"🎤 [{time_str}] You said:")
        lines.append(f"   \"{output.transcribed_text}\"")
        lines.append("")
        
        # AI Response
        lines.append("🤖 AI Response:")
        wrapped_response = textwrap.fill(
            output.ai_response, 
            width=self.max_line_width - 3,
            initial_indent="   ",
            subsequent_indent="   "
        )
        lines.append(wrapped_response)
        
        # Quick analysis summary (if available)
        if output.analysis_data:
            lines.append("")
            lines.append("📊 Quick Analysis:")
            
            # Word count
            if 'word_count' in output.analysis_data:
                lines.append(f"   • Words spoken: {output.analysis_data['word_count']}")
            
            # Topics
            if 'topics' in output.analysis_data and output.analysis_data['topics']:
                topics_str = ", ".join(output.analysis_data['topics'])
                lines.append(f"   • Topics: {topics_str}")
            
            # Question/exclamation indicators
            if output.analysis_data.get('contains_question'):
                lines.append("   • Contains question")
            if output.analysis_data.get('contains_exclamation'):
                lines.append("   • Contains exclamation")
        
        return "\n".join(lines)
    
    def _format_detailed(self, output: FormattedOutput) -> str:
        """Format output with detailed analysis"""
        
        lines = []
        
        # Header
        lines.append("=" * self.max_line_width)
        lines.append("SPEECH-TO-TEXT AI ANALYSIS REPORT")
        lines.append("=" * self.max_line_width)
        lines.append(f"Timestamp: {output.timestamp}")
        lines.append("")
        
        # Input Section
        lines.append("📝 TRANSCRIBED INPUT:")
        lines.append("-" * 40)
        wrapped_input = textwrap.fill(
            f'"{output.transcribed_text}"',
            width=self.max_line_width,
            initial_indent="",
            subsequent_indent=""
        )
        lines.append(wrapped_input)
        lines.append("")
        
        # AI Response Section
        lines.append("🤖 AI RESPONSE:")
        lines.append("-" * 40)
        wrapped_response = textwrap.fill(
            output.ai_response,
            width=self.max_line_width,
            initial_indent="",
            subsequent_indent=""
        )
        lines.append(wrapped_response)
        lines.append("")
        
        # Detailed Analysis Section
        if output.analysis_data:
            lines.append("📊 DETAILED ANALYSIS:")
            lines.append("-" * 40)
            
            for key, value in output.analysis_data.items():
                if isinstance(value, (list, dict)):
                    lines.append(f"{key.replace('_', ' ').title()}:")
                    if isinstance(value, list):
                        for item in value:
                            lines.append(f"  • {item}")
                    else:
                        for sub_key, sub_value in value.items():
                            lines.append(f"  • {sub_key}: {sub_value}")
                else:
                    lines.append(f"{key.replace('_', ' ').title()}: {value}")
            lines.append("")
        
        lines.append("=" * self.max_line_width)
        
        return "\n".join(lines)
    
    def _format_minimal(self, output: FormattedOutput) -> str:
        """Format output in minimal style"""
        
        return f"You: {output.transcribed_text}\nAI: {output.ai_response}"
    
    def _format_json(self, output: FormattedOutput) -> str:
        """Format output as JSON"""
        
        json_data = {
            'timestamp': output.timestamp,
            'input': {
                'transcribed_text': output.transcribed_text,
                'word_count': len(output.transcribed_text.split())
            },
            'ai_response': output.ai_response,
            'analysis': output.analysis_data
        }
        
        return json.dumps(json_data, indent=2, ensure_ascii=False)
    
    def format_error(self, error_message: str, context: Optional[str] = None) -> str:
        """
        Format error messages
        
        Args:
            error_message (str): Error message to format
            context (str): Optional context information
            
        Returns:
            str: Formatted error message
        """
        lines = []
        
        if self.output_style == 'json':
            error_data = {
                'error': True,
                'message': error_message,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            return json.dumps(error_data, indent=2)
        
        lines.append("❌ ERROR:")
        lines.append(f"   {error_message}")
        
        if context:
            lines.append(f"   Context: {context}")
        
        lines.append(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        
        return "\n".join(lines)
    
    def format_system_message(self, message: str, message_type: str = 'info') -> str:
        """
        Format system messages
        
        Args:
            message (str): System message
            message_type (str): Type of message ('info', 'warning', 'success')
            
        Returns:
            str: Formatted system message
        """
        if self.output_style == 'json':
            system_data = {
                'system_message': True,
                'type': message_type,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            return json.dumps(system_data, indent=2)
        
        icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'success': '✅',
            'error': '❌'
        }
        
        icon = icons.get(message_type, 'ℹ️')
        time_str = datetime.now().strftime('%H:%M:%S')
        
        return f"{icon} [{time_str}] {message}"
    
    def get_session_summary(self) -> str:
        """
        Generate a summary of the current session
        
        Returns:
            str: Session summary
        """
        if not self.session_outputs:
            return self.format_system_message("No interactions in this session yet.", 'info')
        
        total_interactions = len(self.session_outputs)
        total_words_spoken = sum(
            len(output.transcribed_text.split()) 
            for output in self.session_outputs
        )
        
        # Collect all topics
        all_topics = []
        for output in self.session_outputs:
            if 'topics' in output.analysis_data:
                all_topics.extend(output.analysis_data['topics'])
        
        unique_topics = list(set(all_topics))
        
        if self.output_style == 'json':
            summary_data = {
                'session_summary': True,
                'total_interactions': total_interactions,
                'total_words_spoken': total_words_spoken,
                'unique_topics': unique_topics,
                'session_start': self.session_outputs[0].timestamp if self.session_outputs else None,
                'session_end': self.session_outputs[-1].timestamp if self.session_outputs else None
            }
            return json.dumps(summary_data, indent=2)
        
        lines = []
        lines.append("📈 SESSION SUMMARY:")
        lines.append(f"   • Total interactions: {total_interactions}")
        lines.append(f"   • Total words spoken: {total_words_spoken}")
        
        if unique_topics:
            topics_str = ", ".join(unique_topics[:5])  # Show first 5 topics
            if len(unique_topics) > 5:
                topics_str += f" (and {len(unique_topics) - 5} more)"
            lines.append(f"   • Topics discussed: {topics_str}")
        
        if self.session_outputs:
            start_time = datetime.fromisoformat(self.session_outputs[0].timestamp.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(self.session_outputs[-1].timestamp.replace('Z', '+00:00'))
            duration = end_time - start_time
            lines.append(f"   • Session duration: {duration}")
        
        return "\n".join(lines)
    
    def export_session(self, file_path: str, format: str = 'json') -> bool:
        """
        Export session data to file
        
        Args:
            file_path (str): Output file path
            format (str): Export format ('json', 'txt', 'csv')
            
        Returns:
            bool: True if export successful
        """
        try:
            if format == 'json':
                session_data = {
                    'session_info': {
                        'total_interactions': len(self.session_outputs),
                        'export_timestamp': datetime.now().isoformat()
                    },
                    'interactions': [
                        {
                            'timestamp': output.timestamp,
                            'transcribed_text': output.transcribed_text,
                            'ai_response': output.ai_response,
                            'analysis': output.analysis_data
                        }
                        for output in self.session_outputs
                    ]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            elif format == 'txt':
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("SPEECH-TO-TEXT AI SESSION EXPORT\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, output in enumerate(self.session_outputs, 1):
                        f.write(f"INTERACTION {i}\n")
                        f.write(f"Time: {output.timestamp}\n")
                        f.write(f"Input: {output.transcribed_text}\n")
                        f.write(f"AI Response: {output.ai_response}\n")
                        f.write("-" * 30 + "\n\n")
            
            logger.info(f"Session exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def clear_session(self):
        """Clear session output history"""
        self.session_outputs = []
        logger.info("Session output history cleared")
    
    def set_output_style(self, style: str):
        """
        Change output formatting style
        
        Args:
            style (str): New output style
        """
        valid_styles = ['conversational', 'detailed', 'minimal', 'json']
        if style in valid_styles:
            self.output_style = style
            logger.info(f"Output style changed to: {style}")
        else:
            logger.warning(f"Invalid output style: {style}. Valid options: {valid_styles}")
