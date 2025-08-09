from __future__ import annotations

from typing import List, Dict, Any
import re
import tiktoken

# Configuration constants from PRD
CHUNK_TOKENS_MIN = 550
CHUNK_TOKENS_MAX = 800
OVERLAP_RATIO = 0.15
CITATION_WINDOW_PARAS = 2

def get_token_count(text: str, model: str = "gpt-4") -> int:
    """Get accurate token count using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback estimation: roughly 4 chars per token
        return len(text) // 4


def chunk_paragraphs(paragraphs: List[str]) -> List[str]:
    """Legacy function - return paragraphs directly as chunks"""
    return paragraphs


def create_chunks(paragraphs: List[Dict[str, Any]], authority_id: str) -> List[Dict[str, Any]]:
    """Create optimized chunks following PRD specifications"""
    
    chunks = []
    
    # Separate headnotes for special handling
    headnotes = [p for p in paragraphs if _is_headnote(p)]
    regular_paras = [p for p in paragraphs if not _is_headnote(p)]
    
    # Process headnotes separately (keep intact)
    for headnote in headnotes:
        chunks.append(_create_single_chunk(
            paras=[headnote],
            authority_id=authority_id,
            chunk_type="headnote"
        ))
    
    # Process regular paragraphs with sliding window
    chunks.extend(_create_sliding_chunks(regular_paras, authority_id))
    
    # Create citation-extended chunks
    citation_chunks = _create_citation_chunks(paragraphs, authority_id)
    chunks.extend(citation_chunks)
    
    return chunks


def _is_headnote(para: Dict[str, Any]) -> bool:
    """Identify if paragraph is a headnote"""
    text = para.get("text", "").upper()
    
    # Check for headnote indicators
    indicators = ["HEADNOTE", "HELD:", "SUMMARY:", "BRIEF:", "GIST:"]
    if any(ind in text for ind in indicators):
        return True
    
    # Check if it's early, substantial paragraph (likely headnote)
    if (para.get("para_id", 0) <= 3 and 
        len(para.get("text", "").split()) > 50 and
        not any(kw in text for kw in ["PETITIONER", "RESPONDENT", "APPELLANT"])):
        return True
    
    return False


def _create_sliding_chunks(paragraphs: List[Dict[str, Any]], authority_id: str) -> List[Dict[str, Any]]:
    """Create chunks with sliding window approach"""
    
    if not paragraphs:
        return []
    
    chunks = []
    i = 0
    
    while i < len(paragraphs):
        current_chunk_paras = []
        current_tokens = 0
        
        # Build chunk up to token limit
        j = i
        while j < len(paragraphs) and current_tokens < CHUNK_TOKENS_MAX:
            para = paragraphs[j]
            para_tokens = get_token_count(para.get("text", ""))
            
            if current_tokens + para_tokens <= CHUNK_TOKENS_MAX:
                current_chunk_paras.append(para)
                current_tokens += para_tokens
                j += 1
            else:
                break
        
        # Ensure minimum chunk size
        if current_tokens < CHUNK_TOKENS_MIN and j < len(paragraphs):
            # Add one more paragraph even if it exceeds max slightly
            if j < len(paragraphs):
                current_chunk_paras.append(paragraphs[j])
                j += 1
        
        # Create chunk if we have content
        if current_chunk_paras:
            chunk = _create_single_chunk(
                paras=current_chunk_paras,
                authority_id=authority_id,
                chunk_type="content"
            )
            chunks.append(chunk)
        
        # Calculate overlap for next chunk
        if j < len(paragraphs):
            overlap_tokens = int(current_tokens * OVERLAP_RATIO)
            overlap_paras = _get_overlap_paragraphs(current_chunk_paras, overlap_tokens)
            
            # Find starting point for next chunk
            next_start = i + len(current_chunk_paras) - len(overlap_paras)
            i = max(next_start, i + 1)  # Ensure we make progress
        else:
            break
    
    return chunks


def _get_overlap_paragraphs(paragraphs: List[Dict[str, Any]], target_tokens: int) -> List[Dict[str, Any]]:
    """Get paragraphs from end that total approximately target_tokens"""
    
    overlap_paras = []
    tokens = 0
    
    for para in reversed(paragraphs):
        para_tokens = get_token_count(para.get("text", ""))
        if tokens + para_tokens <= target_tokens:
            overlap_paras.insert(0, para)
            tokens += para_tokens
        else:
            break
    
    return overlap_paras


def _create_citation_chunks(paragraphs: List[Dict[str, Any]], authority_id: str) -> List[Dict[str, Any]]:
    """Create extended chunks around citations (±2 paragraphs)"""
    
    citation_chunks = []
    
    for i, para in enumerate(paragraphs):
        if _has_citations(para):
            # Define window around citation
            start_idx = max(0, i - CITATION_WINDOW_PARAS)
            end_idx = min(len(paragraphs), i + CITATION_WINDOW_PARAS + 1)
            
            window_paras = paragraphs[start_idx:end_idx]
            
            chunk = _create_single_chunk(
                paras=window_paras,
                authority_id=authority_id,
                chunk_type="citation_context"
            )
            citation_chunks.append(chunk)
    
    return citation_chunks


def _has_citations(para: Dict[str, Any]) -> bool:
    """Check if paragraph contains legal citations"""
    text = para.get("text", "")
    
    # Citation patterns
    citation_patterns = [
        r"\(\d{4}\)\s+\d+\s+SCC\s+\d+",  # SCC citations
        r"AIR\s+\d{4}\s+\w+\s+\d+",      # AIR citations  
        r"\d{4}\s+\d+\s+SCR\s+\d+",      # SCR citations
        r"Section\s+\d+",                 # Section references
        r"Article\s+\d+",                 # Article references
        r"[Vv]\.?\s+[A-Z][^,\n]*\s*\(\d{4}\)",  # Case v. Case (year)
    ]
    
    for pattern in citation_patterns:
        if re.search(pattern, text):
            return True
    
    return False


def _create_single_chunk(paras: List[Dict[str, Any]], authority_id: str, chunk_type: str) -> Dict[str, Any]:
    """Create a single chunk from paragraphs"""
    
    if not paras:
        return {}
    
    # Combine paragraph text
    chunk_text = "\n\n".join([p.get("text", "") for p in paras])
    
    # Calculate range
    para_from = min(p.get("para_id", 0) for p in paras)
    para_to = max(p.get("para_id", 0) for p in paras)
    
    # Extract statute tags from all paragraphs
    statute_tags = set()
    has_citation = False
    
    for para in paras:
        # Simple statute detection
        text = para.get("text", "").upper()
        if "SECTION" in text and any(char.isdigit() for char in text):
            # Extract section numbers
            import re
            sections = re.findall(r'SECTION\s+(\d+[A-Z]?)', text)
            for section in sections:
                statute_tags.add(f"SEC-{section}")
        
        if "ARTICLE" in text and any(char.isdigit() for char in text):
            articles = re.findall(r'ARTICLE\s+(\d+[A-Z]?)', text)
            for article in articles:
                statute_tags.add(f"ART-{article}")
        
        # Check for citations
        if _has_citations(para):
            has_citation = True
    
    return {
        "authority_id": authority_id,
        "para_from": para_from,
        "para_to": para_to,
        "text": chunk_text,
        "tokens": get_token_count(chunk_text),
        "statute_tags": list(statute_tags),
        "has_citation": has_citation,
        "chunk_type": chunk_type,
        "paragraph_count": len(paras)
    }


