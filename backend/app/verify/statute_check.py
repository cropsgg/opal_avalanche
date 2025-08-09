from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple
import structlog

from openai import OpenAI
from app.core.config import get_settings

log = structlog.get_logger()


class StatuteVerifyResult:
    def __init__(self, valid: bool, confidence: float, flags: List[str], details: Dict[str, Any]):
        self.valid = valid
        self.confidence = confidence
        self.flags = flags
        self.details = details


async def verify_statute_alignment(answer: str, sources: List[Dict[str, Any]], 
                                  retrieval_set: List[Dict[str, Any]]) -> StatuteVerifyResult:
    """
    Verify that statutory citations in the answer are accurate and properly aligned
    with the source material
    """
    
    log.info("statute_verify.start", answer_length=len(answer), sources_count=len(sources))
    
    # Extract statutory citations from answer
    answer_citations = _extract_statutory_citations(answer)
    
    # Verify citations exist in sources
    citation_verification = await _verify_citations_in_sources(answer_citations, sources, retrieval_set)
    
    # Check section number accuracy
    section_accuracy = _verify_section_numbers(answer_citations, sources, retrieval_set)
    
    # Verify interpretation accuracy
    interpretation_accuracy = await _verify_statutory_interpretation(answer, answer_citations, sources)
    
    # Calculate overall validity and confidence
    valid, confidence, flags = _calculate_statute_validity(
        citation_verification, section_accuracy, interpretation_accuracy
    )
    
    details = {
        "answer_citations": answer_citations,
        "citation_verification": citation_verification,
        "section_accuracy": section_accuracy,
        "interpretation_accuracy": interpretation_accuracy,
        "total_citations_checked": len(answer_citations)
    }
    
    log.info("statute_verify.complete", 
            valid=valid, 
            confidence=confidence, 
            flags_count=len(flags),
            citations_found=len(answer_citations))
    
    return StatuteVerifyResult(valid, confidence, flags, details)


def _extract_statutory_citations(answer: str) -> List[Dict[str, Any]]:
    """Extract statutory citations from the answer text"""
    
    citations = []
    
    # Patterns for Indian statutory citations
    citation_patterns = [
        # Section patterns
        (r'[Ss]ection\s+(\d+[A-Z]?)\s+of\s+(?:the\s+)?([^,\.\n]+)', 'section_with_act'),
        (r'[Ss]ection\s+(\d+[A-Z]?)', 'section_only'),
        (r'[Ss]ec\.\s*(\d+[A-Z]?)', 'section_abbreviated'),
        
        # Article patterns (Constitution)
        (r'[Aa]rticle\s+(\d+[A-Z]?)\s+of\s+(?:the\s+)?Constitution', 'constitutional_article'),
        (r'[Aa]rticle\s+(\d+[A-Z]?)', 'article_only'),
        
        # Specific acts
        (r'(?:Section\s+)?(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?Indian\s+Penal\s+Code|IPC', 'ipc_section'),
        (r'(?:Section\s+)?(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?Code\s+of\s+Criminal\s+Procedure|CrPC', 'crpc_section'),
        (r'(?:Section\s+)?(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?Code\s+of\s+Civil\s+Procedure|CPC', 'cpc_section'),
        
        # Order and Rule patterns
        (r'Order\s+([IVX]+)\s+Rule\s+(\d+)', 'order_rule'),
        (r'Rule\s+(\d+)', 'rule_only'),
        
        # Schedule patterns
        (r'Schedule\s+([IVX]+)', 'schedule'),
        (r'(?:First|Second|Third|Fourth|Fifth)\s+Schedule', 'schedule_ordinal')
    ]
    
    for pattern, citation_type in citation_patterns:
        matches = re.finditer(pattern, answer, re.IGNORECASE)
        for match in matches:
            citation = {
                "text": match.group(0),
                "type": citation_type,
                "position": match.span(),
                "groups": match.groups()
            }
            
            # Extract section number and act name based on pattern
            if citation_type == 'section_with_act':
                citation["section"] = match.group(1)
                citation["act"] = match.group(2).strip()
            elif citation_type in ['section_only', 'section_abbreviated']:
                citation["section"] = match.group(1)
            elif citation_type == 'constitutional_article':
                citation["article"] = match.group(1)
                citation["act"] = "Constitution of India"
            elif citation_type == 'article_only':
                citation["article"] = match.group(1)
            elif citation_type in ['ipc_section', 'crpc_section', 'cpc_section']:
                citation["section"] = match.group(1)
                citation["act"] = {
                    'ipc_section': 'Indian Penal Code',
                    'crpc_section': 'Code of Criminal Procedure', 
                    'cpc_section': 'Code of Civil Procedure'
                }[citation_type]
            elif citation_type == 'order_rule':
                citation["order"] = match.group(1)
                citation["rule"] = match.group(2)
            
            citations.append(citation)
    
    return citations


async def _verify_citations_in_sources(citations: List[Dict[str, Any]], 
                                     sources: List[Dict[str, Any]], 
                                     retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify that cited statutes actually exist in the source material"""
    
    verification_results = []
    
    for citation in citations:
        citation_text = citation["text"].lower()
        section = citation.get("section", "")
        act = citation.get("act", "")
        
        found_in_sources = False
        matching_sources = []
        
        # Check in retrieval set for exact matches
        for item in retrieval_set:
            item_text = item.get("text", "").lower()
            
            # Look for exact citation match
            if citation_text in item_text:
                found_in_sources = True
                matching_sources.append({
                    "authority_id": item.get("authority_id"),
                    "match_type": "exact_text",
                    "confidence": 0.95
                })
                continue
            
            # Look for section number and act combination
            if section and act:
                if section in item_text and act.lower() in item_text:
                    found_in_sources = True
                    matching_sources.append({
                        "authority_id": item.get("authority_id"),
                        "match_type": "section_and_act",
                        "confidence": 0.8
                    })
                    continue
            
            # Look for just section number if act not specified
            if section and not act:
                if f"section {section}" in item_text or f"sec. {section}" in item_text:
                    found_in_sources = True
                    matching_sources.append({
                        "authority_id": item.get("authority_id"),
                        "match_type": "section_only",
                        "confidence": 0.6
                    })
        
        verification_results.append({
            "citation": citation,
            "found": found_in_sources,
            "sources": matching_sources,
            "confidence": max([s["confidence"] for s in matching_sources], default=0.0)
        })
    
    total_citations = len(citations)
    verified_citations = sum(1 for r in verification_results if r["found"])
    verification_rate = verified_citations / total_citations if total_citations > 0 else 1.0
    
    return {
        "verification_rate": verification_rate,
        "total_citations": total_citations,
        "verified_citations": verified_citations,
        "results": verification_results
    }


def _verify_section_numbers(citations: List[Dict[str, Any]], 
                           sources: List[Dict[str, Any]], 
                           retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify that section numbers cited are accurate and current"""
    
    accuracy_results = []
    
    for citation in citations:
        section = citation.get("section", "")
        act = citation.get("act", "")
        
        if not section:
            continue
        
        # Check for common section number errors
        errors = []
        warnings = []
        
        # Check for impossible section numbers
        try:
            section_num = int(re.sub(r'[A-Z]', '', section))
            if section_num > 1000:  # Most acts don't have >1000 sections
                warnings.append("unusually_high_section_number")
            if section_num == 0:
                errors.append("invalid_section_zero")
        except ValueError:
            pass
        
        # Check for known repealed sections (examples)
        repealed_sections = {
            "Indian Penal Code": ["303"],  # Section 303 was struck down
            "Code of Criminal Procedure": ["562"]  # Example repealed section
        }
        
        if act in repealed_sections and section in repealed_sections[act]:
            errors.append("repealed_section")
        
        # Check for amendment indicators in sources
        amendment_found = False
        for item in retrieval_set:
            item_text = item.get("text", "").lower()
            if section in item_text and any(word in item_text for word in ["amended", "substituted", "repealed"]):
                amendment_found = True
                warnings.append("section_amendment_mentioned")
                break
        
        accuracy_results.append({
            "citation": citation,
            "errors": errors,
            "warnings": warnings,
            "amendment_found": amendment_found
        })
    
    total_errors = sum(len(r["errors"]) for r in accuracy_results)
    total_warnings = sum(len(r["warnings"]) for r in accuracy_results)
    
    return {
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "results": accuracy_results,
        "accuracy_score": 1.0 - (total_errors * 0.3 + total_warnings * 0.1)
    }


async def _verify_statutory_interpretation(answer: str, citations: List[Dict[str, Any]], 
                                         sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify that the interpretation of statutes is accurate"""
    
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        return {"interpretation_score": 0.7, "verified": True, "method": "basic"}
    
    if not citations:
        return {"interpretation_score": 1.0, "verified": True, "method": "no_citations"}
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build verification prompt
        citations_text = "\n".join([f"- {c['text']}" for c in citations[:5]])
        
        prompt = f"""Verify the statutory interpretation accuracy in this legal analysis.

Answer: {answer[:800]}

Statutory Citations Found: 
{citations_text}

Check for:
1. Accurate representation of statutory language
2. Correct interpretation of legal provisions
3. Proper application of statutory tests/requirements
4. No misstatement of law

Rate accuracy from 0.0 to 1.0 and provide brief explanation.
Format: SCORE:0.X|EXPLANATION:reason"""

        response = client.chat.completions.create(
            model=settings.OPENAI_VERIFY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse response
        if "|" in content:
            score_part, explanation_part = content.split("|", 1)
            score = float(re.search(r'(\d\.\d+|\d)', score_part).group(1))
            explanation = explanation_part.replace("EXPLANATION:", "").strip()
        else:
            score = 0.7  # Default if parsing fails
            explanation = content
        
        return {
            "interpretation_score": max(0.0, min(1.0, score)),
            "explanation": explanation,
            "verified": True,
            "method": "llm_verification"
        }
        
    except Exception as e:
        log.error("statute_verify.interpretation_error", error=str(e))
        return {
            "interpretation_score": 0.6,
            "verified": False,
            "error": str(e),
            "method": "fallback"
        }


def _calculate_statute_validity(citation_verification: Dict[str, Any], 
                               section_accuracy: Dict[str, Any], 
                               interpretation_accuracy: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """Calculate overall validity and confidence for statute verification"""
    
    flags = []
    
    # Citation verification score
    citation_score = citation_verification["verification_rate"]
    if citation_score < 0.8:
        flags.append("unverified_statutory_citations")
    
    # Section accuracy score
    accuracy_score = section_accuracy["accuracy_score"]
    if section_accuracy["total_errors"] > 0:
        flags.append("statutory_errors_detected")
    if section_accuracy["total_warnings"] > 0:
        flags.append("statutory_warnings")
    
    # Interpretation accuracy score
    interpretation_score = interpretation_accuracy["interpretation_score"]
    if interpretation_score < 0.7:
        flags.append("questionable_statutory_interpretation")
    
    # Calculate overall confidence
    weights = {
        "citation": 0.4,
        "accuracy": 0.3,
        "interpretation": 0.3
    }
    
    overall_confidence = (
        citation_score * weights["citation"] +
        accuracy_score * weights["accuracy"] +
        interpretation_score * weights["interpretation"]
    )
    
    # Determine validity
    valid = (
        citation_score >= 0.7 and
        section_accuracy["total_errors"] == 0 and
        interpretation_score >= 0.6
    )
    
    return valid, overall_confidence, flags
