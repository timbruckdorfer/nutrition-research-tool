"""
LLM-based Paper Analysis Tools

Uses OpenAI's GPT-4o to extract structured information from research papers.
Implements metadata extraction and methodology analysis.
"""

import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import prompts
import sys
from pathlib import Path
# Add parent directory to path so we can import prompts
sys.path.insert(0, str(Path(__file__).parent.parent))
from prompts import get_metadata_prompt, get_methodology_prompt


class LLMAnalyzer:
    """
    Analyzes research papers using OpenAI's GPT models.
    
    This class handles:
    - API authentication
    - Prompt construction
    - LLM calls with error handling
    - JSON parsing and validation
    """
    
    def __init__(self):
        """Initialize the LLM analyzer with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Please set it in backend/.env file"
            )
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
    def _call_llm(self, prompt: str, json_mode: bool = True) -> Dict[str, Any]:
        """
        Call OpenAI API with error handling.
        
        Args:
            prompt: The prompt to send to the LLM
            json_mode: Whether to use JSON response format
            
        Returns:
            Dictionary with 'success', 'data', and optional 'error' keys
        """
        try:
            # Construct API call parameters
            params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert research analyst. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,  # Low temperature for consistent, factual extraction
            }
            
            # Add JSON mode if supported and requested
            # Note: json_mode requires the prompt to explicitly ask for JSON
            if json_mode:
                params["response_format"] = {"type": "json_object"}
            
            # Make the API call
            response = self.client.chat.completions.create(**params)
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Parse JSON
            try:
                data = json.loads(content)
                return {
                    "success": True,
                    "data": data,
                    "raw_response": content,
                    "model_used": self.model,
                    "tokens_used": response.usage.total_tokens if response.usage else None
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse JSON response: {str(e)}",
                    "raw_response": content
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"LLM API call failed: {str(e)}"
            }
    
    def analyze_metadata(self, paper_text: str) -> Dict[str, Any]:
        """
        Extract bibliographic metadata from a research paper.
        
        Args:
            paper_text: Full text extracted from the PDF
            
        Returns:
            Dictionary containing:
                - success: Boolean
                - data: Extracted metadata (if successful)
                - error: Error message (if failed)
                
        Example response data:
            {
                "authors": ["John Smith", "Jane Doe"],
                "publication_year": 2024,
                "journal": "Nature",
                "doi": "10.1038/xxxxx",
                "country_of_publication": "United States",
                "title": "Paper Title",
                "paper_type": "original"
            }
        """
        if not paper_text or not paper_text.strip():
            return {
                "success": False,
                "error": "Paper text is empty"
            }
        
        # Generate prompt
        prompt = get_metadata_prompt(paper_text)
        
        # Call LLM
        result = self._call_llm(prompt, json_mode=True)
        
        if not result["success"]:
            return result
        
        # Validate required fields exist
        required_fields = ["authors", "publication_year", "journal", "doi", 
                          "country_of_publication", "title", "paper_type"]
        
        data = result["data"]
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return {
                "success": False,
                "error": f"LLM response missing fields: {missing_fields}",
                "partial_data": data
            }
        
        return result
    
    def analyze_methodology(self, paper_text: str) -> Dict[str, Any]:
        """
        Extract methodology information from a research paper.
        
        Args:
            paper_text: Full text extracted from the PDF
            
        Returns:
            Dictionary containing:
                - success: Boolean
                - data: Extracted methodology (if successful)
                - error: Error message (if failed)
                
        Example response data:
            {
                "study_sample_size": 200,
                "study_duration": "6 months",
                "inclusion_criteria": "Adults aged 18-65",
                "country_of_population": "United States",
                "objective": "To study the effects of...",
                "conclusion": "The study found that...",
                "methodology_summary": "Randomized controlled trial..."
            }
        """
        if not paper_text or not paper_text.strip():
            return {
                "success": False,
                "error": "Paper text is empty"
            }
        
        # Generate prompt
        prompt = get_methodology_prompt(paper_text)
        
        # Call LLM
        result = self._call_llm(prompt, json_mode=True)
        
        if not result["success"]:
            return result
        
        # Validate required fields exist
        required_fields = ["study_sample_size", "study_duration", "inclusion_criteria",
                          "country_of_population", "objective", "conclusion", 
                          "methodology_summary"]
        
        data = result["data"]
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return {
                "success": False,
                "error": f"LLM response missing fields: {missing_fields}",
                "partial_data": data
            }
        
        return result
    
    def translate_to_spanish(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate extracted paper data into Spanish.
        
        Args:
            data: Combined metadata + methodology dictionary (English)
            
        Returns:
            Dictionary with same keys but text fields translated to Spanish.
            Non-translatable fields (file_name, doi, year, sample_size) are kept as-is.
        """
        # Fields that should be translated
        fields_to_translate = {
            "title", "paper_type", "objective", "methodology_summary",
            "inclusion_criteria", "conclusion", "study_duration",
            "country_of_publication", "country_of_population", "journal"
        }
        
        # Build a subset of only translatable text fields
        translatable = {k: v for k, v in data.items() if k in fields_to_translate and v}
        
        if not translatable:
            return {"success": True, "data": data}
        
        prompt = f"""Translate the following JSON fields into Spanish. 
Return ONLY a valid JSON object with the same keys and translated values.
Keep proper nouns (journal names, country names) in their Spanish equivalents where they exist.
Do not add any explanation — only return the JSON.

{json.dumps(translatable, ensure_ascii=False, indent=2)}"""
        
        result = self._call_llm(prompt, json_mode=True)
        
        if not result["success"]:
            return result
        
        # Merge translated fields back with untranslated fields
        merged = {**data, **result["data"]}
        
        return {
            "success": True,
            "data": merged,
            "tokens_used": result.get("tokens_used", 0)
        }

    def analyze_full_paper(self, paper_text: str) -> Dict[str, Any]:
        """
        Extract both metadata and methodology in one call.
        
        This is more efficient than calling both separately.
        
        Args:
            paper_text: Full text extracted from the PDF
            
        Returns:
            Dictionary with both metadata and methodology, or error
        """
        # Call both analyzers
        metadata_result = self.analyze_metadata(paper_text)
        methodology_result = self.analyze_methodology(paper_text)
        
        # Combine results
        if metadata_result["success"] and methodology_result["success"]:
            return {
                "success": True,
                "metadata": metadata_result["data"],
                "methodology": methodology_result["data"],
                "tokens_used": {
                    "metadata": metadata_result.get("tokens_used"),
                    "methodology": methodology_result.get("tokens_used"),
                    "total": (metadata_result.get("tokens_used", 0) + 
                             methodology_result.get("tokens_used", 0))
                }
            }
        else:
            return {
                "success": False,
                "metadata_result": metadata_result,
                "methodology_result": methodology_result,
                "error": "One or both analysis steps failed"
            }


# Create singleton instance
llm_analyzer = LLMAnalyzer()
