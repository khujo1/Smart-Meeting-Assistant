import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationService:
    """
    Service for integrating with external calendar and task management systems
    Simulates integration with Google Calendar, Outlook, Asana, etc.
    """
    
    def __init__(self):
        self.calendar_events = []  # Simulated calendar storage
        self.task_assignments = []  # Simulated task storage
        
    def create_calendar_events(self, meeting_analysis: Dict[str, Any]) -> List[Dict]:
        """
        Create calendar events based on meeting analysis
        
        Args:
            meeting_analysis: Analysis results from GPT-4
            
        Returns:
            List of created calendar events
        """
        try:
            events = []
            action_items = meeting_analysis.get('action_items', [])
            
            for item in action_items:
                if item.get('deadline'):
                    event = {
                        'id': f"event_{len(self.calendar_events) + 1}",
                        'title': f"Follow-up: {item.get('task', 'Task')}",
                        'description': f"Action item from meeting. Owner: {item.get('owner', 'Unassigned')}",
                        'start_time': self._parse_deadline(item['deadline']),
                        'duration_minutes': 30,
                        'attendees': [item.get('owner', 'unassigned@company.com')],
                        'location': 'Meeting Room / Video Call',
                        'status': 'confirmed',
                        'created_at': datetime.now().isoformat()
                    }
                    events.append(event)
                    self.calendar_events.append(event)
            
            # Create follow-up meeting if there are multiple action items
            if len(action_items) > 3:
                follow_up_event = {
                    'id': f"event_{len(self.calendar_events) + 1}",
                    'title': 'Action Items Follow-up Meeting',
                    'description': f'Review progress on {len(action_items)} action items from meeting',
                    'start_time': (datetime.now() + timedelta(weeks=1)).isoformat(),
                    'duration_minutes': 60,
                    'attendees': list(set([item.get('owner', 'unassigned@company.com') for item in action_items])),
                    'location': 'Conference Room A',
                    'status': 'tentative',
                    'created_at': datetime.now().isoformat()
                }
                events.append(follow_up_event)
                self.calendar_events.append(follow_up_event)
            
            logger.info(f"Created {len(events)} calendar events")
            return events
            
        except Exception as e:
            logger.error(f"Failed to create calendar events: {str(e)}")
            return []
    
    def create_task_assignments(self, meeting_analysis: Dict[str, Any]) -> List[Dict]:
        """
        Create task assignments based on meeting analysis
        
        Args:
            meeting_analysis: Analysis results from GPT-4
            
        Returns:
            List of created task assignments
        """
        try:
            tasks = []
            action_items = meeting_analysis.get('action_items', [])
            
            for item in action_items:
                task = {
                    'id': f"task_{len(self.task_assignments) + 1}",
                    'title': item.get('task', 'Untitled Task'),
                    'description': f"Action item from meeting analysis",
                    'assignee': item.get('owner', 'Unassigned'),
                    'priority': item.get('priority', 'medium'),
                    'due_date': self._parse_deadline(item.get('deadline', '')),
                    'status': 'not_started',
                    'project': meeting_analysis.get('project_name', 'General'),
                    'tags': ['meeting-action-item', 'auto-generated'],
                    'created_at': datetime.now().isoformat(),
                    'estimated_hours': self._estimate_hours(item.get('task', ''))
                }
                tasks.append(task)
                self.task_assignments.append(task)
            
            # Create tasks for key decisions follow-up
            decisions = meeting_analysis.get('key_decisions', [])
            for decision in decisions:
                if decision.get('impact') and 'high' in decision.get('impact', '').lower():
                    task = {
                        'id': f"task_{len(self.task_assignments) + 1}",
                        'title': f"Implement Decision: {decision.get('decision', 'Decision')[:50]}...",
                        'description': f"Follow-up on high-impact decision. Context: {decision.get('context', '')}",
                        'assignee': 'Project Manager',
                        'priority': 'high',
                        'due_date': (datetime.now() + timedelta(days=7)).isoformat(),
                        'status': 'not_started',
                        'project': meeting_analysis.get('project_name', 'General'),
                        'tags': ['decision-implementation', 'high-impact'],
                        'created_at': datetime.now().isoformat(),
                        'estimated_hours': 4
                    }
                    tasks.append(task)
                    self.task_assignments.append(task)
            
            logger.info(f"Created {len(tasks)} task assignments")
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to create task assignments: {str(e)}")
            return []
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Get summary of all integrations"""
        return {
            'calendar_events': len(self.calendar_events),
            'task_assignments': len(self.task_assignments),
            'upcoming_events': [e for e in self.calendar_events if datetime.fromisoformat(e['start_time']) > datetime.now()],
            'pending_tasks': [t for t in self.task_assignments if t['status'] == 'not_started']
        }
    
    def _parse_deadline(self, deadline_str: str) -> str:
        """Parse deadline string and return ISO format datetime"""
        try:
            if not deadline_str or deadline_str.lower() in ['none', 'no deadline', 'tbd']:
                return (datetime.now() + timedelta(weeks=2)).isoformat()
            
            # Simple parsing for common formats
            deadline_lower = deadline_str.lower()
            if 'week' in deadline_lower:
                weeks = 1
                if 'two' in deadline_lower or '2' in deadline_lower:
                    weeks = 2
                return (datetime.now() + timedelta(weeks=weeks)).isoformat()
            elif 'day' in deadline_lower:
                days = 7
                if 'tomorrow' in deadline_lower:
                    days = 1
                elif 'few' in deadline_lower:
                    days = 3
                return (datetime.now() + timedelta(days=days)).isoformat()
            elif 'month' in deadline_lower:
                return (datetime.now() + timedelta(days=30)).isoformat()
            else:
                return (datetime.now() + timedelta(weeks=1)).isoformat()
                
        except Exception:
            return (datetime.now() + timedelta(weeks=1)).isoformat()
    
    def _estimate_hours(self, task_description: str) -> int:
        """Estimate hours needed for a task based on description"""
        description_lower = task_description.lower()
        
        if any(word in description_lower for word in ['research', 'analyze', 'investigate']):
            return 4
        elif any(word in description_lower for word in ['implement', 'develop', 'create']):
            return 8
        elif any(word in description_lower for word in ['review', 'check', 'verify']):
            return 2
        elif any(word in description_lower for word in ['meeting', 'discuss', 'call']):
            return 1
        else:
            return 3  # Default estimate
