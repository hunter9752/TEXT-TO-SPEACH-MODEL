"""
Web Interface for Speech-to-Text AI System
Flask-based web application
"""

import os
import sys
import tempfile
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from speech_to_text.speech_recognizer import SpeechRecognizer
from ai_analysis.ai_analyzer import AIAnalyzer
from audio_handler.audio_input import AudioInputHandler
from output_processor.output_formatter import OutputFormatter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global system components
speech_recognizer = None
ai_analyzer = None
audio_handler = None
output_formatter = None


def create_app():
    """Create and configure Flask application"""
    # Get the project root directory (two levels up from this file)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(project_root, 'templates')
    static_dir = os.path.join(project_root, 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Enable CORS
    CORS(app)
    
    # Initialize system components
    global speech_recognizer, ai_analyzer, audio_handler, output_formatter
    try:
        speech_recognizer = SpeechRecognizer()
        ai_analyzer = AIAnalyzer()
        audio_handler = AudioInputHandler()
        output_formatter = OutputFormatter(output_style='conversational')
        logger.info("System components initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize system components: {e}")
    
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/api/process-audio', methods=['POST'])
    def process_audio():
        """Process uploaded audio file"""
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400
            
            file = request.files['audio']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)
            file.save(temp_path)
            
            try:
                # Process the audio file
                try:
                    audio_data = audio_handler.load_audio_file(temp_path)
                    if not audio_data:
                        return jsonify({'error': 'Failed to load audio file'}), 400
                except RuntimeError as e:
                    # Handle FFmpeg missing error specifically
                    error_msg = str(e)
                    if "FFmpeg is required" in error_msg:
                        return jsonify({
                            'error': 'FFmpeg Required',
                            'message': error_msg,
                            'solution': 'Please convert your audio file to WAV format or install FFmpeg'
                        }), 400
                    else:
                        return jsonify({'error': f'Audio processing error: {error_msg}'}), 400
                except Exception as e:
                    return jsonify({'error': f'Failed to process audio file: {str(e)}'}), 400
                
                # Transcribe speech
                transcribed_text = speech_recognizer.transcribe_audio(audio_data)
                if not transcribed_text.strip():
                    return jsonify({'error': 'No speech detected in audio'}), 400
                
                # Analyze with AI
                ai_response = ai_analyzer.analyze_text(transcribed_text)
                
                # Format output
                formatted_output = output_formatter.format_response(transcribed_text, ai_response)
                
                return jsonify({
                    'success': True,
                    'transcribed_text': transcribed_text,
                    'ai_response': ai_response.get('response', ''),
                    'analysis': ai_response.get('analysis', {}),
                    'formatted_output': formatted_output,
                    'timestamp': ai_response.get('timestamp')
                })
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    
    @app.route('/api/analyze-text', methods=['POST'])
    def analyze_text():
        """Analyze text directly (for testing)"""
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'error': 'No text provided'}), 400
            
            text = data['text'].strip()
            if not text:
                return jsonify({'error': 'Empty text provided'}), 400
            
            analysis_type = data.get('analysis_type', 'general')
            
            # Analyze with AI
            ai_response = ai_analyzer.analyze_text(text, analysis_type)
            
            # Format output
            formatted_output = output_formatter.format_response(text, ai_response)
            
            return jsonify({
                'success': True,
                'input_text': text,
                'ai_response': ai_response.get('response', ''),
                'analysis': ai_response.get('analysis', {}),
                'formatted_output': formatted_output,
                'timestamp': ai_response.get('timestamp')
            })
            
        except Exception as e:
            logger.error(f"Text analysis error: {e}")
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
    
    @app.route('/api/microphones', methods=['GET'])
    def get_microphones():
        """Get available microphone devices"""
        try:
            microphones = audio_handler.get_available_microphones()
            return jsonify({
                'success': True,
                'microphones': microphones
            })
        except Exception as e:
            logger.error(f"Failed to get microphones: {e}")
            return jsonify({'error': f'Failed to get microphones: {str(e)}'}), 500
    
    @app.route('/api/session-summary', methods=['GET'])
    def get_session_summary():
        """Get current session summary"""
        try:
            summary = output_formatter.get_session_summary()
            return jsonify({
                'success': True,
                'summary': summary
            })
        except Exception as e:
            logger.error(f"Failed to get session summary: {e}")
            return jsonify({'error': f'Failed to get summary: {str(e)}'}), 500
    
    @app.route('/api/clear-session', methods=['POST'])
    def clear_session():
        """Clear current session"""
        try:
            output_formatter.clear_session()
            ai_analyzer.clear_history()
            return jsonify({
                'success': True,
                'message': 'Session cleared successfully'
            })
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return jsonify({'error': f'Failed to clear session: {str(e)}'}), 500
    
    @app.route('/api/settings', methods=['GET', 'POST'])
    def handle_settings():
        """Get or update application settings"""
        if request.method == 'GET':
            try:
                settings = {
                    'speech_engine': speech_recognizer.engine if speech_recognizer else 'whisper',
                    'ai_model': ai_analyzer.model if ai_analyzer else 'gpt-3.5-turbo',
                    'output_style': output_formatter.output_style if output_formatter else 'conversational',
                    'available_engines': speech_recognizer.get_available_engines() if speech_recognizer else [],
                    'max_tokens': ai_analyzer.max_tokens if ai_analyzer else 500,
                    'temperature': ai_analyzer.temperature if ai_analyzer else 0.7
                }
                return jsonify({
                    'success': True,
                    'settings': settings
                })
            except Exception as e:
                logger.error(f"Failed to get settings: {e}")
                return jsonify({'error': f'Failed to get settings: {str(e)}'}), 500
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No settings data provided'}), 400
                
                # Update output style
                if 'output_style' in data and output_formatter:
                    output_formatter.set_output_style(data['output_style'])
                
                # Note: Other settings would require reinitializing components
                # For now, we'll just acknowledge the request
                
                return jsonify({
                    'success': True,
                    'message': 'Settings updated successfully'
                })
                
            except Exception as e:
                logger.error(f"Failed to update settings: {e}")
                return jsonify({'error': f'Failed to update settings: {str(e)}'}), 500
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            status = {
                'speech_recognizer': speech_recognizer is not None,
                'ai_analyzer': ai_analyzer is not None,
                'audio_handler': audio_handler is not None,
                'output_formatter': output_formatter is not None,
                'openai_api_key': bool(os.getenv('OPENAI_API_KEY'))
            }
            
            all_healthy = all(status.values())
            
            return jsonify({
                'success': True,
                'healthy': all_healthy,
                'components': status,
                'timestamp': ai_analyzer.analysis_context['session_start'] if ai_analyzer else None
            }), 200 if all_healthy else 503
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.errorhandler(413)
    def too_large(e):
        """Handle file too large error"""
        return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413
    
    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 errors"""
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        """Handle internal server errors"""
        logger.error(f"Internal server error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Speech-to-Text AI Web Interface on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
