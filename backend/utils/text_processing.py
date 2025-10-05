"""
Text processing utilities for the Space Biology Knowledge Engine.
"""
import re
import string
from typing import List, Set, Optional
import asyncio
from collections import Counter


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep scientific notation
    text = re.sub(r'[^\w\s\-\.\(\)\[\]\/\+\=\<\>]', '', text)
    
    return text


def extract_sentences(text: str) -> List[str]:
    """
    Extract sentences from text.
    
    Args:
        text: Input text
        
    Returns:
        List[str]: List of sentences
    """
    if not text:
        return []
    
    # Simple sentence splitting (can be improved with NLTK/spaCy)
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


async def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis.
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List[str]: Extracted keywords
    """
    if not text:
        return []
    
    # Convert to lowercase and clean
    text = clean_text(text.lower())
    
    # Define stop words (common English words to ignore)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'this', 'that', 'these', 'those', 'is', 'are', 
        'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
        'can', 'cannot', 'not', 'no', 'yes', 'we', 'our', 'us', 'i', 'you',
        'he', 'she', 'it', 'they', 'them', 'his', 'her', 'its', 'their'
    }
    
    # Extract words (2+ characters, alphanumeric)
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
    
    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count frequency and get top keywords
    word_counts = Counter(keywords)
    top_keywords = [word for word, count in word_counts.most_common(max_keywords)]
    
    return top_keywords


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text
        chunk_size: Maximum chunk size in characters
        overlap: Overlap between chunks in characters
        
    Returns:
        List[str]: Text chunks
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at word boundary
        if end < len(text):
            # Look for space within last 100 characters
            space_pos = text.rfind(' ', start, end)
            if space_pos > start:
                end = space_pos
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Input text
        
    Returns:
        List[str]: Found URLs
    """
    if not text:
        return []
    
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # Remove duplicates


def extract_doi(text: str) -> Optional[str]:
    """
    Extract DOI from text.
    
    Args:
        text: Input text
        
    Returns:
        Optional[str]: Found DOI
    """
    if not text:
        return None
    
    # DOI pattern
    doi_pattern = r'10\.\d{4,}\/[^\s]+'
    match = re.search(doi_pattern, text)
    return match.group() if match else None


def normalize_author_name(name: str) -> str:
    """
    Normalize author name format.
    
    Args:
        name: Author name
        
    Returns:
        str: Normalized name
    """
    if not name:
        return ""
    
    # Remove extra whitespace and punctuation
    name = re.sub(r'[^\w\s\-\.]', '', name.strip())
    name = re.sub(r'\s+', ' ', name)
    
    # Capitalize properly
    parts = name.split()
    normalized_parts = []
    
    for part in parts:
        if len(part) == 1 or (len(part) == 2 and part.endswith('.')):
            # Initial
            normalized_parts.append(part.upper())
        else:
            # Full name
            normalized_parts.append(part.capitalize())
    
    return ' '.join(normalized_parts)


def extract_years(text: str) -> List[int]:
    """
    Extract years from text.
    
    Args:
        text: Input text
        
    Returns:
        List[int]: Found years
    """
    if not text:
        return []
    
    # Look for 4-digit years between 1900 and 2030
    year_pattern = r'\b(19[0-9]{2}|20[0-2][0-9]|2030)\b'
    years = re.findall(year_pattern, text)
    return [int(year) for year in set(years)]


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity using word overlap.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        float: Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Convert to lowercase and extract words
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


# Export functions
__all__ = [
    "clean_text",
    "extract_sentences", 
    "extract_keywords",
    "chunk_text",
    "extract_urls",
    "extract_doi",
    "normalize_author_name",
    "extract_years",
    "calculate_text_similarity"
]