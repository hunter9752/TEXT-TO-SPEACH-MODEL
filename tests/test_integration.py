"""
Integration tests for Speech-to-Text AI System
"""

import os
import sys
import unittest
import tempfile
import wave
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from speech_to_text.speech_recognizer import SpeechRecognizer
from ai_analysis.ai_analyzer import AIAnalyzer
from audio_handler.audio_input import AudioInputHandler
from output_processor.output_formatter import OutputFormatter


class TestSpeechToTextIntegration(unittest.TestCase):
    """Integration tests for the complete speech-to-text AI pipeline"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
        
        # Initialize components with mocked dependencies
        self.speech_recognizer = SpeechRecognizer(engine='whisper')
        self.ai_analyzer = AIAnalyzer()
        self.audio_handler = AudioInputHandler()
        self.output_formatter = OutputFormatter()
    
    def create_test_audio_file(self, duration=1.0, sample_rate=16000):
        """Create a test audio file"""
        # Generate a simple sine wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
        
        # Convert to 16-bit integers
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Create temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return temp_file.name
    
    def test_output_formatter_initialization(self):
        """Test output formatter initialization"""
        formatter = OutputFormatter(output_style='conversational')
        self.assertEqual(formatter.output_style, 'conversational')
        self.assertEqual(len(formatter.session_outputs), 0)
    
    def test_output_formatter_styles(self):
        """Test different output formatting styles"""
        test_text = "Hello world"
        test_analysis = {
            'response': 'Hello! How can I help you today?',
            'analysis': {
                'word_count': 2,
                'topics': ['greeting']
            },
            'timestamp': '2023-01-01T12:00:00'
        }
        
        # Test conversational style
        formatter = OutputFormatter(output_style='conversational')
        result = formatter.format_response(test_text, test_analysis)
        self.assertIn('You said:', result)
        self.assertIn('AI Response:', result)
        
        # Test minimal style
        formatter.set_output_style('minimal')
        result = formatter.format_response(test_text, test_analysis)
        self.assertIn('You:', result)
        self.assertIn('AI:', result)
        
        # Test JSON style
        formatter.set_output_style('json')
        result = formatter.format_response(test_text, test_analysis)
        self.assertTrue(result.startswith('{'))
        self.assertTrue(result.endswith('}'))
    
    def test_audio_handler_initialization(self):
        """Test audio handler initialization"""
        handler = AudioInputHandler()
        self.assertIsNotNone(handler.sample_rate)
        self.assertIsNotNone(handler.chunk_size)
    
    @patch('speech_recognition.Recognizer')
    def test_audio_file_loading(self, mock_recognizer):
        """Test loading audio files"""
        # Create a test audio file
        test_file = self.create_test_audio_file()
        
        try:
            # Mock the recognizer
            mock_recognizer_instance = Mock()
            mock_recognizer.return_value = mock_recognizer_instance
            
            handler = AudioInputHandler()
            
            # Test file existence check
            self.assertTrue(os.path.exists(test_file))
            
            # Test non-existent file
            result = handler.load_audio_file('non_existent_file.wav')
            self.assertIsNone(result)
            
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    @patch('openai.ChatCompletion.create')
    def test_ai_analyzer_text_processing(self, mock_openai):
        """Test AI analyzer text processing"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a test response from AI."
        mock_response.choices[0].finish_reason = "stop"
        mock_openai.return_value = mock_response
        
        analyzer = AIAnalyzer()
        
        # Test general analysis
        result = analyzer.analyze_text("Hello, how are you?")
        
        self.assertIn('response', result)
        self.assertIn('analysis', result)
        self.assertEqual(result['response'], "This is a test response from AI.")
        
        # Test empty text
        result = analyzer.analyze_text("")
        self.assertIn('error', result)
    
    def test_speech_recognizer_initialization(self):
        """Test speech recognizer initialization"""
        # Test with different engines
        recognizer = SpeechRecognizer(engine='whisper')
        self.assertEqual(recognizer.engine, 'whisper')
        
        recognizer = SpeechRecognizer(engine='google')
        self.assertEqual(recognizer.engine, 'google')
    
    @patch('whisper.load_model')
    def test_whisper_model_loading(self, mock_load_model):
        """Test Whisper model loading"""
        # Mock Whisper model
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        recognizer = SpeechRecognizer(engine='whisper', whisper_model='base')
        self.assertIsNotNone(recognizer.whisper_model)
        mock_load_model.assert_called_with('base')
    
    def test_session_management(self):
        """Test session management functionality"""
        formatter = OutputFormatter()
        
        # Test empty session
        summary = formatter.get_session_summary()
        self.assertIn('No interactions', summary)
        
        # Add some test interactions
        test_analysis = {
            'response': 'Test response',
            'analysis': {'word_count': 3, 'topics': ['test']},
            'timestamp': '2023-01-01T12:00:00'
        }
        
        formatter.format_response("Test input", test_analysis)
        
        # Test session with interactions
        summary = formatter.get_session_summary()
        self.assertIn('Total interactions: 1', summary)
        
        # Test session clearing
        formatter.clear_session()
        self.assertEqual(len(formatter.session_outputs), 0)
    
    def test_error_handling(self):
        """Test error handling throughout the system"""
        formatter = OutputFormatter()
        
        # Test error formatting
        error_msg = formatter.format_error("Test error", "Test context")
        self.assertIn('ERROR:', error_msg)
        self.assertIn('Test error', error_msg)
        
        # Test system message formatting
        system_msg = formatter.format_system_message("System ready", "success")
        self.assertIn('System ready', system_msg)
    
    @patch('openai.ChatCompletion.create')
    def test_complete_pipeline_simulation(self, mock_openai):
        """Test the complete pipeline with mocked components"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "I understand you said 'Hello world'. How can I help you today?"
        mock_response.choices[0].finish_reason = "stop"
        mock_openai.return_value = mock_response
        
        # Initialize all components
        analyzer = AIAnalyzer()
        formatter = OutputFormatter()
        
        # Simulate the pipeline
        transcribed_text = "Hello world"
        
        # Step 1: AI Analysis
        ai_result = analyzer.analyze_text(transcribed_text)
        
        # Step 2: Format output
        formatted_result = formatter.format_response(transcribed_text, ai_result)
        
        # Verify results
        self.assertIsNotNone(formatted_result)
        self.assertIn('Hello world', formatted_result)
        self.assertIn('AI Response:', formatted_result)
    
    def test_configuration_loading(self):
        """Test configuration loading from environment"""
        # Test with custom environment variables
        os.environ['AI_MODEL'] = 'gpt-4'
        os.environ['MAX_TOKENS'] = '1000'
        os.environ['TEMPERATURE'] = '0.5'
        
        analyzer = AIAnalyzer()
        
        self.assertEqual(analyzer.model, 'gpt-4')
        self.assertEqual(analyzer.max_tokens, 1000)
        self.assertEqual(analyzer.temperature, 0.5)
    
    def tearDown(self):
        """Clean up after tests"""
        # Clean up environment variables
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']


class TestWebIntegration(unittest.TestCase):
    """Test web interface integration"""
    
    def setUp(self):
        """Set up test environment for web interface"""
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    @patch('src.web_interface.app.SpeechRecognizer')
    @patch('src.web_interface.app.AIAnalyzer')
    @patch('src.web_interface.app.AudioInputHandler')
    @patch('src.web_interface.app.OutputFormatter')
    def test_app_creation(self, mock_formatter, mock_audio, mock_ai, mock_speech):
        """Test Flask app creation"""
        from web_interface.app import create_app
        
        app = create_app()
        self.assertIsNotNone(app)
        
        # Test that the app has the expected routes
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/api/health')
            self.assertEqual(response.status_code, 200)
    
    def tearDown(self):
        """Clean up after web tests"""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
