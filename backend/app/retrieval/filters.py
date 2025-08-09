from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import structlog

log = structlog.get_logger()

# Legacy function
def apply_filters(packs: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """MVP: no-op - legacy function"""
    return packs


def validate_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize filter parameters
    Returns sanitized filters dict
    """
    
    validated = {}
    
    # Court filter - must be valid court codes
    if "court" in filters:
        court = filters["court"]
        if isinstance(court, str):
            court = [court]
        
        valid_courts = []
        for c in court:
            if isinstance(c, str) and c.upper() in VALID_COURTS:
                valid_courts.append(c.upper())
        
        if valid_courts:
            validated["court"] = valid_courts
    
    # Year filter - must be reasonable year range
    if "year" in filters:
        year_filter = filters["year"]
        
        if isinstance(year_filter, int):
            if 1900 <= year_filter <= datetime.now().year:
                validated["year"] = year_filter
        elif isinstance(year_filter, dict):
            year_range = {}
            if "from" in year_filter and isinstance(year_filter["from"], int):
                if 1900 <= year_filter["from"] <= datetime.now().year:
                    year_range["from"] = year_filter["from"]
            if "to" in year_filter and isinstance(year_filter["to"], int):
                if 1900 <= year_filter["to"] <= datetime.now().year:
                    year_range["to"] = year_filter["to"]
            
            if year_range:
                validated["year"] = year_range
    
    # Judge filter - string matching
    if "judge" in filters and isinstance(filters["judge"], str):
        judge_name = filters["judge"].strip()
        if judge_name and len(judge_name) >= 2:
            validated["judge"] = judge_name
    
    # Statute tags filter
    if "statute_tags" in filters:
        tags = filters["statute_tags"]
        if isinstance(tags, str):
            tags = [tags]
        
        valid_tags = []
        for tag in tags:
            if isinstance(tag, str) and tag.strip():
                # Normalize statute tag format
                normalized_tag = _normalize_statute_tag(tag.strip())
                if normalized_tag:
                    valid_tags.append(normalized_tag)
        
        if valid_tags:
            validated["statute_tags"] = valid_tags
    
    # Citation requirement filter
    if "has_citation" in filters:
        if isinstance(filters["has_citation"], bool):
            validated["has_citation"] = filters["has_citation"]
    
    # Chunk type filter
    if "chunk_type" in filters:
        chunk_type = filters["chunk_type"]
        if chunk_type in VALID_CHUNK_TYPES:
            validated["chunk_type"] = chunk_type
    
    log.debug("filters.validated", 
             original_count=len(filters),
             validated_count=len(validated))
    
    return validated


def build_qdrant_filters(validated_filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convert validated filters to Qdrant filter format
    Returns Qdrant filter dict or None
    """
    
    if not validated_filters:
        return None
    
    must_conditions = []
    
    # Court filter
    if "court" in validated_filters:
        courts = validated_filters["court"]
        must_conditions.append({
            "key": "court",
            "match": {"any": courts}
        })
    
    # Year filter
    if "year" in validated_filters:
        year_filter = validated_filters["year"]
        if isinstance(year_filter, int):
            # Exact year match
            must_conditions.append({
                "key": "year",
                "match": {"value": year_filter}
            })
        elif isinstance(year_filter, dict):
            # Year range
            range_condition = {}
            if "from" in year_filter:
                range_condition["gte"] = year_filter["from"]
            if "to" in year_filter:
                range_condition["lte"] = year_filter["to"]
            
            if range_condition:
                must_conditions.append({
                    "key": "year",
                    "range": range_condition
                })
    
    # Judge filter (partial string match)
    if "judge" in validated_filters:
        judge_name = validated_filters["judge"]
        must_conditions.append({
            "key": "judge",
            "match": {"text": judge_name}
        })
    
    # Statute tags filter
    if "statute_tags" in validated_filters:
        tags = validated_filters["statute_tags"]
        must_conditions.append({
            "key": "statute_tags",
            "match": {"any": tags}
        })
    
    # Citation requirement filter
    if "has_citation" in validated_filters:
        must_conditions.append({
            "key": "has_citation",
            "match": {"value": validated_filters["has_citation"]}
        })
    
    # Chunk type filter
    if "chunk_type" in validated_filters:
        must_conditions.append({
            "key": "chunk_type",
            "match": {"value": validated_filters["chunk_type"]}
        })
    
    if not must_conditions:
        return None
    
    return {"must": must_conditions}


def _normalize_statute_tag(tag: str) -> Optional[str]:
    """Normalize statute tag to standard format"""
    
    tag = tag.upper().strip()
    
    # Handle section references
    if "SECTION" in tag or "SEC" in tag:
        import re
        # Extract section number
        section_match = re.search(r'(\d+[A-Z]?)', tag)
        if section_match:
            return f"SEC-{section_match.group(1)}"
    
    # Handle article references
    if "ARTICLE" in tag or "ART" in tag:
        import re
        article_match = re.search(r'(\d+[A-Z]?)', tag)
        if article_match:
            return f"ART-{article_match.group(1)}"
    
    # Handle act references
    if "ACT" in tag:
        # Common Indian acts
        act_mappings = {
            "IPC": "IPC",
            "CRPC": "CRPC", 
            "CPC": "CPC",
            "EVIDENCE": "EVIDENCE-ACT",
            "CONTRACT": "CONTRACT-ACT"
        }
        
        for key, value in act_mappings.items():
            if key in tag:
                return value
    
    # If already in normalized format, return as is
    if re.match(r'^(SEC|ART|IPC|CRPC|CPC)-\w+', tag):
        return tag
    
    return None


# Constants for validation
VALID_COURTS = {
    "SC",           # Supreme Court
    "HC-DEL",       # Delhi High Court
    "HC-BOM",       # Bombay High Court
    "HC-MAD",       # Madras High Court
    "HC-CAL",       # Calcutta High Court
    "HC-KAR",       # Karnataka High Court
    "HC-KER",       # Kerala High Court
    "HC-AP",        # Andhra Pradesh High Court
    "HC-TEL",       # Telangana High Court
    "HC-RAJ",       # Rajasthan High Court
    "HC-GUJ",       # Gujarat High Court
    "HC-MP",        # Madhya Pradesh High Court
    "HC-CHA",       # Chhattisgarh High Court
    "HC-ORI",       # Orissa High Court
    "HC-JHA",       # Jharkhand High Court
    "HC-BIH",       # Patna High Court
    "HC-ALL",       # Allahabad High Court
    "HC-UTT",       # Uttarakhand High Court
    "HC-HP",        # Himachal Pradesh High Court
    "HC-J&K",       # Jammu & Kashmir High Court
    "HC-PUN",       # Punjab & Haryana High Court
    "HC-SIK",       # Sikkim High Court
    "HC-TRI",       # Tripura High Court
    "HC-MAN",       # Manipur High Court
    "HC-MEG",       # Meghalaya High Court
    "HC-GAU",       # Gauhati High Court
    "TRIBUNAL",     # Various Tribunals
    "COMMISSION"    # Various Commissions
}

VALID_CHUNK_TYPES = {
    "content",          # Regular content chunks
    "headnote",         # Headnote/summary chunks
    "citation_context"  # Citation context chunks
}


