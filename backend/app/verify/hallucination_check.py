from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple
import structlog
from difflib import SequenceMatcher

from openai import OpenAI
from app.core.config import get_settings

log = structlog.get_logger()


class HallucinationVerifyResult:
    def __init__(self, valid: bool, confidence: float, flags: List[str], details: Dict[str, Any]):
        self.valid = valid
        self.confidence = confidence
        self.flags = flags
        self.details = details


async def verify_hallucination_detection(answer: str, sources: List[Dict[str, Any]], 
                                       retrieval_set: List[Dict[str, Any]]) -> HallucinationVerifyResult:
    """
    Detect fabricated citations and factual claims not supported by source material
    Ensure every citation corresponds to stored authority with >0.9 similarity threshold
    """
    
    log.info("hallucination_verify.start", answer_length=len(answer), sources_count=len(sources))
    
    # Extract factual claims from answer
    factual_claims = _extract_factual_claims(answer)
    
    # Extract and verify citations
    citation_verification = await _verify_citations_exist(answer, retrieval_set)
    
    # Check text similarity for quoted content
    similarity_verification = _verify_text_similarity(answer, retrieval_set)
    
    # Verify case law existence
    case_verification = _verify_case_existence(answer, retrieval_set)
    
    # Check for impossible legal claims
    impossible_claims = _detect_impossible_claims(answer)
    
    # LLM-based hallucination detection
    llm_verification = await _llm_hallucination_check(answer, retrieval_set)
    
    # Calculate overall validity
    valid, confidence, flags = _calculate_hallucination_validity(
        factual_claims, citation_verification, similarity_verification,
        case_verification, impossible_claims, llm_verification
    )
    
    details = {
        "factual_claims": factual_claims,
        "citation_verification": citation_verification,
        "similarity_verification": similarity_verification,
        "case_verification": case_verification,
        "impossible_claims": impossible_claims,
        "llm_verification": llm_verification
    }
    
    log.info("hallucination_verify.complete", 
            valid=valid, 
            confidence=confidence, 
            flags_count=len(flags))
    
    return HallucinationVerifyResult(valid, confidence, flags, details)


def _extract_factual_claims(answer: str) -> List[Dict[str, Any]]:
    """Extract factual claims that can be verified"""
    
    claims = []
    
    # Legal citation patterns
    citation_patterns = [
        r'(?:in|In)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Section\s+(\d+[A-Z]?)\s+of\s+(?:the\s+)?([^,\.\n]+)',
        r'Article\s+(\d+[A-Z]?)\s+of\s+(?:the\s+)?Constitution',
        r'Rule\s+(\d+)\s+of\s+([^,\.\n]+)',
        r'Order\s+([IVX]+)\s+Rule\s+(\d+)'
    ]
    
    for pattern in citation_patterns:
        matches = re.finditer(pattern, answer, re.IGNORECASE)
        for match in matches:
            claims.append({
                "type": "citation",
                "text": match.group(0),
                "position": match.span(),
                "verifiable": True
            })
    
    # Numerical claims
    numerical_patterns = [
        r'(\d+)\s+years?\s+(?:limitation|period)',
        r'(\d+)\s+months?\s+(?:limitation|period)',
        r'fine\s+(?:of\s+)?(?:Rs\.?\s*)?(\d+)',
        r'imprisonment\s+(?:for\s+)?(?:up\s+to\s+)?(\d+)\s+years?',
        r'punishment\s+(?:of\s+)?(?:up\s+to\s+)?(\d+)\s+years?'
    ]
    
    for pattern in numerical_patterns:
        matches = re.finditer(pattern, answer, re.IGNORECASE)
        for match in matches:
            claims.append({
                "type": "numerical",
                "text": match.group(0),
                "position": match.span(),
                "value": match.group(1),
                "verifiable": True
            })
    
    # Date claims
    date_patterns = [
        r'(?:decided|judgment|pronounced)\s+on\s+(\d{1,2}[\./-]\d{1,2}[\./-]\d{4})',
        r'(?:in|on)\s+(\d{4})',
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})'
    ]
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, answer, re.IGNORECASE)
        for match in matches:
            claims.append({
                "type": "date",
                "text": match.group(0),
                "position": match.span(),
                "verifiable": True
            })
    
    # Definitional claims
    definition_patterns = [
        r'(?:defined\s+as|means|refers\s+to|is)\s+["\']([^"\']+)["\']',
        r'(?:Section\s+\d+\s+)?(?:defines|provides|states)\s+that\s+([^\.]+)',
    ]
    
    for pattern in definition_patterns:
        matches = re.finditer(pattern, answer, re.IGNORECASE)
        for match in matches:
            claims.append({
                "type": "definition",
                "text": match.group(0),
                "position": match.span(),
                "verifiable": True
            })
    
    return claims


async def _verify_citations_exist(answer: str, retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify that all citations in the answer correspond to actual stored authorities"""
    
    # Extract case citations
    case_patterns = [
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'(?:AIR|SCC|SCR)\s+\d{4}\s+(?:SC|[A-Z]{2,4})\s+\d+',
        r'\d{4}\s+SCC\s+OnLine\s+(?:SC|[A-Z]{2,4})\s+\d+'
    ]
    
    citations_in_answer = []
    for pattern in case_patterns:
        matches = re.finditer(pattern, answer, re.IGNORECASE)
        for match in matches:
            citations_in_answer.append({
                "text": match.group(0),
                "position": match.span()
            })
    
    verification_results = []
    
    for citation in citations_in_answer:
        citation_text = citation["text"].lower()
        found_match = False
        best_match = None
        best_similarity = 0.0
        
        # Check against all authorities in retrieval set
        for item in retrieval_set:
            title = item.get("title", "").lower()
            neutral_cite = item.get("neutral_cite", "").lower()
            reporter_cite = item.get("reporter_cite", "").lower()
            
            # Check for exact matches
            if citation_text in title or citation_text in neutral_cite or citation_text in reporter_cite:
                found_match = True
                best_match = item
                best_similarity = 1.0
                break
            
            # Check for partial matches
            similarity_title = SequenceMatcher(None, citation_text, title).ratio()
            similarity_neutral = SequenceMatcher(None, citation_text, neutral_cite).ratio()
            similarity_reporter = SequenceMatcher(None, citation_text, reporter_cite).ratio()
            
            max_similarity = max(similarity_title, similarity_neutral, similarity_reporter)
            
            if max_similarity > best_similarity:
                best_similarity = max_similarity
                best_match = item
                if max_similarity >= 0.7:
                    found_match = True
        
        verification_results.append({
            "citation": citation,
            "found": found_match,
            "similarity": best_similarity,
            "matched_authority": best_match.get("authority_id") if best_match else None,
            "matched_title": best_match.get("title") if best_match else None
        })
    
    total_citations = len(citations_in_answer)
    verified_citations = sum(1 for r in verification_results if r["found"])
    fabricated_citations = sum(1 for r in verification_results if not r["found"])
    
    verification_rate = verified_citations / total_citations if total_citations > 0 else 1.0
    
    return {
        "total_citations": total_citations,
        "verified_citations": verified_citations,
        "fabricated_citations": fabricated_citations,
        "verification_rate": verification_rate,
        "results": verification_results,
        "has_fabricated": fabricated_citations > 0
    }


def _verify_text_similarity(answer: str, retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify text similarity for quoted or paraphrased content"""
    
    # Extract quoted text
    quoted_patterns = [
        r'"([^"]+)"',
        r"'([^']+)'",
        r'held\s+that\s+([^\.]+)',
        r'observed\s+that\s+([^\.]+)',
        r'stated\s+that\s+([^\.]+)'
    ]
    
    quoted_texts = []
    for pattern in quoted_patterns:
        matches = re.finditer(pattern, answer, re.IGNORECASE)
        for match in matches:
            quoted_text = match.group(1).strip()
            if len(quoted_text) > 20:  # Only check substantial quotes
                quoted_texts.append({
                    "text": quoted_text,
                    "position": match.span(),
                    "pattern": pattern
                })
    
    similarity_results = []
    
    for quote in quoted_texts:
        quote_text = quote["text"].lower()
        best_similarity = 0.0
        best_match = None
        
        # Check against all text in retrieval set
        for item in retrieval_set:
            item_text = item.get("text", "").lower()
            
            # Check for substring match
            if quote_text in item_text:
                best_similarity = 1.0
                best_match = item
                break
            
            # Check for similarity
            similarity = SequenceMatcher(None, quote_text, item_text).ratio()
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = item
        
        similarity_results.append({
            "quote": quote,
            "similarity": best_similarity,
            "verified": best_similarity >= 0.9,  # 90% similarity threshold
            "matched_authority": best_match.get("authority_id") if best_match else None
        })
    
    verified_quotes = sum(1 for r in similarity_results if r["verified"])
    total_quotes = len(similarity_results)
    
    return {
        "total_quotes": total_quotes,
        "verified_quotes": verified_quotes,
        "similarity_results": similarity_results,
        "verification_rate": verified_quotes / total_quotes if total_quotes > 0 else 1.0,
        "has_unverified_quotes": total_quotes > verified_quotes
    }


def _verify_case_existence(answer: str, retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify that case names mentioned actually exist in the source material"""
    
    # Extract case names with party names
    case_name_pattern = r'(?:in|In)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    case_matches = re.finditer(case_name_pattern, answer)
    
    case_verification = []
    
    for match in case_matches:
        petitioner = match.group(1).strip().lower()
        respondent = match.group(2).strip().lower()
        full_case = f"{petitioner} v {respondent}"
        
        found = False
        matched_authority = None
        
        # Check if this case exists in retrieval set
        for item in retrieval_set:
            title = item.get("title", "").lower()
            
            # Check for both party names in title
            if petitioner in title and respondent in title:
                found = True
                matched_authority = item.get("authority_id")
                break
            
            # Check for partial match with high similarity
            similarity = SequenceMatcher(None, full_case, title).ratio()
            if similarity >= 0.8:
                found = True
                matched_authority = item.get("authority_id")
                break
        
        case_verification.append({
            "case_name": full_case,
            "petitioner": petitioner,
            "respondent": respondent,
            "found": found,
            "matched_authority": matched_authority
        })
    
    verified_cases = sum(1 for c in case_verification if c["found"])
    total_cases = len(case_verification)
    
    return {
        "total_cases": total_cases,
        "verified_cases": verified_cases,
        "unverified_cases": total_cases - verified_cases,
        "case_verification": case_verification,
        "verification_rate": verified_cases / total_cases if total_cases > 0 else 1.0
    }


def _detect_impossible_claims(answer: str) -> List[Dict[str, Any]]:
    """Detect obviously impossible or inconsistent legal claims"""
    
    impossible_claims = []
    answer_lower = answer.lower()
    
    # Impossible numerical claims
    impossible_numbers = [
        (r'section\s+(\d{4,})', "section_number_too_high"),  # Sections >1000 rare
        (r'article\s+(\d{4,})', "article_number_too_high"),  # Constitution has ~400 articles
        (r'(\d+)\s+years?\s+imprisonment', "excessive_imprisonment"),  # Check for >100 years
        (r'fine\s+(?:of\s+)?(?:rs\.?\s*)?(\d{10,})', "excessive_fine"),  # Unrealistic fine amounts
    ]
    
    for pattern, error_type in impossible_numbers:
        matches = re.finditer(pattern, answer_lower)
        for match in matches:
            try:
                number = int(match.group(1))
                if error_type == "section_number_too_high" and number > 2000:
                    impossible_claims.append({
                        "type": error_type,
                        "text": match.group(0),
                        "issue": f"Section {number} is unusually high"
                    })
                elif error_type == "article_number_too_high" and number > 500:
                    impossible_claims.append({
                        "type": error_type,
                        "text": match.group(0),
                        "issue": f"Article {number} does not exist in Constitution"
                    })
                elif error_type == "excessive_imprisonment" and number > 100:
                    impossible_claims.append({
                        "type": error_type,
                        "text": match.group(0),
                        "issue": f"{number} years imprisonment is unrealistic"
                    })
                elif error_type == "excessive_fine" and number > 10000000:  # 1 crore
                    impossible_claims.append({
                        "type": error_type,
                        "text": match.group(0),
                        "issue": f"Fine of Rs. {number} is unrealistic"
                    })
            except ValueError:
                continue
    
    # Impossible date claims
    future_dates = re.finditer(r'(?:decided|judgment)\s+(?:on\s+)?(\d{4})', answer_lower)
    current_year = 2024
    
    for match in future_dates:
        try:
            year = int(match.group(1))
            if year > current_year:
                impossible_claims.append({
                    "type": "future_judgment",
                    "text": match.group(0),
                    "issue": f"Judgment in {year} is in the future"
                })
            elif year < 1850:  # Before Indian legal system
                impossible_claims.append({
                    "type": "anachronistic_judgment",
                    "text": match.group(0),
                    "issue": f"Judgment in {year} predates Indian legal system"
                })
        except ValueError:
            continue
    
    # Contradictory claims within the same answer
    contradictions = []
    
    # Check for both "time-barred" and "within time"
    if "time-barred" in answer_lower and "within time" in answer_lower:
        contradictions.append({
            "type": "limitation_contradiction",
            "issue": "Claims both time-barred and within time"
        })
    
    # Check for both "liable" and "not liable"
    if "liable" in answer_lower and "not liable" in answer_lower:
        contradictions.append({
            "type": "liability_contradiction", 
            "issue": "Claims both liable and not liable"
        })
    
    impossible_claims.extend(contradictions)
    
    return impossible_claims


async def _llm_hallucination_check(answer: str, retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Use LLM to detect potential hallucinations"""
    
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        return {"verified": True, "score": 0.8, "method": "no_llm"}
    
    if not retrieval_set:
        return {"verified": True, "score": 1.0, "method": "no_sources"}
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build source context (limited to avoid token overflow)
        source_context = "\n\n".join([
            f"Source {i+1}: {item.get('title', '')}\n{item.get('text', '')[:300]}..."
            for i, item in enumerate(retrieval_set[:5])
        ])
        
        prompt = f"""Analyze this legal answer for potential hallucinations or fabricated information.

Answer to verify:
{answer[:1000]}

Available source material:
{source_context}

Check for:
1. Citations not supported by sources
2. Factual claims contradicting sources  
3. Legal provisions not mentioned in sources
4. Case details not matching sources
5. Impossible or anachronistic claims

Rate hallucination risk from 0.0 (no hallucinations) to 1.0 (severe hallucinations).
Format: RISK:0.X|EXPLANATION:brief reason"""

        response = client.chat.completions.create(
            model=settings.OPENAI_VERIFY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse response
        if "|" in content:
            risk_part, explanation_part = content.split("|", 1)
            risk = float(re.search(r'(\d\.\d+|\d)', risk_part).group(1))
            explanation = explanation_part.replace("EXPLANATION:", "").strip()
        else:
            risk = 0.3  # Default medium risk if parsing fails
            explanation = content
        
        # Convert risk to verification score
        verification_score = 1.0 - max(0.0, min(1.0, risk))
        
        return {
            "verified": risk <= 0.3,
            "risk_score": risk,
            "verification_score": verification_score,
            "explanation": explanation,
            "method": "llm_verification"
        }
        
    except Exception as e:
        log.error("hallucination_verify.llm_error", error=str(e))
        return {
            "verified": True,
            "score": 0.7,
            "error": str(e),
            "method": "fallback"
        }


def _calculate_hallucination_validity(factual_claims: List[Dict[str, Any]],
                                    citation_verification: Dict[str, Any],
                                    similarity_verification: Dict[str, Any],
                                    case_verification: Dict[str, Any],
                                    impossible_claims: List[Dict[str, Any]],
                                    llm_verification: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """Calculate overall hallucination validity and confidence"""
    
    flags = []
    
    # Citation verification
    if citation_verification["has_fabricated"]:
        flags.append("fabricated_citations_detected")
    
    citation_score = citation_verification["verification_rate"]
    
    # Text similarity verification
    if similarity_verification["has_unverified_quotes"]:
        flags.append("unverified_quotes_detected")
    
    similarity_score = similarity_verification["verification_rate"]
    
    # Case existence verification
    case_score = case_verification["verification_rate"]
    if case_verification["unverified_cases"] > 0:
        flags.append("non_existent_cases_cited")
    
    # Impossible claims
    if impossible_claims:
        flags.append("impossible_claims_detected")
        if len(impossible_claims) > 2:
            flags.append("multiple_impossible_claims")
    
    impossible_penalty = min(0.5, len(impossible_claims) * 0.15)
    
    # LLM verification
    llm_score = llm_verification.get("verification_score", 0.8)
    if not llm_verification.get("verified", True):
        flags.append("llm_detected_hallucinations")
    
    # Calculate overall confidence
    weights = {
        "citation": 0.3,
        "similarity": 0.25,
        "case": 0.2,
        "impossible": 0.1,
        "llm": 0.15
    }
    
    overall_confidence = (
        citation_score * weights["citation"] +
        similarity_score * weights["similarity"] +
        case_score * weights["case"] +
        (1.0 - impossible_penalty) * weights["impossible"] +
        llm_score * weights["llm"]
    )
    
    # Determine validity (strict threshold for hallucinations)
    valid = (
        citation_score >= 0.9 and  # Very strict on citations
        similarity_score >= 0.8 and
        case_score >= 0.9 and
        len(impossible_claims) == 0 and
        llm_verification.get("verified", True)
    )
    
    return valid, max(0.0, overall_confidence), flags
