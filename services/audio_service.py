import os
import json
import logging
from openai import OpenAI
from typing import Dict, List, Optional, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe audio file using Whisper API
        
        Args:
            audio_file_path (str): Path to audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            with open(audio_file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            logger.info(f"Successfully transcribed audio file: {audio_file_path}")
            return transcript
        
        except Exception as e:
            logger.error(f"Audio transcription failed for {audio_file_path}: {str(e)}")
            raise Exception(f"Audio transcription failed: {str(e)}")
    
    def transcribe_with_timestamps(self, audio_file_path: str) -> Dict:
        """
        Transcribe audio with detailed timestamp information
        
        Args:
            audio_file_path (str): Path to audio file
            
        Returns:
            dict: Detailed transcription with timestamps
        """
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            with open(audio_file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            
            logger.info(f"Successfully transcribed audio with timestamps: {audio_file_path}")
            return transcript.model_dump() if hasattr(transcript, 'model_dump') else dict(transcript)
        
        except Exception as e:
            logger.error(f"Detailed audio transcription failed for {audio_file_path}: {str(e)}")
            raise Exception(f"Detailed audio transcription failed: {str(e)}")
