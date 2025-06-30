import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock, Mock, mock_open
import sys
sys.path.append('..')

from app import app, load_meetings, save_meetings
from services.audio_service import AudioService
from services.analysis_service import AnalysisService
from services.search_service import SearchService
from services.visual_service import VisualService
from services.integration_service import IntegrationService

class TestSmartMeetingAssistant(unittest.TestCase):
    """Comprehensive test suite for Smart Meeting Assistant"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Sample meeting data for testing
        self.sample_meeting = {
            'id': 'test-meeting-1',
            'filename': 'test_meeting.mp3',
            'timestamp': '2024-01-15T10:00:00',
            'transcription': 'This is a test meeting about project planning and task assignments.',
            'analysis': {
                'summary': 'Team discussed project timeline and assigned tasks to team members.',
                'action_items': [
                    {'task': 'Complete design mockups', 'owner': 'John', 'deadline': '2024-01-20'},
                    {'task': 'Set up development environment', 'owner': 'Jane', 'deadline': '2024-01-18'}
                ],
                'topics_discussed': ['project planning', 'task assignment', 'timeline'],
                'key_decisions': ['Use Agile methodology', 'Weekly sprint meetings']
            },
            'embedding': [0.1] * 1536,  # Mock embedding
            'visual_url': '/static/images/test_visual.png'
        }
        
        # Create temporary data directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.original_data_path = 'data/meetings.json'
        self.test_data_path = os.path.join(self.temp_dir, 'meetings.json')
        
    def tearDown(self):
        """Clean up after tests"""
        # Clean up temporary files
        if os.path.exists(self.test_data_path):
            os.remove(self.test_data_path)
        os.rmdir(self.temp_dir)

class TestAudioService(TestSmartMeetingAssistant):
    """Test audio transcription service"""
    
    @patch('services.audio_service.OpenAI')
    def test_transcribe_audio_success(self, mock_openai):
        """Test successful audio transcription"""
        # Mock the OpenAI client and its audio.transcriptions.create method
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = "This is a test transcription"
        
        audio_service = AudioService()
        
        # Mock file existence
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=b"fake audio data")):
                result = audio_service.transcribe("test_audio.mp3")
        
        self.assertEqual(result, "This is a test transcription")
        mock_client.audio.transcriptions.create.assert_called_once()
    
    @patch('services.audio_service.OpenAI')
    def test_transcribe_audio_failure(self, mock_openai):
        """Test audio transcription failure handling"""
        # Mock the OpenAI client and make it raise an exception
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")
        
        audio_service = AudioService()
        
        # Mock file existence
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=b"fake audio data")):
                with self.assertRaises(Exception):
                    audio_service.transcribe("test_audio.mp3")

class TestAnalysisService(TestSmartMeetingAssistant):
    """Test meeting analysis service"""
    
    @patch('services.analysis_service.OpenAI')
    def test_analyze_meeting_success(self, mock_openai):
        """Test successful meeting analysis"""
        # Mock the OpenAI client and its chat.completions.create method
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.tool_calls = [Mock()]
        mock_response.choices[0].message.tool_calls[0].function.arguments = json.dumps({
            'summary': 'Test meeting summary',
            'action_items': [{'task': 'Test task', 'owner': 'Test owner'}],
            'topics_discussed': ['test topic'],
            'key_decisions': ['test decision']
        })
        mock_client.chat.completions.create.return_value = mock_response
        
        analysis_service = AnalysisService()
        result = analysis_service.analyze_meeting("Test transcription")
        
        self.assertIsInstance(result, dict)
        self.assertIn('summary', result)
        self.assertIn('action_items', result)
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('services.analysis_service.OpenAI')
    def test_analyze_meeting_failure(self, mock_openai):
        """Test meeting analysis failure handling"""
        # Mock the OpenAI client to raise an exception
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        analysis_service = AnalysisService()
        result = analysis_service.analyze_meeting("Test transcription")
        
        # Should return fallback analysis, not raise exception
        self.assertIsInstance(result, dict)
        self.assertIn('summary', result)
        self.assertIn('Meeting analysis unavailable', result['summary'])

class TestSearchService(TestSmartMeetingAssistant):
    """Test search and embedding service"""
    
    @patch('services.search_service.OpenAI')
    def test_create_embedding_success(self, mock_openai):
        """Test successful embedding creation"""
        # Mock the OpenAI client and its embeddings.create method
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1] * 1536
        mock_client.embeddings.create.return_value = mock_response
        
        search_service = SearchService()
        result = search_service.create_embedding("Test text")
        
        self.assertEqual(len(result), 1536)
        mock_client.embeddings.create.assert_called_once()
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        # Create a SearchService with mocked OpenAI for initialization
        with patch('services.search_service.OpenAI'):
            search_service = SearchService()
        
        vec1 = [1, 2, 3]
        vec2 = [2, 4, 6]
        
        similarity = search_service.cosine_similarity(vec1, vec2)
        
        self.assertAlmostEqual(similarity, 1.0, places=5)  # Perfect correlation
    
    def test_search_meetings(self):
        """Test meeting search functionality"""
        meetings = [self.sample_meeting]
        
        # Create a SearchService with mocked OpenAI for initialization
        with patch('services.search_service.OpenAI'):
            search_service = SearchService()
        
        with patch.object(search_service, 'create_embedding', return_value=[0.1] * 1536):
            results = search_service.search_meetings("project planning", meetings)
            
        self.assertIsInstance(results, list)
        if results:  # If search returns results
            self.assertIn('meeting_id', results[0])
            self.assertIn('similarity', results[0])

class TestVisualService(TestSmartMeetingAssistant):
    """Test visual summary generation service"""
    
    @patch('services.visual_service.OpenAI')
    def test_generate_visual_summary_success(self, mock_openai):
        """Test successful visual summary generation"""
        # Mock OpenAI client and DALL-E response
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].url = "https://example.com/image.png"
        mock_client.images.generate.return_value = mock_response
        
        visual_service = VisualService()
        result = visual_service.generate_visual_summary("Test summary")
            
        self.assertIsInstance(result, str)
        self.assertEqual(result, "https://example.com/image.png")
        mock_client.images.generate.assert_called_once()

class TestIntegrationService(TestSmartMeetingAssistant):
    """Test calendar and task integration service"""
    
    def setUp(self):
        super().setUp()
        self.integration_service = IntegrationService()
    
    def test_create_calendar_events(self):
        """Test calendar event creation"""
        analysis = self.sample_meeting['analysis']
        
        events = self.integration_service.create_calendar_events(analysis)
        
        self.assertIsInstance(events, list)
        if events:
            self.assertIn('title', events[0])
            self.assertIn('start_time', events[0])
    
    def test_create_task_assignments(self):
        """Test task assignment creation"""
        analysis = self.sample_meeting['analysis']
        
        tasks = self.integration_service.create_task_assignments(analysis)
        
        self.assertIsInstance(tasks, list)
        if tasks:
            self.assertIn('title', tasks[0])
            self.assertIn('assignee', tasks[0])

class TestFlaskEndpoints(TestSmartMeetingAssistant):
    """Test Flask API endpoints"""
    
    def test_index_endpoint(self):
        """Test main page endpoint"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_upload_no_file(self):
        """Test upload endpoint without file"""
        response = self.app.post('/upload')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.load_meetings')
    def test_search_endpoint(self, mock_load):
        """Test search endpoint"""
        mock_load.return_value = [self.sample_meeting]
        
        with patch.object(SearchService, 'search_meetings', return_value=[]):
            response = self.app.get('/search?q=test')
            
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('success', data)
    
    @patch('app.load_meetings')
    def test_insights_endpoint(self, mock_load):
        """Test cross-meeting insights endpoint"""
        mock_load.return_value = [self.sample_meeting]
        
        with patch.object(SearchService, 'get_meeting_insights', return_value={}):
            response = self.app.get('/api/insights')
            
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('insights', data)

class TestDataPersistence(TestSmartMeetingAssistant):
    """Test data loading and saving functionality"""
    
    def test_load_meetings_empty(self):
        """Test loading meetings when file doesn't exist"""
        with patch('os.path.exists', return_value=False):
            meetings = load_meetings()
            
        self.assertEqual(meetings, [])
    
    def test_save_and_load_meetings(self):
        """Test saving and loading meetings"""
        test_meetings = [self.sample_meeting]
        
        with patch('app.open', unittest.mock.mock_open()) as mock_file:
            with patch('os.makedirs'):
                save_meetings(test_meetings)
                
        mock_file.assert_called_once()

if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestAudioService,
        TestAnalysisService, 
        TestSearchService,
        TestVisualService,
        TestIntegrationService,
        TestFlaskEndpoints,
        TestDataPersistence
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
