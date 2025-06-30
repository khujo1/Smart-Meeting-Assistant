import asyncio
import websockets
import json
import logging
from datetime import datetime
import base64
import io
import wave
from typing import Dict, Any, List
import threading
import queue

from services.audio_service import AudioService
from services.analysis_service import AnalysisService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeTranscriptionService:
    """
    Advanced feature: Real-time meeting transcription and analysis
    Processes audio chunks as they come in and provides live updates
    """
    
    def __init__(self):
        self.audio_service = AudioService()
        self.analysis_service = AnalysisService()
        self.active_sessions = {}  # session_id -> session_data
        self.chunk_size = 1024 * 16  # 16KB chunks
        self.sample_rate = 16000
        
    def create_session(self, session_id: str) -> Dict[str, Any]:
        """Create a new real-time transcription session"""
        session = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'audio_chunks': [],
            'transcription_segments': [],
            'partial_transcriptions': [],
            'live_analysis': {
                'word_count': 0,
                'speakers_detected': 0,
                'current_topic': 'Unknown',
                'sentiment': 'neutral',
                'action_items_detected': 0
            },
            'audio_buffer': io.BytesIO(),
            'is_active': True
        }
        
        self.active_sessions[session_id] = session
        logger.info(f"Created real-time session: {session_id}")
        return session
    
    def process_audio_chunk(self, session_id: str, audio_data: bytes) -> Dict[str, Any]:
        """
        Process incoming audio chunk and return partial results
        
        Args:
            session_id: Session identifier
            audio_data: Raw audio data chunk
            
        Returns:
            Dict with partial transcription and analysis
        """
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            
            # Add chunk to buffer
            session['audio_buffer'].write(audio_data)
            session['audio_chunks'].append({
                'timestamp': datetime.now().isoformat(),
                'size': len(audio_data)
            })
            
            # Process if we have enough data (every 3 seconds worth)
            buffer_size = session['audio_buffer'].tell()
            if buffer_size >= self.sample_rate * 2 * 3:  # 3 seconds of 16-bit audio
                return self._process_buffer(session_id)
            
            return {
                'session_id': session_id,
                'status': 'buffering',
                'buffer_size': buffer_size,
                'chunks_received': len(session['audio_chunks'])
            }
            
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
            return {'error': str(e)}
    
    def _process_buffer(self, session_id: str) -> Dict[str, Any]:
        """Process accumulated audio buffer"""
        try:
            session = self.active_sessions[session_id]
            
            # Get audio data from buffer
            session['audio_buffer'].seek(0)
            audio_data = session['audio_buffer'].read()
            
            # Create temporary WAV file for transcription
            temp_wav = io.BytesIO()
            with wave.open(temp_wav, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data)
            
            temp_wav.seek(0)
            
            # Transcribe the chunk
            transcription = self._transcribe_chunk(temp_wav)
            
            if transcription:
                segment = {
                    'timestamp': datetime.now().isoformat(),
                    'text': transcription,
                    'duration': len(audio_data) / (self.sample_rate * 2)  # Duration in seconds
                }
                
                session['transcription_segments'].append(segment)
                
                # Update live analysis
                self._update_live_analysis(session, transcription)
                
                # Clear buffer for next chunk
                session['audio_buffer'] = io.BytesIO()
                
                return {
                    'session_id': session_id,
                    'status': 'transcribed',
                    'segment': segment,
                    'live_analysis': session['live_analysis'],
                    'total_segments': len(session['transcription_segments'])
                }
            
            return {
                'session_id': session_id,
                'status': 'no_transcription',
                'buffer_cleared': True
            }
            
        except Exception as e:
            logger.error(f"Error processing buffer: {str(e)}")
            return {'error': str(e)}
    
    def _transcribe_chunk(self, audio_stream: io.BytesIO) -> str:
        """Transcribe audio chunk using Whisper API"""
        try:
            # Use the existing audio service with some modifications for streaming
            # Note: This is a simplified version - in production you'd want to use
            # streaming-specific optimizations
            
            # Save to temporary file (Whisper API requires file input)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_stream.read())
                temp_path = temp_file.name
            
            try:
                transcription = self.audio_service.transcribe_audio(temp_path)
                return transcription if transcription else ""
            finally:
                import os
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Error transcribing chunk: {str(e)}")
            return ""
    
    def _update_live_analysis(self, session: Dict, new_text: str):
        """Update live analysis with new transcription"""
        try:
            analysis = session['live_analysis']
            
            # Update word count
            words = new_text.split()
            analysis['word_count'] += len(words)
            
            # Simple keyword detection for topics
            keywords = {
                'planning': ['plan', 'schedule', 'timeline', 'roadmap'],
                'technical': ['code', 'bug', 'feature', 'development', 'api'],
                'business': ['revenue', 'customer', 'market', 'sales'],
                'meeting': ['agenda', 'action', 'decision', 'review']
            }
            
            text_lower = new_text.lower()
            for topic, words_list in keywords.items():
                if any(word in text_lower for word in words_list):
                    analysis['current_topic'] = topic
                    break
            
            # Simple action item detection
            action_indicators = ['todo', 'action', 'assign', 'responsible', 'deadline', 'due']
            if any(indicator in text_lower for indicator in action_indicators):
                analysis['action_items_detected'] += 1
            
            # Simple sentiment analysis (basic keyword-based)
            positive_words = ['good', 'great', 'excellent', 'success', 'positive']
            negative_words = ['issue', 'problem', 'concern', 'difficult', 'challenge']
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                analysis['sentiment'] = 'positive'
            elif negative_count > positive_count:
                analysis['sentiment'] = 'negative'
            else:
                analysis['sentiment'] = 'neutral'
                
        except Exception as e:
            logger.error(f"Error updating live analysis: {str(e)}")
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get complete session summary"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            
            # Combine all transcription segments
            full_transcription = " ".join([
                segment['text'] for segment in session['transcription_segments']
            ])
            
            # Generate final analysis using the regular analysis service
            final_analysis = None
            if full_transcription.strip():
                final_analysis = self.analysis_service.analyze_meeting(full_transcription)
            
            return {
                'session_id': session_id,
                'created_at': session['created_at'],
                'ended_at': datetime.now().isoformat(),
                'total_segments': len(session['transcription_segments']),
                'total_chunks': len(session['audio_chunks']),
                'full_transcription': full_transcription,
                'live_analysis': session['live_analysis'],
                'final_analysis': final_analysis,
                'duration_seconds': sum(chunk['size'] for chunk in session['audio_chunks']) / (self.sample_rate * 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting session summary: {str(e)}")
            return {'error': str(e)}
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a real-time session and return final results"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            # Get final summary
            summary = self.get_session_summary(session_id)
            
            # Mark session as inactive
            self.active_sessions[session_id]['is_active'] = False
            
            # Clean up (remove from active sessions after a delay)
            def cleanup():
                import time
                time.sleep(300)  # Keep for 5 minutes for potential retrieval
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                    logger.info(f"Cleaned up session: {session_id}")
            
            threading.Thread(target=cleanup, daemon=True).start()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            return {'error': str(e)}
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return [
            session_id for session_id, session in self.active_sessions.items()
            if session.get('is_active', False)
        ]

# WebSocket handler for real-time communication
class RealTimeWebSocketHandler:
    """WebSocket handler for real-time transcription"""
    
    def __init__(self):
        self.transcription_service = RealTimeTranscriptionService()
        self.clients = {}  # websocket -> session_id
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        try:
            logger.info(f"New WebSocket connection: {websocket.remote_address}")
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self.process_message(websocket, data)
                    
                    if response:
                        await websocket.send(json.dumps(response))
                        
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'error': 'Invalid JSON message'
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        'error': f'Message processing error: {str(e)}'
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed: {websocket.remote_address}")
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
        finally:
            await self.cleanup_client(websocket)
    
    async def process_message(self, websocket, data: Dict) -> Dict:
        """Process incoming WebSocket message"""
        message_type = data.get('type')
        
        if message_type == 'start_session':
            return await self.start_session(websocket, data)
        elif message_type == 'audio_chunk':
            return await self.process_audio(websocket, data)
        elif message_type == 'end_session':
            return await self.end_session(websocket, data)
        elif message_type == 'get_summary':
            return await self.get_summary(websocket, data)
        else:
            return {'error': f'Unknown message type: {message_type}'}
    
    async def start_session(self, websocket, data: Dict) -> Dict:
        """Start a new transcription session"""
        try:
            session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
            session = self.transcription_service.create_session(session_id)
            
            self.clients[websocket] = session_id
            
            return {
                'type': 'session_started',
                'session_id': session_id,
                'created_at': session['created_at']
            }
            
        except Exception as e:
            return {'error': f'Failed to start session: {str(e)}'}
    
    async def process_audio(self, websocket, data: Dict) -> Dict:
        """Process incoming audio chunk"""
        try:
            session_id = self.clients.get(websocket)
            if not session_id:
                return {'error': 'No active session'}
            
            # Decode base64 audio data
            audio_data = base64.b64decode(data.get('audio_data', ''))
            
            result = self.transcription_service.process_audio_chunk(session_id, audio_data)
            result['type'] = 'transcription_update'
            
            return result
            
        except Exception as e:
            return {'error': f'Failed to process audio: {str(e)}'}
    
    async def end_session(self, websocket, data: Dict) -> Dict:
        """End the current session"""
        try:
            session_id = self.clients.get(websocket)
            if not session_id:
                return {'error': 'No active session'}
            
            summary = self.transcription_service.end_session(session_id)
            summary['type'] = 'session_ended'
            
            return summary
            
        except Exception as e:
            return {'error': f'Failed to end session: {str(e)}'}
    
    async def get_summary(self, websocket, data: Dict) -> Dict:
        """Get session summary"""
        try:
            session_id = self.clients.get(websocket) or data.get('session_id')
            if not session_id:
                return {'error': 'No session specified'}
            
            summary = self.transcription_service.get_session_summary(session_id)
            summary['type'] = 'session_summary'
            
            return summary
            
        except Exception as e:
            return {'error': f'Failed to get summary: {str(e)}'}
    
    async def cleanup_client(self, websocket):
        """Clean up client connection"""
        try:
            session_id = self.clients.get(websocket)
            if session_id:
                # End session if still active
                self.transcription_service.end_session(session_id)
                del self.clients[websocket]
                logger.info(f"Cleaned up client session: {session_id}")
                
        except Exception as e:
            logger.error(f"Error cleaning up client: {str(e)}")

def start_websocket_server(host='localhost', port=8765):
    """Start the WebSocket server for real-time transcription"""
    handler = RealTimeWebSocketHandler()
    
    start_server = websockets.serve(handler.handle_client, host, port)
    
    logger.info(f"🎙️ Real-time transcription WebSocket server starting on ws://{host}:{port}")
    
    return start_server

if __name__ == "__main__":
    # Example usage
    import asyncio
    
    server = start_websocket_server()
    
    try:
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
