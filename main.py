#!/usr/bin/env python3
"""
Speech-to-Text AI Analysis System
Main application entry point
"""

import argparse
import os
import sys
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from speech_to_text.speech_recognizer import SpeechRecognizer
from ai_analysis.ai_analyzer import AIAnalyzer
from audio_handler.audio_input import AudioInputHandler
from output_processor.output_formatter import OutputFormatter
from web_interface.app import create_app


class SpeechToTextAISystem:
    """Main system orchestrator"""
    
    def __init__(self):
        load_dotenv()
        self.speech_recognizer = SpeechRecognizer()
        self.ai_analyzer = AIAnalyzer()
        self.audio_handler = AudioInputHandler()
        self.output_formatter = OutputFormatter()
    
    def process_audio_file(self, file_path):
        """Process an audio file through the complete pipeline"""
        try:
            print(f"Processing audio file: {file_path}")
            
            # Step 1: Load and prepare audio
            audio_data = self.audio_handler.load_audio_file(file_path)
            
            # Step 2: Convert speech to text
            print("Converting speech to text...")
            transcribed_text = self.speech_recognizer.transcribe_audio(audio_data)
            print(f"Transcribed: {transcribed_text}")
            
            # Step 3: Analyze with AI
            print("Analyzing with AI...")
            ai_response = self.ai_analyzer.analyze_text(transcribed_text)
            
            # Step 4: Format output
            formatted_output = self.output_formatter.format_response(
                transcribed_text, ai_response
            )
            
            return formatted_output
            
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            return None
    
    def process_live_audio(self):
        """Process live microphone input"""
        try:
            print("Starting live audio processing. Speak into your microphone...")
            print("Press Ctrl+C to stop.")
            
            while True:
                # Step 1: Capture audio from microphone
                audio_data = self.audio_handler.capture_live_audio()
                
                if audio_data:
                    # Step 2: Convert speech to text
                    transcribed_text = self.speech_recognizer.transcribe_audio(audio_data)
                    
                    if transcribed_text.strip():
                        print(f"\nYou said: {transcribed_text}")
                        
                        # Step 3: Analyze with AI
                        ai_response = self.ai_analyzer.analyze_text(transcribed_text)
                        
                        # Step 4: Format and display output
                        formatted_output = self.output_formatter.format_response(
                            transcribed_text, ai_response
                        )
                        print(formatted_output)
                        print("\n" + "="*50 + "\n")
                
        except KeyboardInterrupt:
            print("\nStopping live audio processing...")
        except Exception as e:
            print(f"Error in live audio processing: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Speech-to-Text AI Analysis System')
    parser.add_argument('--mode', choices=['cli', 'web', 'file'], default='cli',
                       help='Run mode: cli (live audio), web (web interface), or file (process audio file)')
    parser.add_argument('--file', type=str, help='Audio file path (required for file mode)')
    parser.add_argument('--port', type=int, default=5000, help='Port for web interface')
    
    args = parser.parse_args()
    
    if args.mode == 'file':
        if not args.file:
            print("Error: --file argument is required for file mode")
            sys.exit(1)
        
        system = SpeechToTextAISystem()
        result = system.process_audio_file(args.file)
        if result:
            print("\n" + "="*50)
            print("FINAL RESULT:")
            print("="*50)
            print(result)
    
    elif args.mode == 'cli':
        system = SpeechToTextAISystem()
        system.process_live_audio()
    
    elif args.mode == 'web':
        app = create_app()
        print(f"Starting web interface on http://localhost:{args.port}")
        app.run(host='0.0.0.0', port=args.port, debug=True)


if __name__ == '__main__':
    main()
