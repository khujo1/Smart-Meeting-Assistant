import os
import json
import logging
import math
from openai import OpenAI
from typing import Dict, List, Optional, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embedding_model = "text-embedding-3-small"
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for text using OpenAI Embeddings API
        
        Args:
            text (str): Text to embed
            
        Returns:
            list: Embedding vector
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty for embedding")
            
            # Limit text length to avoid API limits
            text = text[:8000]  # Reasonable limit for embeddings
            
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Successfully created embedding for text of length {len(text)}")
            return embedding
        
        except Exception as e:
            logger.error(f"Embedding creation failed: {str(e)}")
            raise Exception(f"Embedding creation failed: {str(e)}")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1 (list): First vector
            vec2 (list): Second vector
            
        Returns:
            float: Cosine similarity score
        """
        try:
            # Handle edge cases
            if len(vec1) != len(vec2):
                logger.warning(f"Vector length mismatch: {len(vec1)} vs {len(vec2)}")
                return 0.0
            
            if len(vec1) == 0:
                return 0.0
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Calculate magnitudes
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(a * a for a in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(-1.0, min(1.0, similarity))  # Clamp to [-1, 1]
        
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {str(e)}")
            return 0.0
    
    def search_meetings(self, query: str, meetings: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Search meetings using semantic similarity
        
        Args:
            query (str): Search query
            meetings (list): List of meeting data
            top_k (int): Number of top results to return
            
        Returns:
            list: Ranked search results
        """
        try:
            if not query or not query.strip():
                logger.warning("Empty search query provided")
                return []
            
            if not meetings:
                logger.warning("No meetings provided for search")
                return []
            
            # Create embedding for query
            try:
                query_embedding = self.create_embedding(query)
            except Exception as e:
                logger.error(f"Failed to create query embedding: {str(e)}")
                return []
            
            # Calculate similarities
            results = []
            for meeting in meetings:
                try:
                    # Check if meeting has required fields
                    if not isinstance(meeting, dict):
                        continue
                    
                    if 'embedding' not in meeting or not meeting['embedding']:
                        logger.warning(f"Meeting {meeting.get('id', 'unknown')} missing embedding")
                        continue
                    
                    similarity = self.cosine_similarity(query_embedding, meeting['embedding'])
                    
                    # Extract safe data
                    analysis = meeting.get('analysis', {})
                    summary = analysis.get('summary', '')
                    
                    result = {
                        'meeting_id': meeting.get('id', 'unknown'),
                        'filename': meeting.get('filename', 'unknown'),
                        'timestamp': meeting.get('timestamp', ''),
                        'similarity': similarity,
                        'summary': summary[:300] + '...' if len(summary) > 300 else summary,
                        'topics': analysis.get('topics_discussed', []),
                        'action_items_count': len(analysis.get('action_items', []))
                    }
                    results.append(result)
                
                except Exception as e:
                    logger.error(f"Error processing meeting {meeting.get('id', 'unknown')}: {str(e)}")
                    continue
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            logger.info(f"Search completed: found {len(results)} results for query '{query}'")
            return results[:top_k]
        
        except Exception as e:
            logger.error(f"Meeting search failed: {str(e)}")
            return []
    
    def find_similar_meetings(self, meeting_id: int, meetings: List[Dict], top_k: int = 3) -> List[Dict]:
        """
        Find meetings similar to a given meeting
        
        Args:
            meeting_id (int): ID of the reference meeting
            meetings (list): List of meeting data
            top_k (int): Number of similar meetings to return
            
        Returns:
            list: Similar meetings
        """
        try:
            # Find reference meeting
            reference_meeting = None
            for meeting in meetings:
                if meeting.get('id') == meeting_id:
                    reference_meeting = meeting
                    break
            
            if not reference_meeting or 'embedding' not in reference_meeting:
                logger.warning(f"Reference meeting {meeting_id} not found or missing embedding")
                return []
            
            reference_embedding = reference_meeting['embedding']
            
            # Calculate similarities with other meetings
            similarities = []
            for meeting in meetings:
                if meeting.get('id') == meeting_id or 'embedding' not in meeting:
                    continue
                
                try:
                    similarity = self.cosine_similarity(reference_embedding, meeting['embedding'])
                    
                    analysis = meeting.get('analysis', {})
                    summary = analysis.get('summary', '')
                    
                    result = {
                        'meeting_id': meeting.get('id'),
                        'filename': meeting.get('filename', 'unknown'),
                        'timestamp': meeting.get('timestamp', ''),
                        'similarity': similarity,
                        'summary': summary[:200] + '...' if len(summary) > 200 else summary
                    }
                    similarities.append(result)
                
                except Exception as e:
                    logger.error(f"Error processing similar meeting {meeting.get('id')}: {str(e)}")
                    continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            logger.info(f"Found {len(similarities)} similar meetings to {meeting_id}")
            return similarities[:top_k]
        
        except Exception as e:
            logger.error(f"Similar meeting search failed: {str(e)}")
            return []
    
    def get_meeting_insights(self, meetings: List[Dict]) -> Dict[str, Any]:
        """
        Extract cross-meeting insights using embeddings
        
        Args:
            meetings (list): List of meeting data
            
        Returns:
            dict: Cross-meeting insights
        """
        try:
            if not meetings:
                return {
                    'common_themes': [],
                    'total_meetings': 0,
                    'total_action_items': 0,
                    'recommendations': ['No meetings to analyze']
                }
            
            # Collect all topics and action items safely
            all_topics = []
            all_action_items = []
            
            for meeting in meetings:
                try:
                    analysis = meeting.get('analysis', {})
                    topics = analysis.get('topics_discussed', [])
                    action_items = analysis.get('action_items', [])
                    
                    if isinstance(topics, list):
                        all_topics.extend([str(topic) for topic in topics])
                    
                    if isinstance(action_items, list):
                        for item in action_items:
                            if isinstance(item, dict):
                                task = item.get('task', '')
                                if task:
                                    all_action_items.append(str(task))
                
                except Exception as e:
                    logger.error(f"Error processing meeting insights for {meeting.get('id')}: {str(e)}")
                    continue
            
            # Find common themes
            if all_topics:
                # Simple frequency-based approach
                topic_counts = {}
                for topic in all_topics:
                    topic_lower = topic.lower().strip()
                    if topic_lower:
                        topic_counts[topic_lower] = topic_counts.get(topic_lower, 0) + 1
                
                # Get topics that appear more than once
                common_themes = [topic for topic, count in topic_counts.items() if count > 1]
                common_themes = sorted(common_themes, key=lambda x: topic_counts[x], reverse=True)[:5]
            else:
                common_themes = []
            
            insights = {
                'common_themes': common_themes,
                'total_meetings': len(meetings),
                'total_action_items': len(all_action_items),
                'recommendations': [
                    'Consider consolidating meetings on similar topics',
                    'Review recurring action items for process improvements',
                    'Set up automated follow-ups for high-priority items'
                ]
            }
            
            logger.info(f"Generated insights for {len(meetings)} meetings")
            return insights
        
        except Exception as e:
            logger.error(f"Cross-meeting insights failed: {str(e)}")
            return {
                'common_themes': [],
                'total_meetings': len(meetings) if meetings else 0,
                'total_action_items': 0,
                'recommendations': ['Error generating insights']
            }
