from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from eth_utils import keccak


def extract_metadata(text: str, paragraphs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract comprehensive metadata from legal document text"""
    
    # Combine first few paragraphs for header analysis
    header_text = " ".join([p.get("text", "") for p in paragraphs[:5]])
    full_text = " ".join([p.get("text", "") for p in paragraphs])
    
    metadata = {
        "court": extract_court(header_text),
        "title": extract_title(header_text),
        "neutral_cite": extract_neutral_citation(header_text),
        "reporter_cite": extract_reporter_citation(header_text),
        "date": extract_date(header_text),
        "bench": extract_bench(header_text),
        "headnote": extract_headnote(paragraphs),
        "subject_matter": extract_subject_matter(full_text),
        "statutes_cited": extract_statute_citations(full_text),
        "precedents_cited": extract_precedent_citations(full_text)
    }
    
    return {k: v for k, v in metadata.items() if v is not None}


def extract_court(text: str) -> str:
    """Identify the court from document text"""
    text_upper = text.upper()
    
    # Supreme Court patterns
    if any(pattern in text_upper for pattern in [
        "SUPREME COURT OF INDIA",
        "SUPREME COURT",
        "S.C.",
        "SC OF INDIA"
    ]):
        return "SC"
    
    # High Court patterns
    hc_patterns = [
        r"HIGH COURT OF (\w+)",
        r"(\w+) HIGH COURT",
        r"H\.?C\.? OF (\w+)",
        r"HC (\w+)"
    ]
    
    for pattern in hc_patterns:
        match = re.search(pattern, text_upper)
        if match:
            state = match.group(1) if match.groups() else "UNKNOWN"
            return f"HC-{state[:3]}"
    
    # Default patterns
    if "HIGH COURT" in text_upper:
        return "HC"
    if "TRIBUNAL" in text_upper:
        return "TRIBUNAL"
    if "COMMISSION" in text_upper:
        return "COMMISSION"
    
    return "UNKNOWN"


def extract_title(text: str) -> Optional[str]:
    """Extract case title/party names"""
    
    # Common title patterns in Indian legal documents
    title_patterns = [
        r"([A-Z][^v\n]*)\s+[Vv]\.?\s+([A-Z][^\n]*)",  # Party A v. Party B
        r"([A-Z][^Vs\n]*)\s+[Vv]s\.?\s+([A-Z][^\n]*)",  # Party A vs. Party B
        r"IN THE MATTER OF:?\s*([^\n]+)",  # In the matter of
        r"RE:?\s*([^\n]+)",  # Re: case title
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 2:
                return f"{match.group(1).strip()} v. {match.group(2).strip()}"
            else:
                return match.group(1).strip()
    
    # Fallback: extract first line that looks like a title
    lines = text.split('\n')[:10]
    for line in lines:
        line = line.strip()
        if (len(line) > 20 and len(line) < 200 and 
            any(char.isupper() for char in line) and
            not line.startswith(('CIVIL', 'CRIMINAL', 'WRIT', 'SLP'))):
            return line
    
    return None


def extract_neutral_citation(text: str) -> Optional[str]:
    """Extract neutral citation (e.g., 2020 SCC OnLine SC 123)"""
    
    # Indian neutral citation patterns
    patterns = [
        r"(\d{4})\s+SCC\s+OnLine\s+SC\s+(\d+)",
        r"(\d{4})\s+SCC\s+OnLine\s+(\w+)\s+(\d+)",
        r"(\d{4})\s+(\d+)\s+SCC\s+(\d+)",
        r"AIR\s+(\d{4})\s+SC\s+(\d+)",
        r"(\d{4})\s+\d+\s+SCR\s+(\d+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None


def extract_reporter_citation(text: str) -> Optional[str]:
    """Extract law reporter citation"""
    
    # Common Indian law reporter patterns
    patterns = [
        r"\(\d{4}\)\s+\d+\s+SCC\s+\d+",
        r"AIR\s+\d{4}\s+\w+\s+\d+",
        r"\(\d{4}\)\s+\d+\s+SCR\s+\d+",
        r"\d{4}\s+\(\d+\)\s+\w+\s+\d+"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None


def extract_date(text: str) -> Optional[datetime]:
    """Extract judgment/order date"""
    
    # Date patterns commonly found in Indian judgments
    date_patterns = [
        r"DATED:?\s*(\d{1,2})[\./-](\d{1,2})[\./-](\d{4})",
        r"(\d{1,2})[\./-](\d{1,2})[\./-](\d{4})",
        r"(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})",
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})"
    ]
    
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                groups = match.groups()
                if len(groups) == 3:
                    if groups[1].lower() in month_names:  # Month name format
                        day = int(groups[0]) if groups[0].isdigit() else int(groups[1])
                        month = month_names[groups[1].lower()] if groups[1].lower() in month_names else month_names[groups[0].lower()]
                        year = int(groups[2])
                    else:  # Numeric format
                        day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                    
                    if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2030:
                        return datetime(year, month, day)
            except (ValueError, IndexError):
                continue
    
    return None


def extract_bench(text: str) -> Optional[str]:
    """Extract bench composition"""
    
    # Patterns for bench information
    patterns = [
        r"BEFORE:?\s*([^,\n]+(?:,\s*[^,\n]+)*),?\s*JJ?\.?",
        r"CORAM:?\s*([^,\n]+(?:,\s*[^,\n]+)*),?\s*JJ?\.?",
        r"([A-Z][a-z]+,?\s*J\.?(?:\s*and\s*[A-Z][a-z]+,?\s*J\.?)*)",
        r"HON'BLE\s+([^,\n]+(?:,\s*[^,\n]+)*),?\s*JJ?\.?"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            bench = match.group(1).strip()
            # Clean up common suffixes
            bench = re.sub(r',?\s*JJ?\.?$', '', bench)
            return bench
    
    return None


def extract_headnote(paragraphs: List[Dict[str, Any]]) -> Optional[str]:
    """Extract headnote/summary from early paragraphs"""
    
    # Look for headnote in first few paragraphs
    for para in paragraphs[:10]:
        text = para.get("text", "")
        
        # Headnote indicators
        if any(indicator in text.upper() for indicator in [
            "HEADNOTE", "HELD:", "SUMMARY:", "BRIEF:", "GIST:"
        ]):
            return text
        
        # If paragraph is substantial and early, might be headnote
        if (len(text.split()) > 30 and 
            para.get("para_id", 0) <= 3 and
            not any(keyword in text.upper() for keyword in ["PETITIONER", "RESPONDENT", "APPELLANT"])):
            return text
    
    return None


def extract_subject_matter(text: str) -> List[str]:
    """Extract areas of law/subject matter"""
    
    subject_keywords = {
        "constitutional": ["constitution", "fundamental rights", "directive principles", "article"],
        "criminal": ["criminal", "ipc", "crpc", "bail", "murder", "theft", "fraud"],
        "civil": ["civil", "cpc", "contract", "tort", "property", "damages"],
        "corporate": ["company", "corporate", "directors", "shareholders", "sebi"],
        "taxation": ["income tax", "gst", "customs", "excise", "tax"],
        "labour": ["labour", "employment", "industrial", "workmen", "wages"],
        "family": ["marriage", "divorce", "custody", "maintenance", "succession"],
        "property": ["property", "land", "real estate", "acquisition", "title"],
        "intellectual_property": ["patent", "trademark", "copyright", "ip"],
        "environmental": ["environment", "pollution", "forest", "mining"]
    }
    
    subjects = []
    text_lower = text.lower()
    
    for subject, keywords in subject_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            subjects.append(subject)
    
    return subjects


def extract_statute_citations(text: str) -> List[str]:
    """Extract statute and section references"""
    
    # Common Indian statute patterns
    patterns = [
        r"Section\s+(\d+[A-Z]?)\s+of\s+([^,\n\.]+)",
        r"Article\s+(\d+[A-Z]?)\s+of\s+([^,\n\.]+)",
        r"(IPC|CrPC|CPC|Evidence Act|Contract Act)\s+[Ss]ection\s+(\d+[A-Z]?)",
        r"(\w+\s+Act,?\s+\d{4})",
        r"Rule\s+(\d+[A-Z]?)\s+of\s+([^,\n\.]+)"
    ]
    
    statutes = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            statutes.append(match.group(0))
    
    return list(set(statutes))  # Remove duplicates


def extract_precedent_citations(text: str) -> List[str]:
    """Extract case law citations"""
    
    # Case citation patterns
    patterns = [
        r"([A-Z][^v\n]*)\s+[Vv]\.?\s+([A-Z][^\n,\.]*),?\s*(?:\(\d{4}\)|\d{4})\s*\d*\s*\w+\s*\d+",
        r"AIR\s+\d{4}\s+\w+\s+\d+",
        r"\(\d{4}\)\s+\d+\s+SCC\s+\d+",
        r"\d{4}\s+\d+\s+SCR\s+\d+"
    ]
    
    precedents = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            precedents.append(match.group(0))
    
    return list(set(precedents))  # Remove duplicates


def compute_document_hash(text: str) -> str:
    """Compute keccak256 hash of canonical document text"""
    # Normalize text for consistent hashing
    canonical = " ".join(text.split()).strip().lower()
    hash_bytes = keccak(text=canonical)
    return hash_bytes.hex()


def split_paragraphs(text: str) -> List[str]:
    """Simple paragraph split - legacy function"""
    return [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]


