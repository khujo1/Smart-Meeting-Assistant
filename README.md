# 🎯 Smart Meeting Assistant

**AI-Powered Meeting Intelligence Platform**

Transform meeting recordings into actionable insights, create searchable knowledge bases, and automate follow-up tasks using 4 integrated OpenAI APIs.

![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Tests: 100% Passing](https://img.shields.io/badge/Tests-16%2F16%20Passing-brightgreen)
![Coverage: 100%](https://img.shields.io/badge/Coverage-100%25-brightgreen)

---

## 🌟 Features Overview

### Core AI Features (All 4 OpenAI APIs)
- 🎵 **Audio Transcription** (Whisper API): Convert MP3, WAV, M4A files up to 25MB into accurate text
- 🧠 **Smart Analysis** (GPT-4 + Function Calling): Extract summaries, action items, key decisions, and topics
- 🔍 **Semantic Search** (Embeddings API): Find information across meetings using natural language queries
- 🎨 **Visual Summaries** (DALL-E 3): Generate professional visual representations of meeting content

### Advanced Features
- 🎤 **Real-time Transcription**: Live meeting processing with WebSocket support (optional)
- 🔗 **Calendar/Task Integration**: Automatically create calendar events and task assignments
- 📊 **Cross-Meeting Analytics**: Discover patterns, trends, and insights across all meetings
- 🔄 **Visual Regeneration**: Re-create visuals with different styles or focus areas
- 📱 **Responsive Web Interface**: Works seamlessly on desktop, tablet, and mobile

### Business Impact
- **Preserve organizational knowledge** with searchable meeting database
- **Automate follow-up tasks** with integrated calendar and task management
- **Improve meeting effectiveness** through AI-powered insights and action tracking
- **Save time** with automated transcription and summary generation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- OpenAI API key with access to GPT-4, Whisper, Embeddings, and DALL-E 3
- 10+ GB free disk space (for virtual environment and data)

### Option 1: Automated Setup (Recommended)
```bash
# 1. Clone repository
git clone <your-repo-url>
cd Smart-Meeting-Assistant

# 2. Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-key-here

# 3. Run automated setup (creates venv, installs dependencies, starts app)
chmod +x start.sh
./start.sh
```

### Option 2: Manual Setup
```bash
# 1. Clone and navigate
git clone <your-repo-url>
cd Smart-Meeting-Assistant

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# 5. Run application
python app.py
```

### 🌐 Access the Application
- Open your browser and go to `http://localhost:5000`
- If port 5000 is in use, the app will automatically use port 5001

---

## 🔧 Environment Configuration

### Required Environment Variables
Create a `.env` file with the following variables:

```env
# Required: Your OpenAI API key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Custom Flask secret key (generated automatically if not provided)
FLASK_SECRET_KEY=your-custom-secret-key-here
```

### OpenAI API Setup
1. **Get API Key**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Required Access**: Ensure you have access to:
   - GPT-4 (for analysis and function calling)
   - Whisper (for audio transcription)
   - text-embedding-3-small (for semantic search)
   - DALL-E 3 (for visual generation)
3. **Billing**: Add sufficient credits (estimate: $5-15 for comprehensive testing)

### Supported Audio Formats
- **MP3**: Most common format, recommended
- **WAV**: High quality, larger file sizes
- **M4A**: Apple format, good compression
- **File Size Limit**: 25MB maximum per file
- **Duration**: No specific limit, but longer files cost more to process

---

## 🎯 How to Use

### 1. Upload and Process Meetings

#### Basic Upload
1. **Access Interface**: Open the web application in your browser
2. **Upload File**: 
   - Drag and drop audio file onto the upload area, OR
   - Click "Choose File" button to select from your computer
3. **Automatic Processing**: The system will automatically:
   - Transcribe audio using Whisper API
   - Analyze content with GPT-4
   - Generate embeddings for search
   - Create a visual summary with DALL-E 3
4. **View Results**: Review the generated summary, action items, and visual

#### Upload Area Features
- **Multiple file support**: Upload several files in sequence
- **Progress indicators**: Real-time processing status
- **Error handling**: Clear feedback if upload fails
- **Format validation**: Automatic checking of supported formats

### 2. Browse and Search Meetings

#### Meeting History
- **View All Meetings**: Browse chronologically sorted meeting list
- **Meeting Details**: Click any meeting to view full analysis
- **Quick Preview**: See summary and key points without opening full details

#### Semantic Search
- **Natural Language**: Search using everyday language (e.g., "meetings about budget planning")
- **Cross-Meeting**: Find information across all processed meetings
- **Relevance Scoring**: Results ranked by semantic similarity
- **Instant Results**: Fast search powered by embedding vectors

#### Search Examples
```
"action items assigned to John"
"budget discussions from last month"
"decisions about the new product launch"
"meetings where we talked about hiring"
```

### 3. Advanced Features

#### Calendar Integration
1. **Select Meeting**: Choose any processed meeting
2. **Create Events**: Click "Create Calendar Events" 
3. **Automatic Generation**: System creates calendar events based on:
   - Action items with deadlines
   - Follow-up meetings mentioned
   - Scheduled deliverables

#### Task Management
1. **Task Assignment**: Click "Create Task Assignments"
2. **Smart Extraction**: Automatically identifies:
   - Who is responsible for what
   - Deadlines and priorities
   - Task dependencies
3. **Export Options**: Tasks formatted for popular project management tools

#### Cross-Meeting Analytics
1. **Pattern Discovery**: Click "Get Insights" to analyze patterns across meetings
2. **Trend Analysis**: Identify recurring topics and themes
3. **Recommendations**: AI-powered suggestions for improving meeting effectiveness
4. **Team Insights**: Understand collaboration patterns and communication trends

#### Visual Regeneration
1. **New Perspectives**: Regenerate visuals with different focus areas
2. **Style Options**: Request different visual styles or emphasis
3. **Manual Trigger**: Use "Regenerate Visual" button on any meeting
4. **Automatic Updates**: Visuals can be updated when content changes

### 4. Real-time Features (Optional)

#### Live Transcription
- **WebSocket Support**: Real-time transcription during meetings
- **Live Analysis**: Immediate insights as the meeting progresses
- **Session Management**: Automatic saving of live sessions
- **Note**: Requires additional WebSocket setup (currently disabled by default)

---

## 🧪 Testing and Quality Assurance

### Run Test Suite
```bash
# Run comprehensive test suite (16 tests)
python run_tests.py

# Expected output: 100% success rate
# Tests run: 16
# Failures: 0
# Errors: 0
# Success rate: 100.0%
```

### Test Coverage
- ✅ **Unit Tests**: All service classes (Audio, Analysis, Search, Visual, Integration)
- ✅ **Integration Tests**: API endpoints and data flow
- ✅ **Error Handling**: Edge cases and failure scenarios
- ✅ **Mocked APIs**: No external API calls during testing
- ✅ **Performance Tests**: Processing time and memory usage

### Continuous Integration
The project includes a comprehensive test suite that validates:
- OpenAI API integration (mocked)
- File upload and processing
- Search functionality
- Data persistence
- Error handling and recovery

---

## 📁 Project Architecture

### Directory Structure
```
Smart-Meeting-Assistant/
├── 📄 app.py                    # Main Flask application (613 lines)
├── 📄 requirements.txt          # Python dependencies
├── 📄 start.sh                 # Automated setup script
├── 📄 run_tests.py             # Test runner with detailed output
├── 📂 services/                # AI service modules (modular architecture)
│   ├── 📄 __init__.py
│   ├── 📄 audio_service.py     # Whisper API integration (73 lines)
│   ├── 📄 analysis_service.py  # GPT-4 analysis + function calling (198 lines)
│   ├── 📄 search_service.py    # Embeddings & semantic search (296 lines)
│   ├── 📄 visual_service.py    # DALL-E 3 visual generation (171 lines)
│   ├── 📄 integration_service.py # Calendar/task integration (145 lines)
│   └── 📄 realtime_service.py  # WebSocket real-time processing (128 lines)
├── 📂 templates/
│   └── 📄 index.html           # Modern responsive UI (156 lines)
├── 📂 static/
│   ├── 📂 css/
│   │   └── 📄 style.css        # Professional styling (200+ lines)
│   ├── 📂 js/
│   │   └── 📄 app.js          # Interactive frontend logic (400+ lines)
│   └── 📂 images/             # Generated visual summaries
│       └── 📄 .gitkeep        # Preserve directory structure
├── 📂 data/
│   └── 📄 meetings.json       # Persistent meeting storage (JSON format)
├── 📂 tests/
│   └── 📄 test_comprehensive.py # Complete test suite (306 lines)
├── 📂 uploads/                # Temporary audio file storage
│   └── 📄 .gitkeep           # Preserve directory structure
├── 📂 venv/                   # Virtual environment (auto-created)
├── 📄 .env                    # Environment variables (not in git)
├── 📄 .env.example           # Environment template
├── 📄 .gitignore             # Comprehensive git ignore rules
├── 📄 README.md              # This comprehensive documentation
└── 📄 TECHNICAL_DOCS.md      # Detailed technical documentation
```

### Service Architecture

#### 🎵 AudioService (`audio_service.py`)
- **Purpose**: Audio file transcription using OpenAI Whisper
- **Features**: 
  - Support for multiple audio formats
  - Batch processing capabilities
  - Detailed timestamp extraction
  - Error handling and retry logic
- **API Used**: OpenAI Whisper (`whisper-1` model)

#### 🧠 AnalysisService (`analysis_service.py`)
- **Purpose**: Intelligent content analysis using GPT-4
- **Features**:
  - Function calling for structured data extraction
  - Fallback analysis for error resilience
  - Custom analysis prompts
  - Action item extraction with owners and deadlines
- **API Used**: OpenAI Chat Completions with GPT-4

#### 🔍 SearchService (`search_service.py`)
- **Purpose**: Semantic search and embedding management
- **Features**:
  - Vector embedding generation
  - Cosine similarity search
  - Cross-meeting analytics
  - Similar meeting discovery
  - Meeting insights and recommendations
- **API Used**: OpenAI Embeddings (`text-embedding-3-small`)

#### 🎨 VisualService (`visual_service.py`)
- **Purpose**: Visual summary generation using DALL-E 3
- **Features**:
  - Professional presentation visuals
  - Multiple visual styles
  - Regeneration capabilities
  - Error handling and fallbacks
- **API Used**: OpenAI Images (DALL-E 3)

#### 🔗 IntegrationService (`integration_service.py`)
- **Purpose**: Calendar and task management integration
- **Features**:
  - Calendar event generation
  - Task assignment creation
  - Deadline management
  - Export to various formats

#### 🎤 RealtimeService (`realtime_service.py`)
- **Purpose**: Real-time meeting processing (optional)
- **Features**:
  - WebSocket support
  - Live transcription
  - Real-time analysis
  - Session management

### Data Flow
1. **Upload** → File validation and storage
2. **Transcription** → Whisper API processing
3. **Analysis** → GPT-4 content analysis
4. **Embedding** → Vector generation for search
5. **Visual** → DALL-E 3 summary creation
6. **Storage** → JSON persistence with full metadata

---

## 🌐 API Endpoints

### Core Endpoints
- `GET /` - Main application interface
- `POST /upload` - Upload audio files (supports multipart/form-data)
- `GET /meetings` - List all processed meetings (JSON response)
- `GET /meetings/<id>` - Get specific meeting details
- `GET /search?q=<query>` - Semantic search across meetings

### Advanced Endpoints
- `POST /meetings/<id>/regenerate-visual` - Regenerate visual summary
- `GET /api/insights` - Cross-meeting analytics and insights
- `POST /api/calendar-events` - Create calendar events from meeting
- `POST /api/task-assignments` - Create task assignments from meeting
- `GET /api/similar/<meeting_id>` - Find similar meetings

### Real-time Endpoints (Optional)
- `WebSocket /ws/transcribe` - Live transcription stream
- `POST /api/realtime/start` - Start real-time session
- `POST /api/realtime/stop` - Stop real-time session

### Response Formats
All API endpoints return JSON responses with consistent structure:
```json
{
  "success": true/false,
  "data": {...},
  "error": "error message if applicable",
  "timestamp": "ISO 8601 timestamp"
}
```

---

## 🔍 Usage Examples

### Example 1: Basic Meeting Upload
```bash
# Upload a meeting recording
curl -X POST http://localhost:5000/upload \
  -F "file=@meeting_recording.mp3"

# Response:
{
  "success": true,
  "meeting_id": "meeting-20250630-123456",
  "message": "Meeting processed successfully"
}
```

### Example 2: Search Meetings
```bash
# Search for budget-related discussions
curl "http://localhost:5000/search?q=budget%20planning"

# Response:
{
  "success": true,
  "results": [
    {
      "meeting_id": "meeting-20250630-123456",
      "filename": "budget_meeting.mp3",
      "relevance": 0.89,
      "snippet": "Discussed Q3 budget allocation..."
    }
  ]
}
```

### Example 3: Get Meeting Insights
```bash
# Get cross-meeting analytics
curl http://localhost:5000/api/insights

# Response:
{
  "success": true,
  "insights": {
    "total_meetings": 15,
    "common_topics": ["budget", "planning", "team"],
    "recommendations": [
      "Consider shorter meetings for status updates",
      "Action items follow-up rate could be improved"
    ]
  }
}
```

---

## ⚡ Performance and Optimization

### Processing Times (Approximate)
- **Transcription**: ~1 minute per 10 minutes of audio
- **Analysis**: ~30 seconds per meeting
- **Embedding Generation**: ~5 seconds per meeting
- **Visual Creation**: ~30-60 seconds per visual
- **Search**: <1 second for any query

### Resource Usage
- **Memory**: ~200MB base + ~50MB per concurrent processing task
- **Storage**: ~1-5MB per meeting (varies by transcript length)
- **Network**: Depends on OpenAI API calls, ~1-10MB per meeting

### Optimization Features
- **Lazy Loading**: Visuals and embeddings loaded on demand
- **Caching**: Intelligent caching of API responses
- **Batch Processing**: Efficient handling of multiple uploads
- **Error Recovery**: Automatic retry with exponential backoff

---

## 🛠 Troubleshooting

### Common Issues and Solutions

#### 1. Upload Issues
**Problem**: File upload fails or times out
**Solutions**:
- Check file size (must be under 25MB)
- Verify audio format (MP3, WAV, M4A)
- Ensure stable internet connection
- Check browser developer console for errors

#### 2. Processing Errors
**Problem**: Meeting processing fails during analysis
**Solutions**:
- Verify OpenAI API key in `.env` file
- Check OpenAI account credits and limits
- Ensure audio file is not corrupted
- Try with a shorter audio file first

#### 3. Search Not Working
**Problem**: Search returns no results or errors
**Solutions**:
- Restart the application to trigger embedding migration
- Check that meetings have been fully processed
- Try simpler search terms
- Verify embeddings are generated (check console logs)

#### 4. Visual Generation Fails
**Problem**: DALL-E visuals not generating
**Solutions**:
- Verify DALL-E 3 access in OpenAI account
- Check API usage limits
- Use "Regenerate Visual" button
- Check console logs for specific error messages

#### 5. Real-time Features Not Available
**Problem**: WebSocket features disabled
**Solutions**:
- This is expected (WebSocket support is optional)
- Features are disabled by default for stability
- Can be enabled by installing additional dependencies

### Debug Mode
Enable debug mode for detailed logging:
```bash
# Set environment variable
export FLASK_DEBUG=1

# Or add to .env file
FLASK_DEBUG=1
```

### Log Analysis
Check console output for detailed information:
- **INFO**: Normal operation status
- **WARNING**: Non-critical issues
- **ERROR**: Problems that need attention

---

## 🔐 Security and Privacy

### Data Handling
- **Local Storage**: All meeting data stored locally in JSON format
- **Temporary Files**: Audio files deleted after processing
- **No Persistent Audio**: Original recordings not permanently stored
- **API Security**: OpenAI API calls use secure HTTPS

### Privacy Considerations
- **Data Ownership**: All processed data remains under your control
- **No Telemetry**: No usage data sent to external services
- **Local Processing**: Only API calls to OpenAI for processing
- **Configurable**: Can be modified to use local models if needed

### Recommended Security Practices
1. **Secure API Keys**: Never commit `.env` file to version control
2. **Access Control**: Run on secure networks only
3. **Regular Updates**: Keep dependencies updated
4. **Backup Strategy**: Regular backups of `data/meetings.json`

---

## 🚀 Deployment Options

### Local Development
- Perfect for testing and personal use
- Uses built-in Flask development server
- Automatic reloading on code changes

### Production Deployment
For production use, consider:

```bash
# Using Gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using uWSGI
pip install uwsgi
uwsgi --http :5000 --module app:app
```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```


## 📈 Future Enhancements

### Planned Features
- **Multi-language Support**: Support for languages beyond English
- **Video Processing**: Support for video files with audio extraction
- **Team Collaboration**: Multi-user access and sharing
- **Custom Models**: Support for fine-tuned or local models
- **Advanced Analytics**: More sophisticated meeting analytics
- **Integration APIs**: Connect with popular productivity tools

### Potential Integrations
- **Slack/Teams**: Direct integration with chat platforms
- **Calendar Apps**: Two-way sync with Google Calendar, Outlook
- **Project Management**: Jira, Asana, Trello integration
- **CRM Systems**: Salesforce, HubSpot integration
- **Storage**: Google Drive, Dropbox, OneDrive sync

---