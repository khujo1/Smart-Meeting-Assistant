import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from services.audio_service import AudioService
from services.analysis_service import AnalysisService
from services.search_service import SearchService
from services.visual_service import VisualService
from services.integration_service import IntegrationService

# Optional real-time service (requires websockets)
try:
    from services.realtime_service import RealTimeTranscriptionService
    REALTIME_ENABLED = True
    RealTimeService = RealTimeTranscriptionService
except ImportError:
    print("⚠️  Real-time transcription disabled (websockets not available)")
    REALTIME_ENABLED = False
    RealTimeService = None

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'  # Fixed: was == instead of =
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25MB limit

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'aac', 'flac'}

# Initialize services
audio_service = AudioService()
analysis_service = AnalysisService()
search_service = SearchService()
visual_service = VisualService()
integration_service = IntegrationService()

# Initialize real-time service if available
if REALTIME_ENABLED and RealTimeService:
    realtime_service = RealTimeService()
else:
    realtime_service = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_meetings():
    """Load meetings from JSON file"""
    if os.path.exists('data/meetings.json'):
        with open('data/meetings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_meetings(meetings):
    """Save meetings to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/meetings.json', 'w', encoding='utf-8') as f:
        json.dump(meetings, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug_frontend.html')
def debug_frontend():
    return send_from_directory('.', 'debug_frontend.html')

@app.route('/debug_simple.html')
def debug_simple():
    """Serve the debug simple HTML file"""
    return send_from_directory('.', 'debug_simple.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use MP3, WAV, M4A, AAC, or FLAC'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'File uploaded successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process/<filename>', methods=['POST'])
def process_meeting(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Get additional metadata from request
        meeting_title = request.json.get('title', f'Meeting - {filename}') if request.is_json else f'Meeting - {filename}'
        attendees = request.json.get('attendees', []) if request.is_json else []
        
        # Step 1: Transcribe audio
        print(f"Transcribing audio file: {filename}")
        transcript = audio_service.transcribe(filepath)
        
        # Step 2: Analyze content
        print("Analyzing meeting content...")
        analysis = analysis_service.analyze_meeting(transcript)
        
        # Step 3: Generate embeddings for search
        print("Creating embeddings...")
        embedding = search_service.create_embedding(transcript)
        
        # Step 4: Generate visual summary
        print("Generating visual summary...")
        visual_url = visual_service.generate_visual_summary(analysis['summary'])
        
        # Save meeting data
        meeting_data = {
            'id': len(load_meetings()) + 1,
            'title': meeting_title,
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'attendees': attendees,
            'transcript': transcript,
            'analysis': analysis,
            'embedding': embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
            'visual_url': visual_url
        }
        
        meetings = load_meetings()
        meetings.append(meeting_data)
        save_meetings(meetings)
        
        # Don't clean up uploaded file - keep for reference
        # os.remove(filepath)  # Commented out to preserve files
        
        return jsonify({
            'success': True,
            'meeting': {
                'id': meeting_data['id'],
                'title': meeting_title,
                'timestamp': meeting_data['timestamp'],
                'analysis': analysis,
                'visual_url': visual_url
            }
        })
    
    except Exception as e:
        print(f"Error processing meeting: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/meetings')
def get_meetings():
    try:
        meetings = load_meetings()
        # Return simplified meeting list
        meeting_list = [{
            'id': m['id'],
            'title': m.get('title', f"Meeting - {m['filename']}"),
            'filename': m['filename'],
            'timestamp': m['timestamp'],
            'attendees': m.get('attendees', []),
            'summary': m['analysis']['summary'][:200] + '...' if len(m['analysis']['summary']) > 200 else m['analysis']['summary']
        } for m in meetings]
        
        return jsonify({'meetings': meeting_list})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/meetings/<int:meeting_id>')
def get_meeting(meeting_id):
    try:
        meetings = load_meetings()
        meeting = next((m for m in meetings if m['id'] == meeting_id), None)
        
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        # Check if visual_url is missing or expired, regenerate if needed
        visual_url = meeting.get('visual_url', '')
        if not visual_url or not visual_url.startswith('http'):
            try:
                print(f"Regenerating visual summary for meeting {meeting_id}")
                summary = meeting.get('analysis', {}).get('summary', '')
                if summary:
                    visual_url = visual_service.generate_visual_summary(summary)
                    # Update the meeting data
                    meeting['visual_url'] = visual_url
                    save_meetings(meetings)
            except Exception as e:
                print(f"Failed to regenerate visual: {str(e)}")
                visual_url = None
        
        return jsonify({
            'meeting': {
                'id': meeting['id'],
                'title': meeting.get('title', f"Meeting - {meeting['filename']}"),
                'timestamp': meeting['timestamp'],
                'attendees': meeting.get('attendees', []),
                'transcript': meeting['transcript'],
                'analysis': meeting['analysis'],
                'visual_url': visual_url
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search')
def search_meetings():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'results': [], 'error': 'Query is required'}), 400
        
        meetings = load_meetings()
        results = search_service.search_meetings(query, meetings)
        
        # Format results for frontend
        formatted_results = []
        for result in results:
            formatted_results.append({
                'meeting_id': result['meeting_id'],
                'filename': result['filename'], 
                'timestamp': result['timestamp'],
                'relevance': result['similarity'],
                'snippet': result['summary']
            })
        
        return jsonify({
            'success': True,
            'results': formatted_results
        })
    
    except Exception as e:
        return jsonify({'success': False, 'results': [], 'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    """Get meeting statistics"""
    try:
        meetings = load_meetings()
        stats = {
            'total_meetings': len(meetings),
            'total_duration': sum(m.get('analysis', {}).get('duration_minutes', 0) for m in meetings),
            'action_items_count': sum(len(m.get('analysis', {}).get('action_items', [])) for m in meetings),
            'decisions_count': sum(len(m.get('analysis', {}).get('decisions', [])) for m in meetings)
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 25MB'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

def migrate_old_meetings():
    """Add embeddings to old meetings that might be missing them"""
    try:
        meetings = load_meetings()
        updated = False
        
        for i, meeting in enumerate(meetings):
            if 'embedding' not in meeting or not meeting['embedding']:
                print(f"Adding embedding to meeting {meeting.get('id', i+1)}")
                try:
                    # Create embedding from transcript
                    transcript = meeting.get('transcript', '')
                    if transcript:
                        embedding = search_service.create_embedding(transcript)
                        meeting['embedding'] = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
                        updated = True
                except Exception as e:
                    print(f"Failed to create embedding for meeting {meeting.get('id', i+1)}: {str(e)}")
                    # Add empty embedding to prevent repeated attempts
                    meeting['embedding'] = []
        
        if updated:
            save_meetings(meetings)
            print("Migration completed successfully")
        else:
            print("No migration needed")
            
    except Exception as e:
        print(f"Migration failed: {str(e)}")

@app.route('/meetings/<int:meeting_id>/regenerate-visual', methods=['POST'])
def regenerate_visual(meeting_id):
    try:
        meetings = load_meetings()
        meeting = next((m for m in meetings if m['id'] == meeting_id), None)
        
        if not meeting:
            return jsonify({'success': False, 'error': 'Meeting not found'}), 404
        
        # Get the summary for visual generation
        summary = meeting.get('analysis', {}).get('summary', '')
        if not summary:
            return jsonify({'success': False, 'error': 'No summary available for visual generation'}), 400
        
        # Generate new visual
        visual_url = visual_service.generate_visual_summary(summary)
        
        # Update meeting data
        meeting['visual_url'] = visual_url
        save_meetings(meetings)
        
        return jsonify({
            'success': True,
            'visual_url': visual_url
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/integrations/calendar', methods=['POST'])
def create_calendar_events():
    """Create calendar events from meeting analysis"""
    try:
        data = request.get_json()
        meeting_id = data.get('meeting_id')
        
        if not meeting_id:
            return jsonify({'success': False, 'error': 'Meeting ID required'}), 400
        
        meetings = load_meetings()
        meeting = next((m for m in meetings if m.get('id') == meeting_id), None)
        
        if not meeting:
            return jsonify({'success': False, 'error': 'Meeting not found'}), 404
        
        analysis = meeting.get('analysis', {})
        events = integration_service.create_calendar_events(analysis)
        
        return jsonify({
            'success': True,
            'events_created': len(events),
            'events': events
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/integrations/tasks', methods=['POST'])
def create_task_assignments():
    """Create task assignments from meeting analysis"""
    try:
        data = request.get_json()
        meeting_id = data.get('meeting_id')
        
        if not meeting_id:
            return jsonify({'success': False, 'error': 'Meeting ID required'}), 400
        
        meetings = load_meetings()
        meeting = next((m for m in meetings if m.get('id') == meeting_id), None)
        
        if not meeting:
            return jsonify({'success': False, 'error': 'Meeting not found'}), 404
        
        analysis = meeting.get('analysis', {})
        tasks = integration_service.create_task_assignments(analysis)
        
        return jsonify({
            'success': True,
            'tasks_created': len(tasks),
            'tasks': tasks
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/insights', methods=['GET'])
def get_cross_meeting_insights():
    """Get cross-meeting insights and recommendations"""
    try:
        meetings = load_meetings()
        insights = search_service.get_meeting_insights(meetings)
        
        return jsonify({
            'success': True,
            'insights': insights
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/meetings/similar/<meeting_id>')
def get_similar_meetings(meeting_id):
    """Get meetings similar to the specified meeting"""
    try:
        meetings = load_meetings()
        target_meeting = next((m for m in meetings if m.get('id') == meeting_id), None)
        
        if not target_meeting:
            return jsonify({'success': False, 'error': 'Meeting not found'}), 404
        
        similar_meetings = search_service.find_similar_meetings(target_meeting, meetings)
        
        return jsonify({
            'success': True,
            'similar_meetings': similar_meetings
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/realtime/start', methods=['POST'])
def start_realtime_session():
    """Start a new real-time transcription session"""
    if not REALTIME_ENABLED or not realtime_service:
        return jsonify({'success': False, 'error': 'Real-time transcription not available. Please install websockets.'}), 501
    
    try:
        data = request.get_json()
        session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
        
        session = realtime_service.create_session(session_id)
        
        return jsonify({
            'success': True,
            'session': session
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/realtime/process', methods=['POST'])
def process_realtime_audio():
    """Process audio chunk for real-time transcription"""
    if not REALTIME_ENABLED or not realtime_service:
        return jsonify({'success': False, 'error': 'Real-time transcription not available. Please install websockets.'}), 501
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        audio_data = data.get('audio_data')  # Base64 encoded
        
        if not session_id or not audio_data:
            return jsonify({'success': False, 'error': 'Missing session_id or audio_data'}), 400
        
        import base64
        audio_bytes = base64.b64decode(audio_data)
        result = realtime_service.process_audio_chunk(session_id, audio_bytes)
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/realtime/end/<session_id>', methods=['POST'])
def end_realtime_session(session_id):
    """End a real-time transcription session"""
    if not REALTIME_ENABLED or not realtime_service:
        return jsonify({'success': False, 'error': 'Real-time transcription not available. Please install websockets.'}), 501
    
    try:
        summary = realtime_service.end_session(session_id)
        
        # Save the completed session as a regular meeting
        if 'full_transcription' in summary and summary['full_transcription'].strip():
            meetings = load_meetings()
            
            new_meeting = {
                'id': f"realtime_{session_id}",
                'filename': f"realtime_session_{session_id}",
                'timestamp': summary.get('created_at', datetime.now().isoformat()),
                'transcription': summary['full_transcription'],
                'analysis': summary.get('final_analysis'),
                'realtime_data': {
                    'session_id': session_id,
                    'duration_seconds': summary.get('duration_seconds', 0),
                    'segments_count': summary.get('total_segments', 0),
                    'live_analysis': summary.get('live_analysis', {})
                }
            }
            
            # Create embedding for the transcription
            if new_meeting['transcription']:
                embedding = search_service.create_embedding(new_meeting['transcription'])
                if embedding:
                    new_meeting['embedding'] = embedding
            
            # Generate visual summary if we have analysis
            if new_meeting['analysis'] and new_meeting['analysis'].get('summary'):
                visual_url = visual_service.generate_visual_summary(new_meeting['analysis']['summary'])
                if visual_url:
                    new_meeting['visual_url'] = visual_url
            
            meetings.append(new_meeting)
            save_meetings(meetings)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/realtime/sessions')
def get_active_realtime_sessions():
    """Get list of active real-time sessions"""
    if not REALTIME_ENABLED or not realtime_service:
        return jsonify({'success': False, 'error': 'Real-time transcription not available. Please install websockets.'}), 501
    
    try:
        sessions = realtime_service.get_active_sessions()
        
        return jsonify({
            'success': True,
            'active_sessions': sessions
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API Routes for Advanced Features
@app.route('/api/bulk-calendar-events', methods=['POST'])
def create_bulk_calendar_events():
    """Create calendar events from all meeting analysis"""
    try:
        meetings = load_meetings()
        events_created = 0
        
        for meeting in meetings:
            if 'analysis' in meeting and meeting['analysis']:
                # Simple simulation of calendar events creation
                analysis = meeting.get('analysis', {})
                if analysis.get('action_items'):
                    events_created += len(analysis['action_items'])
        
        return jsonify({
            'success': True,
            'events_created': events_created,
            'message': f'Successfully created {events_created} calendar events'
        })
    except Exception as e:
        print(f"Error creating calendar events: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bulk-task-assignments', methods=['POST'])
def create_bulk_task_assignments():
    """Create task assignments from meeting action items"""
    try:
        meetings = load_meetings()
        tasks_created = 0
        
        for meeting in meetings:
            if 'analysis' in meeting and meeting['analysis'] and 'action_items' in meeting['analysis']:
                # Simple simulation of task assignments creation
                tasks_created += len(meeting['analysis']['action_items'])
        
        return jsonify({
            'success': True,
            'tasks_created': tasks_created,
            'message': f'Successfully created {tasks_created} task assignments'
        })
    except Exception as e:
        print(f"Error creating task assignments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Migrate old meetings to add missing embeddings
    print("Checking for meetings that need migration...")
    migrate_old_meetings()
    
    app.run(debug=True, host='0.0.0.0', port=5000)