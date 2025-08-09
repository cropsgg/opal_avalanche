from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple
import structlog

from openai import OpenAI
from app.core.config import get_settings

log = structlog.get_logger()


class PrecedentVerifyResult:
    def __init__(self, valid: bool, confidence: float, flags: List[str], details: Dict[str, Any]):
        self.valid = valid
        self.confidence = confidence
        self.flags = flags
        self.details = details


async def verify_precedent_conflicts(answer: str, sources: List[Dict[str, Any]], 
                                   retrieval_set: List[Dict[str, Any]]) -> PrecedentVerifyResult:
    """
    Verify precedents for conflicts, overruling, and proper hierarchical application
    """
    
    log.info("precedent_verify.start", answer_length=len(answer), sources_count=len(sources))
    
    # Extract case citations from answer
    case_citations = _extract_case_citations(answer)
    
    # Analyze precedent hierarchy 
    hierarchy_analysis = _analyze_precedent_hierarchy(sources, retrieval_set)
    
    # Detect explicit conflict indicators
    conflict_indicators = _detect_conflict_indicators(answer, retrieval_set)
    
    # Check for overruling/distinguishing patterns
    overruling_analysis = _check_overruling_patterns(case_citations, retrieval_set)
    
    # Verify binding vs persuasive authority usage
    authority_verification = _verify_authority_usage(answer, hierarchy_analysis)
    
    # Check Supreme Court precedent compliance
    sc_compliance = _check_supreme_court_compliance(hierarchy_analysis, conflict_indicators)
    
    # Calculate overall validity
    valid, confidence, flags = _calculate_precedent_validity(
        hierarchy_analysis, conflict_indicators, overruling_analysis, 
        authority_verification, sc_compliance
    )
    
    details = {
        "case_citations": case_citations,
        "hierarchy_analysis": hierarchy_analysis,
        "conflict_indicators": conflict_indicators,
        "overruling_analysis": overruling_analysis,
        "authority_verification": authority_verification,
        "sc_compliance": sc_compliance
    }
    
    log.info("precedent_verify.complete", 
            valid=valid, 
            confidence=confidence, 
            flags_count=len(flags),
            citations_found=len(case_citations))
    
    return PrecedentVerifyResult(valid, confidence, flags, details)


def _extract_case_citations(answer: str) -> List[Dict[str, Any]]:
    """Extract case citations from the answer text"""
    
    citations = []
    
    # Patterns for Indian case citations
    citation_patterns = [
        # Supreme Court patterns
        (r'(\w+(?:\s+\w+)*)\s+v\.?\s+(\w+(?:\s+\w+)*)\s*\(\d{4}\)\s*\d+\s*SCC\s*\d+', 'scc_citation'),
        (r'(\w+(?:\s+\w+)*)\s+v\.?\s+(\w+(?:\s+\w+)*)\s*\(\d{4}\)\s*\d+\s*SCR\s*\d+', 'scr_citation'),
        (r'(\w+(?:\s+\w+)*)\s+v\.?\s+(\w+(?:\s+\w+)*)\s*AIR\s*\d{4}\s*SC\s*\d+', 'air_sc_citation'),
        
        # High Court patterns  
        (r'(\w+(?:\s+\w+)*)\s+v\.?\s+(\w+(?:\s+\w+)*)\s*AIR\s*\d{4}\s*[A-Z]{2,4}\s*\d+', 'air_hc_citation'),
        (r'(\w+(?:\s+\w+)*)\s+v\.?\s+(\w+(?:\s+\w+)*)\s*\(\d{4}\)\s*\d+\s*[A-Z]{2,4}[CJ]?\s*\d+', 'hc_citation'),
        
        # Neutral citations
        (r'(\w+(?:\s+\w+)*)\s+v\.?\s+(\w+(?:\s+\w+)*)\s*\d{4}\s*SCC\s*OnLine\s*SC\s*\d+', 'neutral_sc'),
        (r'(\w+(?:\s+\w+)*)\s+v\.?\s+(\w+(?:\s+\w+)*)\s*\d{4}\s*SCC\s*OnLine\s*[A-Z]{2,4}\s*\d+', 'neutral_hc'),
        
        # Case name only patterns
        (r'(?:In\s+)?(\w+(?:\s+\w+)*)\s+v\.?\s+(\w+(?:\s+\w+)*)', 'case_name_only')
    ]
    
    for pattern, citation_type in citation_patterns:
        matches = re.finditer(pattern, answer, re.IGNORECASE)
        for match in matches:
            citation = {
                "text": match.group(0),
                "type": citation_type,
                "position": match.span(),
                "petitioner": match.group(1).strip(),
                "respondent": match.group(2).strip()
            }
            
            # Determine court level from citation type
            if 'sc' in citation_type or 'SCC' in match.group(0):
                citation["court_level"] = "SC"
            elif 'hc' in citation_type or 'HC' in match.group(0):
                citation["court_level"] = "HC"
            else:
                citation["court_level"] = "UNKNOWN"
            
            citations.append(citation)
    
    return citations


def _analyze_precedent_hierarchy(sources: List[Dict[str, Any]], 
                                retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the precedent hierarchy in the sources"""
    
    court_hierarchy = {
        "SC": {"level": 1, "binding_on": ["HC", "TRIBUNAL", "DISTRICT"], "cases": []},
        "HC": {"level": 2, "binding_on": ["TRIBUNAL", "DISTRICT"], "cases": []},
        "HC-DEL": {"level": 2, "binding_on": ["TRIBUNAL", "DISTRICT"], "cases": []},
        "HC-BOM": {"level": 2, "binding_on": ["TRIBUNAL", "DISTRICT"], "cases": []},
        "HC-CAL": {"level": 2, "binding_on": ["TRIBUNAL", "DISTRICT"], "cases": []},
        "HC-MAD": {"level": 2, "binding_on": ["TRIBUNAL", "DISTRICT"], "cases": []},
        "TRIBUNAL": {"level": 3, "binding_on": [], "cases": []},
        "DISTRICT": {"level": 4, "binding_on": [], "cases": []}
    }
    
    for item in retrieval_set:
        court = item.get("court", "UNKNOWN")
        title = item.get("title", "")
        
        if court in court_hierarchy:
            court_hierarchy[court]["cases"].append({
                "title": title,
                "authority_id": item.get("authority_id"),
                "date": item.get("date"),
                "neutral_cite": item.get("neutral_cite"),
                "reporter_cite": item.get("reporter_cite")
            })
        elif court.startswith("HC-"):
            if court not in court_hierarchy:
                court_hierarchy[court] = {"level": 2, "binding_on": ["TRIBUNAL", "DISTRICT"], "cases": []}
            court_hierarchy[court]["cases"].append({
                "title": title,
                "authority_id": item.get("authority_id"),
                "date": item.get("date")
            })
    
    # Calculate hierarchy statistics
    sc_count = len(court_hierarchy["SC"]["cases"])
    hc_count = sum(len(court["cases"]) for court, data in court_hierarchy.items() 
                   if data["level"] == 2)
    tribunal_count = len(court_hierarchy["TRIBUNAL"]["cases"])
    
    return {
        "court_hierarchy": court_hierarchy,
        "sc_count": sc_count,
        "hc_count": hc_count,
        "tribunal_count": tribunal_count,
        "hierarchy_score": _calculate_hierarchy_score(sc_count, hc_count, tribunal_count)
    }


def _calculate_hierarchy_score(sc_count: int, hc_count: int, tribunal_count: int) -> float:
    """Calculate a score based on precedent hierarchy quality"""
    
    # Higher score for more Supreme Court precedents
    score = 0.5  # Base score
    
    if sc_count > 0:
        score += min(0.3, sc_count * 0.1)  # Up to 0.3 boost for SC cases
    
    if hc_count > 0:
        score += min(0.15, hc_count * 0.03)  # Up to 0.15 boost for HC cases
    
    if tribunal_count > 0:
        score += min(0.05, tribunal_count * 0.01)  # Small boost for tribunal cases
    
    return min(1.0, score)


def _detect_conflict_indicators(answer: str, retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detect indicators of precedent conflicts"""
    
    conflict_keywords = [
        "overrule", "overruled", "overruling",
        "distinguish", "distinguished", "distinguishable",
        "not follow", "not followed", "decline to follow",
        "differ", "differs", "different view",
        "contrary", "inconsistent", "conflict", "conflicting",
        "doubt", "doubted", "questionable",
        "disapprove", "disapproved"
    ]
    
    answer_lower = answer.lower()
    conflicts_in_answer = []
    
    for keyword in conflict_keywords:
        if keyword in answer_lower:
            conflicts_in_answer.append({
                "keyword": keyword,
                "context": _extract_context(answer, keyword, 50)
            })
    
    # Check sources for conflict indicators
    conflicts_in_sources = []
    for item in retrieval_set:
        title = item.get("title", "").lower()
        for keyword in conflict_keywords:
            if keyword in title:
                conflicts_in_sources.append({
                    "keyword": keyword,
                    "title": item.get("title", ""),
                    "authority_id": item.get("authority_id"),
                    "court": item.get("court", "")
                })
                break
    
    return {
        "conflicts_in_answer": conflicts_in_answer,
        "conflicts_in_sources": conflicts_in_sources,
        "total_conflicts": len(conflicts_in_answer) + len(conflicts_in_sources),
        "conflict_score": 1.0 - min(0.5, (len(conflicts_in_answer) + len(conflicts_in_sources)) * 0.1)
    }


def _extract_context(text: str, keyword: str, context_length: int) -> str:
    """Extract context around a keyword"""
    
    pos = text.lower().find(keyword.lower())
    if pos == -1:
        return ""
    
    start = max(0, pos - context_length)
    end = min(len(text), pos + len(keyword) + context_length)
    
    return text[start:end].strip()


def _check_overruling_patterns(case_citations: List[Dict[str, Any]], 
                              retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check for patterns indicating cases have been overruled"""
    
    overruling_patterns = []
    
    for citation in case_citations:
        petitioner = citation.get("petitioner", "").lower()
        respondent = citation.get("respondent", "").lower()
        
        # Look for this case in sources with overruling indicators
        for item in retrieval_set:
            title = item.get("title", "").lower()
            
            # Check if this case appears with overruling language
            if (petitioner in title and respondent in title):
                overruling_keywords = ["overruled", "not good law", "no longer valid"]
                for keyword in overruling_keywords:
                    if keyword in title:
                        overruling_patterns.append({
                            "citation": citation,
                            "overruling_authority": item.get("title", ""),
                            "overruling_court": item.get("court", ""),
                            "keyword": keyword
                        })
                        break
    
    return {
        "overruled_cases": overruling_patterns,
        "overruling_count": len(overruling_patterns),
        "overruling_risk": len(overruling_patterns) / max(1, len(case_citations))
    }


def _verify_authority_usage(answer: str, hierarchy_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Verify proper usage of binding vs persuasive authority"""
    
    answer_lower = answer.lower()
    
    # Check for proper authority language
    binding_indicators = ["binding", "must follow", "bound by", "binding precedent"]
    persuasive_indicators = ["persuasive", "guidance", "instructive", "helpful"]
    
    binding_mentions = sum(1 for indicator in binding_indicators if indicator in answer_lower)
    persuasive_mentions = sum(1 for indicator in persuasive_indicators if indicator in answer_lower)
    
    # Check if SC precedents are treated as binding
    sc_count = hierarchy_analysis["sc_count"]
    sc_binding_score = 1.0 if sc_count == 0 or binding_mentions > 0 else 0.7
    
    return {
        "binding_mentions": binding_mentions,
        "persuasive_mentions": persuasive_mentions,
        "sc_binding_score": sc_binding_score,
        "authority_usage_score": min(1.0, (binding_mentions + persuasive_mentions) * 0.2 + 0.6)
    }


def _check_supreme_court_compliance(hierarchy_analysis: Dict[str, Any], 
                                   conflict_indicators: Dict[str, Any]) -> Dict[str, Any]:
    """Check compliance with Supreme Court precedents"""
    
    sc_cases = hierarchy_analysis["court_hierarchy"]["SC"]["cases"]
    
    if not sc_cases:
        return {"compliant": True, "score": 1.0, "reason": "no_sc_precedents"}
    
    # Check if there are conflicts involving SC precedents
    sc_conflicts = 0
    for conflict in conflict_indicators["conflicts_in_sources"]:
        if conflict["court"] == "SC":
            sc_conflicts += 1
    
    # SC precedents should not be in conflict
    compliance_score = 1.0 - (sc_conflicts * 0.3)
    compliant = sc_conflicts == 0
    
    return {
        "compliant": compliant,
        "score": max(0.0, compliance_score),
        "sc_conflicts": sc_conflicts,
        "sc_cases_count": len(sc_cases)
    }


def _calculate_precedent_validity(hierarchy_analysis: Dict[str, Any], 
                                 conflict_indicators: Dict[str, Any],
                                 overruling_analysis: Dict[str, Any],
                                 authority_verification: Dict[str, Any],
                                 sc_compliance: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """Calculate overall precedent validity and confidence"""
    
    flags = []
    
    # Check hierarchy quality
    hierarchy_score = hierarchy_analysis["hierarchy_score"]
    if hierarchy_score < 0.6:
        flags.append("weak_precedent_hierarchy")
    
    # Check conflicts
    conflict_score = conflict_indicators["conflict_score"]
    if conflict_indicators["total_conflicts"] > 0:
        flags.append("precedent_conflicts_detected")
    
    # Check overruling
    overruling_risk = overruling_analysis["overruling_risk"]
    if overruling_risk > 0.2:
        flags.append("overruled_precedents_cited")
    
    # Check authority usage
    authority_score = authority_verification["authority_usage_score"]
    if authority_score < 0.7:
        flags.append("improper_authority_usage")
    
    # Check SC compliance
    if not sc_compliance["compliant"]:
        flags.append("supreme_court_non_compliance")
    
    # Calculate overall confidence
    weights = {
        "hierarchy": 0.25,
        "conflicts": 0.25,
        "overruling": 0.2,
        "authority": 0.15,
        "sc_compliance": 0.15
    }
    
    overall_confidence = (
        hierarchy_score * weights["hierarchy"] +
        conflict_score * weights["conflicts"] +
        (1.0 - overruling_risk) * weights["overruling"] +
        authority_score * weights["authority"] +
        sc_compliance["score"] * weights["sc_compliance"]
    )
    
    # Determine validity
    valid = (
        hierarchy_score >= 0.5 and
        conflict_indicators["total_conflicts"] <= 1 and
        overruling_risk <= 0.3 and
        sc_compliance["compliant"]
    )
    
    return valid, overall_confidence, flags
