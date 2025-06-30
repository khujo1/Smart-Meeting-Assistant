import os
import json
import logging
from openai import OpenAI
from typing import Dict, List, Optional, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def generate_visual_summary(self, meeting_summary: str) -> str:
        """
        Generate visual summary using DALL-E 3
        
        Args:
            meeting_summary (str): Meeting summary text
            
        Returns:
            str: URL of generated image
        """
        try:
            if not meeting_summary or not meeting_summary.strip():
                raise ValueError("Meeting summary cannot be empty")
            
            # Create a prompt for DALL-E based on meeting content
            prompt = self._create_visual_prompt(meeting_summary)
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info("Successfully generated visual summary")
            return image_url
        
        except Exception as e:
            logger.error(f"Visual generation failed: {str(e)}")
            raise Exception(f"Visual generation failed: {str(e)}")
    
    def _create_visual_prompt(self, summary: str) -> str:
        """
        Create DALL-E prompt based on meeting summary
        
        Args:
            summary (str): Meeting summary
            
        Returns:
            str: DALL-E prompt
        """
        # Extract key concepts for visualization
        base_prompt = """Create a professional, clean infographic-style illustration that represents a business meeting summary. The image should include:

- Modern office or meeting room setting
- Professional business people discussing
- Visual elements like charts, graphs, or presentation screens
- Clean, corporate aesthetic with blue and white color scheme
- Symbols representing collaboration, decisions, and action items
- Abstract elements suggesting productivity and efficiency

Style: Modern, clean, professional infographic. No text or words in the image."""
        
        # Enhance prompt based on summary content
        summary_lower = summary.lower()
        
        if 'project' in summary_lower:
            base_prompt += " Include project management elements like timelines or milestones."
        
        if 'decision' in summary_lower:
            base_prompt += " Emphasize decision-making with visual elements like checkmarks or selection symbols."
        
        if any(word in summary_lower for word in ['budget', 'financial', 'cost', 'revenue']):
            base_prompt += " Include financial elements like charts or calculator symbols."
        
        return base_prompt
    
    def generate_presentation_asset(self, key_points: List[str]) -> str:
        """
        Generate presentation-ready visual asset
        
        Args:
            key_points (list): List of key meeting points
            
        Returns:
            str: URL of generated presentation asset
        """
        try:
            if not key_points:
                key_points = ['business meeting', 'collaboration', 'productivity']
            
            # Ensure key_points are strings
            key_points = [str(point) for point in key_points if point]
            
            prompt = f"""Create a professional presentation slide background with abstract business elements. 

Key themes to represent visually: {', '.join(key_points[:3])}

Style requirements:
- Clean, modern design suitable for business presentations
- Professional color palette (blues, grays, whites)
- Abstract geometric shapes and business icons
- Space for text overlay
- Corporate meeting room aesthetic
- No text or words in the image
- High contrast for readability when text is added later"""
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",  # Presentation aspect ratio
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info("Successfully generated presentation asset")
            return image_url
        
        except Exception as e:
            logger.error(f"Presentation asset generation failed: {str(e)}")
            raise Exception(f"Presentation asset generation failed: {str(e)}")
    
    def generate_concept_illustration(self, concept_text: str) -> str:
        """
        Generate conceptual illustration for complex ideas
        
        Args:
            concept_text (str): Text describing the concept
            
        Returns:
            str: URL of generated concept illustration
        """
        try:
            if not concept_text or not concept_text.strip():
                raise ValueError("Concept text cannot be empty")
            
            prompt = f"""Create a professional conceptual illustration representing: {concept_text}

Style requirements:
- Clean, modern business illustration
- Abstract but meaningful visual metaphors
- Professional color palette
- Suitable for business stakeholders
- Clear visual hierarchy
- No text or words in the image
- Infographic-style design elements"""
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info("Successfully generated concept illustration")
            return image_url
        
        except Exception as e:
            logger.error(f"Concept illustration generation failed: {str(e)}")
            raise Exception(f"Concept illustration generation failed: {str(e)}")