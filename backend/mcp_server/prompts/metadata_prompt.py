"""
Metadata Extraction Prompt

This prompt instructs GPT-4o to extract bibliographic metadata from research papers.
It uses structured JSON output to ensure reliable parsing.
"""

METADATA_EXTRACTION_PROMPT = """You are an expert research librarian analyzing scientific papers. Extract the following bibliographic metadata from the research paper provided.

**Instructions:**
1. Extract ONLY the information that is clearly stated in the paper
2. For missing information, use null (not empty strings)
3. For country of publication, look at:
   - Author affiliations (institutions and their countries)
   - Corresponding author location
   - If multiple countries, use the country of the FIRST author
4. Return ONLY valid JSON with no additional text

**Required JSON Structure:**
{{
    "authors": ["FirstName LastName", ...],  // List of all author names
    "publication_year": 2024,                 // Year as integer, or null
    "journal": "Journal Name",                // Full journal name, or null
    "doi": "10.xxxx/xxxxx",                   // DOI string, or null
    "country_of_publication": "Country",      // Country of first author's institution
    "title": "Paper Title",                   // Full paper title
    "paper_type": "original|review|cohort|meta-analysis|case-study|other"  // Best guess of paper type
}}

**Paper Text:**
{paper_text}

**JSON Output:**"""


def get_metadata_prompt(paper_text: str, max_chars: int = 50000) -> str:
    """
    Generate the metadata extraction prompt with the paper text.
    
    Args:
        paper_text: The full text extracted from the PDF
        max_chars: Maximum characters to include (to avoid token limits)
        
    Returns:
        The complete prompt ready to send to GPT-4o
        
    Note:
        GPT-4o has a context limit. For very long papers, we truncate.
        The most important metadata is usually in the first few pages anyway.
    """
    # Truncate paper text if too long
    if len(paper_text) > max_chars:
        paper_text = paper_text[:max_chars] + "\n\n[... paper truncated for length ...]"
    
    return METADATA_EXTRACTION_PROMPT.format(paper_text=paper_text)


# Example response format (for documentation/testing)
EXAMPLE_METADATA_RESPONSE = {
    "authors": [
        "Liezhou Zhong",
        "Jonathan M Hodgson", 
        "Joshua R Lewis",
        "Lauren C Blekkenhorst"
    ],
    "publication_year": 2025,
    "journal": "The American Journal of Clinical Nutrition",
    "doi": "10.1016/j.ajcnut.2025.01.067",
    "country_of_publication": "Australia",
    "title": "Nitrate and nitrite food composition database: an update and extensive deep dive",
    "paper_type": "original"
}
