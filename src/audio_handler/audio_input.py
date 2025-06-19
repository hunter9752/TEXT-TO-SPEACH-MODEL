"""
Audio Input Handler Module
Handles audio input from microphone and file sources
"""

import os
import wave
import speech_recognition as sr
import numpy as np
from pydub import AudioSegment
from pydub.utils import which
import tempfile
import logging
import threading
import queue
import time
import io
from typing import Optional, Tuple, List

# Optional pyaudio import
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    pyaudio = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioInputHandler:
    """
    Audio input handler for microphone and file-based audio processing
    """
    
    def __init__(self, sample_rate: int = None, chunk_size: int = None):
        """
        Initialize audio input handler
        
        Args:
            sample_rate (int): Audio sample rate (default from env or 16000)
            chunk_size (int): Audio chunk size (default from env or 1024)
        """
        self.sample_rate = sample_rate or int(os.getenv('AUDIO_SAMPLE_RATE', '16000'))
        self.chunk_size = chunk_size or int(os.getenv('AUDIO_CHUNK_SIZE', '1024'))
        
        # Audio format settings
        if PYAUDIO_AVAILABLE:
            self.format = pyaudio.paInt16
        else:
            self.format = None
        self.channels = 1

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = None

        # Audio recording state
        self.is_recording = False
        self.audio_queue = queue.Queue()

        # Initialize PyAudio if available
        if PYAUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
                logger.info("PyAudio initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize PyAudio: {e}")
                self.audio = None
        else:
            logger.warning("PyAudio not available - microphone input will not work")
            self.audio = None
        
        # Check for ffmpeg (required for pydub)
        if not which("ffmpeg"):
            logger.warning("ffmpeg not found. Some audio formats may not be supported.")
    
    def get_available_microphones(self) -> List[dict]:
        """Get list of available microphone devices"""
        if not self.audio:
            return []
        
        devices = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': device_info['defaultSampleRate']
                })
        
        return devices
    
    def setup_microphone(self, device_index: Optional[int] = None) -> bool:
        """
        Setup microphone for recording
        
        Args:
            device_index (int): Specific microphone device index (None for default)
            
        Returns:
            bool: True if setup successful
        """
        try:
            self.microphone = sr.Microphone(
                device_index=device_index,
                sample_rate=self.sample_rate,
                chunk_size=self.chunk_size
            )
            
            # Calibrate for ambient noise
            logger.info("Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            logger.info(f"Microphone setup complete. Energy threshold: {self.recognizer.energy_threshold}")
            return True
            
        except Exception as e:
            logger.error(f"Microphone setup failed: {e}")
            return False
    
    def capture_live_audio(self, timeout: float = None, phrase_timeout: float = None) -> Optional[sr.AudioData]:
        """
        Capture audio from microphone
        
        Args:
            timeout (float): Maximum time to wait for speech (None for no timeout)
            phrase_timeout (float): Time to wait after speech ends (None for default)
            
        Returns:
            AudioData object or None if no audio captured
        """
        if not self.microphone:
            if not self.setup_microphone():
                logger.error("Cannot capture audio: microphone not available")
                return None
        
        try:
            # Set timeouts
            speech_timeout = timeout or float(os.getenv('SPEECH_RECOGNITION_TIMEOUT', '5'))
            phrase_timeout = phrase_timeout or float(os.getenv('SPEECH_RECOGNITION_PHRASE_TIMEOUT', '1'))
            
            logger.info("Listening for speech...")
            
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=speech_timeout,
                    phrase_time_limit=phrase_timeout
                )
            
            logger.info("Audio captured successfully")
            return audio
            
        except sr.WaitTimeoutError:
            logger.info("No speech detected within timeout period")
            return None
        except Exception as e:
            logger.error(f"Audio capture failed: {e}")
            return None
    
    def start_continuous_recording(self, callback_func=None):
        """
        Start continuous audio recording in background thread
        
        Args:
            callback_func: Function to call when audio is captured
        """
        if self.is_recording:
            logger.warning("Recording already in progress")
            return
        
        if not self.microphone:
            if not self.setup_microphone():
                logger.error("Cannot start recording: microphone not available")
                return
        
        self.is_recording = True
        self.recording_thread = threading.Thread(
            target=self._continuous_recording_worker,
            args=(callback_func,)
        )
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        logger.info("Continuous recording started")
    
    def stop_continuous_recording(self):
        """Stop continuous audio recording"""
        self.is_recording = False
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join(timeout=2)
        logger.info("Continuous recording stopped")
    
    def _continuous_recording_worker(self, callback_func):
        """Worker function for continuous recording"""
        while self.is_recording:
            try:
                audio = self.capture_live_audio(timeout=1, phrase_timeout=0.5)
                if audio and callback_func:
                    callback_func(audio)
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            except Exception as e:
                logger.error(f"Error in continuous recording: {e}")
                time.sleep(1)  # Wait before retrying
    
    def load_audio_file(self, file_path: str) -> Optional[sr.AudioData]:
        """
        Load audio from file
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            AudioData object or None if loading failed
        """
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return None
        
        try:
            # Get file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.wav':
                return self._load_wav_file(file_path)
            else:
                return self._load_other_audio_file(file_path)
                
        except Exception as e:
            logger.error(f"Failed to load audio file {file_path}: {e}")
            return None
    
    def _load_wav_file(self, file_path: str) -> sr.AudioData:
        """Load WAV file directly"""
        with sr.AudioFile(file_path) as source:
            audio = self.recognizer.record(source)
        return audio
    
    def _load_other_audio_file(self, file_path: str) -> sr.AudioData:
        """Load non-WAV audio file using pydub"""
        try:
            # Check if ffmpeg is available
            if not which("ffmpeg"):
                raise RuntimeError(
                    "FFmpeg is required to process MP3, M4A, and other audio formats. "
                    "Please install FFmpeg or convert your audio file to WAV format. "
                    "You can convert online at: https://convertio.co/mp3-wav/ or https://cloudconvert.com/mp3-to-wav"
                )

            # Load audio with pydub
            audio_segment = AudioSegment.from_file(file_path)

            # Convert to WAV format in memory
            audio_segment = audio_segment.set_frame_rate(self.sample_rate)
            audio_segment = audio_segment.set_channels(1)
            audio_segment = audio_segment.set_sample_width(2)  # 16-bit

            # Export to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                audio_segment.export(temp_path, format="wav")

            try:
                # Load the temporary WAV file
                with sr.AudioFile(temp_path) as source:
                    audio = self.recognizer.record(source)
                return audio
            finally:
                # Clean up temporary file
                os.unlink(temp_path)

        except RuntimeError as e:
            # Re-raise our custom error message
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Failed to convert audio file: {e}")
            raise RuntimeError(f"Audio conversion failed: {str(e)}")
    
    def save_audio_to_file(self, audio_data: sr.AudioData, file_path: str, format: str = 'wav'):
        """
        Save AudioData to file
        
        Args:
            audio_data: AudioData object to save
            file_path (str): Output file path
            format (str): Audio format ('wav', 'mp3', 'flac', etc.)
        """
        try:
            if format.lower() == 'wav':
                # Save as WAV directly
                wav_data = audio_data.get_wav_data()
                with open(file_path, 'wb') as f:
                    f.write(wav_data)
            else:
                # Convert using pydub
                wav_data = audio_data.get_wav_data()
                audio_segment = AudioSegment.from_wav(io.BytesIO(wav_data))
                audio_segment.export(file_path, format=format)
            
            logger.info(f"Audio saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise
    
    def get_audio_info(self, audio_data: sr.AudioData) -> dict:
        """
        Get information about audio data
        
        Args:
            audio_data: AudioData object
            
        Returns:
            dict: Audio information
        """
        return {
            'sample_rate': audio_data.sample_rate,
            'sample_width': audio_data.sample_width,
            'duration_seconds': len(audio_data.frame_data) / (audio_data.sample_rate * audio_data.sample_width),
            'frame_count': len(audio_data.frame_data),
            'channels': 1  # AudioData is always mono
        }
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.is_recording:
            self.stop_continuous_recording()
        
        if self.audio:
            self.audio.terminate()
            logger.info("Audio resources cleaned up")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
