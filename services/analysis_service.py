import os
import json
from openai import OpenAI
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def analyze_meeting(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze meeting transcript using GPT-4 with function calling
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            dict: Analysis results with summary, action items, and decisions
        """
        try:
            if not transcript or not transcript.strip():
                raise ValueError("Transcript cannot be empty")
            
            # Updated function schema for modern OpenAI API
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "extract_meeting_insights",
                        "description": "Extract structured insights from meeting transcript",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "summary": {
                                    "type": "string",
                                    "description": "Concise meeting summary (2-3 paragraphs)"
                                },
                                "key_decisions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "decision": {"type": "string"},
                                            "context": {"type": "string"},
                                            "impact": {"type": "string"}
                                        }
                                    },
                                    "description": "List of key decisions made"
                                },
                                "action_items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "task": {"type": "string"},
                                            "owner": {"type": "string"},
                                            "deadline": {"type": "string"},
                                            "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                                        }
                                    },
                                    "description": "List of action items with owners"
                                },
                                "participants": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of meeting participants"
                                },
                                "topics_discussed": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Main topics discussed"
                                },
                                "meeting_effectiveness_score": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 10,
                                    "description": "Meeting effectiveness score (1-10)"
                                },
                                "recommendations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Recommendations for follow-up"
                                }
                            },
                            "required": ["summary", "action_items", "key_decisions", "participants", "topics_discussed"]
                        }
                    }
                }
            ]
            
            # Analyze transcript with GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert meeting analyst for KIU Consulting. Analyze meeting transcripts to extract actionable insights that will help reduce the 25,000 GEL annual cost per employee from ineffective meetings.

Focus on:
- Clear, actionable summaries
- Specific action items with owners
- Key decisions and their business impact
- Meeting effectiveness assessment
- Recommendations for improvement

Be precise and business-focused in your analysis."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this meeting transcript and extract key insights:\n\n{transcript[:4000]}"  # Limit to avoid token limits
                    }
                ],
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "extract_meeting_insights"}}
            )
            
            # Parse function call result
            if response.choices[0].message.tool_calls:
                function_call = response.choices[0].message.tool_calls[0]
                insights = json.loads(function_call.function.arguments)
                logger.info("Successfully analyzed meeting transcript")
                return insights
            else:
                raise Exception("No function call in response")
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in meeting analysis: {str(e)}")
            # Return fallback analysis
            return self._fallback_analysis(transcript)
        
        except Exception as e:
            logger.error(f"Meeting analysis failed: {str(e)}")
            return self._fallback_analysis(transcript)
    
    def _fallback_analysis(self, transcript: str) -> Dict[str, Any]:
        """Fallback analysis when API fails"""
        return {
            "summary": "Meeting analysis unavailable due to processing error. Please try again.",
            "key_decisions": [],
            "action_items": [],
            "participants": [],
            "topics_discussed": ["Unable to process"],
            "meeting_effectiveness_score": 5,
            "recommendations": ["Review transcript manually", "Retry analysis"]
        }
    
    def generate_follow_up_tasks(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate calendar/task integration using function calling
        
        Args:
            analysis (dict): Meeting analysis results
            
        Returns:
            dict: Task integration recommendations
        """
        try:
            if not analysis or not analysis.get('action_items'):
                return {"calendar_events": [], "task_assignments": []}
            
            # Updated function schema
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "create_task_integration",
                        "description": "Create task and calendar integration recommendations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "calendar_events": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"type": "string"},
                                            "description": {"type": "string"},
                                            "suggested_date": {"type": "string"},
                                            "duration": {"type": "integer"},
                                            "attendees": {"type": "array", "items": {"type": "string"}}
                                        }
                                    }
                                },
                                "task_assignments": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "task_title": {"type": "string"},
                                            "description": {"type": "string"},
                                            "assignee": {"type": "string"},
                                            "due_date": {"type": "string"},
                                            "project": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a task management assistant. Convert meeting insights into actionable calendar events and task assignments."
                    },
                    {
                        "role": "user",
                        "content": f"Create task and calendar recommendations based on this meeting analysis:\n\n{json.dumps(analysis, indent=2)}"
                    }
                ],
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "create_task_integration"}}
            )
            
            if response.choices[0].message.tool_calls:
                function_call = response.choices[0].message.tool_calls[0]
                integration = json.loads(function_call.function.arguments)
                logger.info("Successfully generated follow-up tasks")
                return integration
            else:
                return {"calendar_events": [], "task_assignments": []}
        
        except Exception as e:
            logger.error(f"Task integration failed: {str(e)}")
            return {"calendar_events": [], "task_assignments": []}
