"""
Methodology Extraction Prompt

This prompt extracts study methodology details from research papers.
Focuses on sample size, duration, inclusion criteria, and study population.
"""

METHODOLOGY_EXTRACTION_PROMPT = """You are an expert research methodologist analyzing scientific papers. Extract the following methodology information from the research paper provided.

**Instructions:**
1. Look carefully in the Methods/Methodology section
2. Extract ONLY information that is clearly stated
3. For missing information, use null
4. For country of population, this is the country where the study participants/data came from (may differ from publication country)
5. For objective, provide a 1-2 sentence summary of the study's main goal
6. For conclusion, provide a 2-3 sentence summary of the main findings
7. Return ONLY valid JSON with no additional text

**Required JSON Structure:**
{{
    "study_sample_size": 200,                 // Number of participants/samples, or null
    "study_duration": "6 months",             // Duration as string (e.g., "2 years", "6 months"), or null
    "inclusion_criteria": "Brief description", // Main inclusion criteria as string, or null
    "country_of_population": "Country",       // Country where study participants are from, or null
    "objective": "Study objective...",        // 1-2 sentence objective
    "conclusion": "Main findings...",         // 2-3 sentence summary of conclusions
    "methodology_summary": "Brief summary..."  // 1-2 sentence summary of study design
}}

**Paper Text:**
{paper_text}

**JSON Output:**"""


def get_methodology_prompt(paper_text: str, max_chars: int = 50000) -> str:
    """
    Generate the methodology extraction prompt with the paper text.
    
    Args:
        paper_text: The full text extracted from the PDF
        max_chars: Maximum characters to include
        
    Returns:
        The complete prompt ready to send to GPT-4o
        
    Note:
        Methodology is usually in the middle of papers, but we include
        the full text (truncated if needed) to also capture objectives
        (from intro) and conclusions (from end).
    """
    # Truncate paper text if too long
    if len(paper_text) > max_chars:
        # For methodology, we want to keep more of the middle
        # Take first 20k chars (intro + methods) and last 10k (results + conclusion)
        first_part = paper_text[:20000]
        last_part = paper_text[-10000:]
        paper_text = first_part + "\n\n[... middle section truncated ...]\n\n" + last_part
    
    return METHODOLOGY_EXTRACTION_PROMPT.format(paper_text=paper_text)


# Example response format (for documentation/testing)
EXAMPLE_METHODOLOGY_RESPONSE = {
    "study_sample_size": 4680,
    "study_duration": "Cross-sectional analysis",
    "inclusion_criteria": "Food items containing measurable nitrate or nitrite",
    "country_of_population": "Multiple (international food database)",
    "objective": "To provide an updated and comprehensive nitrate and nitrite food composition database for use in nutritional research and dietary assessment.",
    "conclusion": "This updated database provides comprehensive nitrate and nitrite values for 4,680 food items, significantly expanding available data for nutritional epidemiology and clinical research.",
    "methodology_summary": "Systematic literature review and laboratory analysis to compile nitrate and nitrite content across diverse food categories."
}
