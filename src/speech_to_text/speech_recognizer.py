"""
Speech Recognition Module
Handles conversion of audio to text using multiple recognition engines
"""

import os
import speech_recognition as sr
import tempfile
import numpy as np
from typing import Optional, Union
import logging

# Optional whisper import
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """
    Speech recognition class supporting multiple engines:
    - Google Speech Recognition (online)
    - OpenAI Whisper (offline)
    - Azure Speech Services (online)
    """
    
    def __init__(self, engine='whisper', whisper_model='base'):
        """
        Initialize speech recognizer
        
        Args:
            engine (str): Recognition engine ('whisper', 'google', 'azure')
            whisper_model (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.engine = engine
        self.recognizer = sr.Recognizer()
        
        # Configure recognition settings
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        
        # Initialize Whisper if selected and available
        if engine == 'whisper':
            if WHISPER_AVAILABLE:
                try:
                    logger.info(f"Loading Whisper model: {whisper_model}")
                    self.whisper_model = whisper.load_model(whisper_model)
                    logger.info("Whisper model loaded successfully")
                except Exception as e:
                    logger.error(f"Failed to load Whisper model: {e}")
                    self.whisper_model = None
            else:
                logger.warning("Whisper not available, falling back to Google Speech Recognition")
                self.engine = 'google'
                self.whisper_model = None
    
    def transcribe_audio(self, audio_data: Union[sr.AudioData, str, np.ndarray]) -> str:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Audio data (AudioData object, file path, or numpy array)
            
        Returns:
            str: Transcribed text
        """
        try:
            if self.engine == 'whisper':
                return self._transcribe_with_whisper(audio_data)
            elif self.engine == 'google':
                return self._transcribe_with_google(audio_data)
            elif self.engine == 'azure':
                return self._transcribe_with_azure(audio_data)
            else:
                raise ValueError(f"Unsupported engine: {self.engine}")
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
    
    def _transcribe_with_whisper(self, audio_data: Union[sr.AudioData, str, np.ndarray]) -> str:
        """Transcribe using OpenAI Whisper (offline)"""
        if not self.whisper_model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Handle different audio data types
            if isinstance(audio_data, str):
                # File path
                result = self.whisper_model.transcribe(audio_data)
                return result["text"].strip()
            
            elif isinstance(audio_data, sr.AudioData):
                # AudioData object - save to temp file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_path = temp_file.name
                    
                # Convert AudioData to WAV file
                wav_data = audio_data.get_wav_data()
                with open(temp_path, 'wb') as f:
                    f.write(wav_data)
                
                try:
                    result = self.whisper_model.transcribe(temp_path)
                    return result["text"].strip()
                finally:
                    os.unlink(temp_path)
            
            elif isinstance(audio_data, np.ndarray):
                # Numpy array
                result = self.whisper_model.transcribe(audio_data)
                return result["text"].strip()
            
            else:
                raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
                
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return ""
    
    def _transcribe_with_google(self, audio_data: sr.AudioData) -> str:
        """Transcribe using Google Speech Recognition (online)"""
        try:
            text = self.recognizer.recognize_google(audio_data)
            return text.strip()
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Google Speech Recognition error: {e}")
            return ""
    
    def _transcribe_with_azure(self, audio_data: sr.AudioData) -> str:
        """Transcribe using Azure Speech Services (online)"""
        try:
            # Requires Azure Speech API key
            azure_key = os.getenv('AZURE_SPEECH_KEY')
            azure_region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
            
            if not azure_key:
                raise ValueError("AZURE_SPEECH_KEY environment variable not set")
            
            text = self.recognizer.recognize_azure(
                audio_data, 
                key=azure_key, 
                location=azure_region
            )
            return text.strip()
        except sr.UnknownValueError:
            logger.warning("Azure Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Azure Speech Recognition error: {e}")
            return ""
    
    def set_microphone_settings(self, energy_threshold: int = 300, 
                               pause_threshold: float = 0.8):
        """
        Configure microphone sensitivity settings
        
        Args:
            energy_threshold (int): Minimum audio energy to consider for recording
            pause_threshold (float): Seconds of silence to mark end of phrase
        """
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        logger.info(f"Microphone settings updated: energy={energy_threshold}, pause={pause_threshold}")
    
    def calibrate_microphone(self, microphone: sr.Microphone, duration: float = 1.0):
        """
        Calibrate microphone for ambient noise
        
        Args:
            microphone: Microphone object
            duration (float): Calibration duration in seconds
        """
        try:
            logger.info(f"Calibrating microphone for {duration} seconds...")
            with microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            logger.info(f"Microphone calibrated. Energy threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            logger.error(f"Microphone calibration failed: {e}")
    
    def get_available_engines(self) -> list:
        """Get list of available recognition engines"""
        engines = ['whisper']
        
        # Check if online services are available
        try:
            # Test Google
            test_audio = sr.AudioData(b'', 16000, 2)
            self.recognizer.recognize_google(test_audio)
            engines.append('google')
        except:
            pass
        
        if os.getenv('AZURE_SPEECH_KEY'):
            engines.append('azure')
        
        return engines
