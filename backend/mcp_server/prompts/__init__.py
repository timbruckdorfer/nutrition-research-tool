"""
Prompt templates for LLM-based extraction.

Each prompt is carefully crafted to get reliable, structured output from GPT-4o.
"""

from .metadata_prompt import get_metadata_prompt, EXAMPLE_METADATA_RESPONSE
from .methodology_prompt import get_methodology_prompt, EXAMPLE_METHODOLOGY_RESPONSE

__all__ = [
    'get_metadata_prompt',
    'get_methodology_prompt',
    'EXAMPLE_METADATA_RESPONSE',
    'EXAMPLE_METHODOLOGY_RESPONSE',
]
