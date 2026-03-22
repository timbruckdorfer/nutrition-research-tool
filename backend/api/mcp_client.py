"""
MCP Client for FastAPI

This module handles communication between FastAPI and the MCP server.
It calls MCP tools to analyze papers and returns structured results.

Note: For now, we'll call the tools directly (same process).
In production, you could run MCP server separately and connect via stdio.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add mcp_server to path so we can import tools
MCP_SERVER_DIR = Path(__file__).parent.parent / "mcp_server"
sys.path.insert(0, str(MCP_SERVER_DIR))

# Import tools directly (in-process for simplicity)
from tools.pdf_extractor import pdf_extractor
from tools.llm_analyzer import llm_analyzer


async def analyze_paper_via_mcp(pdf_path: str) -> Dict[str, Any]:
    """
    Analyze a research paper using MCP tools.
    
    This orchestrates the full pipeline:
    1. Extract PDF text
    2. Analyze metadata (authors, year, journal, etc.)
    3. Analyze methodology (sample size, duration, etc.)
    4. Combine results
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with:
            - success: Boolean
            - data: Combined metadata + methodology (if successful)
            - error: Error message (if failed)
            
    Example successful response:
        {
            "success": True,
            "data": {
                "file_name": "paper.pdf",
                "authors": ["John Smith", "Jane Doe"],
                "publication_year": 2024,
                "journal": "Nature",
                "doi": "10.1038/xxxxx",
                "country_of_publication": "USA",
                "title": "Paper Title",
                "paper_type": "original",
                "study_sample_size": 200,
                "study_duration": "6 months",
                "inclusion_criteria": "Adults 18-65",
                "country_of_population": "USA",
                "objective": "To study...",
                "conclusion": "We found...",
                "methodology_summary": "RCT with..."
            }
        }
    """
    
    try:
        # Step 1: Extract PDF text
        pdf_result = pdf_extractor.extract_text(pdf_path)
        
        if not pdf_result["success"]:
            return {
                "success": False,
                "error": f"PDF extraction failed: {pdf_result.get('error')}",
                "step": "pdf_extraction"
            }
        
        paper_text = pdf_result["text"]
        file_name = pdf_result["file_name"]
        
        # Step 2: Analyze metadata
        metadata_result = llm_analyzer.analyze_metadata(paper_text)
        
        if not metadata_result["success"]:
            return {
                "success": False,
                "error": f"Metadata analysis failed: {metadata_result.get('error')}",
                "step": "metadata_analysis",
                "file_name": file_name
            }
        
        # Step 3: Analyze methodology
        methodology_result = llm_analyzer.analyze_methodology(paper_text)
        
        if not methodology_result["success"]:
            return {
                "success": False,
                "error": f"Methodology analysis failed: {methodology_result.get('error')}",
                "step": "methodology_analysis",
                "file_name": file_name
            }
        
        # Step 4: Combine results
        combined_data = {
            "file_name": file_name,
            **metadata_result["data"],
            **methodology_result["data"]
        }
        
        # Step 5: Translate combined data to Spanish
        spanish_result = llm_analyzer.translate_to_spanish(combined_data)
        spanish_data = spanish_result["data"] if spanish_result["success"] else combined_data
        
        return {
            "success": True,
            "data": combined_data,
            "spanish_data": spanish_data,
            "tokens_used": {
                "metadata": metadata_result.get("tokens_used", 0),
                "methodology": methodology_result.get("tokens_used", 0),
                "spanish": spanish_result.get("tokens_used", 0),
                "total": (
                    metadata_result.get("tokens_used", 0) +
                    methodology_result.get("tokens_used", 0) +
                    spanish_result.get("tokens_used", 0)
                )
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error during analysis: {str(e)}",
            "step": "unknown"
        }


# Alternative: Connect to MCP server via stdio (more advanced)
# This would be used if MCP server runs as separate process
"""
from mcp import ClientSession
import asyncio

async def analyze_via_stdio_mcp(pdf_path: str):
    # Start MCP server as subprocess
    # Connect via stdin/stdout
    # Call tools via MCP protocol
    # This is more complex but allows true process isolation
    pass
"""
