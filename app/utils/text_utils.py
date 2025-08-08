import re
from typing import List

def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing common artifacts.
    
    Args:
        text: Raw text from document
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove page numbers and headers
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
    
    # Remove URLs and emails
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove common headers/footers
    headers_to_remove = [
        r'AROGYA SANJEEVANI POLICY',
        r'HEALTH INSURANCE POLICY',
        r'POLICY DOCUMENT',
        r'TERMS AND CONDITIONS',
        r'PRIVACY POLICY',
        r'DISCLAIMER',
        r'©.*?All rights reserved',
        r'Confidential',
        r'Internal Use Only'
    ]
    
    for header in headers_to_remove:
        text = re.sub(header, '', text, flags=re.IGNORECASE)
    
    # Fix hyphenation at line breaks
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def split_into_clauses(text: str) -> List[str]:
    """
    Split document text into individual clauses based on headings and structure.
    
    Args:
        text: Clean document text
        
    Returns:
        List of clause texts
    """
    if not text:
        return []
    
    # Split on numbered headings (1., 2., etc.)
    clauses = re.split(r'\n\s*\d+\.\s+', text)
    
    # Split on ALL CAPS headings
    clauses = [clause for clause in clauses if clause.strip()]
    all_caps_split = []
    for clause in clauses:
        all_caps_split.extend(re.split(r'\n\s*[A-Z][A-Z\s]{3,}\n', clause))
    
    # Split on "Section" or "Clause" markers
    final_clauses = []
    for clause in all_caps_split:
        if clause.strip():
            section_split = re.split(r'\n\s*(?:Section|Clause)\s+\d+', clause)
            final_clauses.extend([c.strip() for c in section_split if c.strip()])
    
    # If no clear splits found, split on double newlines
    if len(final_clauses) <= 1:
        final_clauses = [c.strip() for c in text.split('\n\n') if c.strip()]
    
    return final_clauses

def normalize_clause_text(text: str) -> str:
    """
    Normalize clause text for better embedding.
    
    Args:
        text: Raw clause text
        
    Returns:
        Normalized clause text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove bullet points and numbering
    text = re.sub(r'^\s*[•\-\*]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)
    
    # Clean up
    text = text.strip()
    
    return text
