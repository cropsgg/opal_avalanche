from __future__ import annotations

from typing import Any, Dict, List
import structlog

from app.verify.statute_check import verify_statute_alignment
from app.verify.precedent_check import verify_precedent_conflicts  
from app.verify.limitation_check import verify_limitation_compliance
from app.verify.jurisdiction_check import verify_jurisdiction_compliance
from app.verify.hallucination_check import verify_hallucination_detection

log = structlog.get_logger()


async def verify_comprehensive(answer: str, sources: List[Dict[str, Any]], 
                             retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Comprehensive verification with all 5 checks as per PRD:
    1. Statute alignment verification
    2. Precedent conflict detection  
    3. Limitation period verification
    4. Jurisdiction validation
    5. Hallucination detection
    """
    
    log.info("verify.comprehensive.start", 
            answer_length=len(answer), 
            sources_count=len(sources),
            retrieval_set_count=len(retrieval_set))
    
    verification_results = {}
    all_flags = []
    
    try:
        # 1. Statute Alignment Check
        log.info("verify.statute_check.start")
        statute_result = await verify_statute_alignment(answer, sources, retrieval_set)
        verification_results["statute"] = {
            "valid": statute_result.valid,
            "confidence": statute_result.confidence,
            "flags": statute_result.flags,
            "details": statute_result.details
        }
        all_flags.extend([f"statute_{flag}" for flag in statute_result.flags])
        log.info("verify.statute_check.complete", valid=statute_result.valid)
        
    except Exception as e:
        log.error("verify.statute_check.error", error=str(e))
        verification_results["statute"] = {
            "valid": False,
            "confidence": 0.3,
            "flags": ["statute_verification_error"],
            "error": str(e)
        }
        all_flags.append("statute_verification_error")
    
    try:
        # 2. Precedent Conflict Check
        log.info("verify.precedent_check.start")
        precedent_result = await verify_precedent_conflicts(answer, sources, retrieval_set)
        verification_results["precedent"] = {
            "valid": precedent_result.valid,
            "confidence": precedent_result.confidence,
            "flags": precedent_result.flags,
            "details": precedent_result.details
        }
        all_flags.extend([f"precedent_{flag}" for flag in precedent_result.flags])
        log.info("verify.precedent_check.complete", valid=precedent_result.valid)
        
    except Exception as e:
        log.error("verify.precedent_check.error", error=str(e))
        verification_results["precedent"] = {
            "valid": False,
            "confidence": 0.3,
            "flags": ["precedent_verification_error"],
            "error": str(e)
        }
        all_flags.append("precedent_verification_error")
    
    try:
        # 3. Limitation Period Check
        log.info("verify.limitation_check.start")
        limitation_result = await verify_limitation_compliance(answer, sources, retrieval_set)
        verification_results["limitation"] = {
            "valid": limitation_result.valid,
            "confidence": limitation_result.confidence,
            "flags": limitation_result.flags,
            "details": limitation_result.details
        }
        all_flags.extend([f"limitation_{flag}" for flag in limitation_result.flags])
        log.info("verify.limitation_check.complete", valid=limitation_result.valid)
        
    except Exception as e:
        log.error("verify.limitation_check.error", error=str(e))
        verification_results["limitation"] = {
            "valid": False,
            "confidence": 0.3,
            "flags": ["limitation_verification_error"],
            "error": str(e)
        }
        all_flags.append("limitation_verification_error")
    
    try:
        # 4. Jurisdiction Compliance Check
        log.info("verify.jurisdiction_check.start")
        jurisdiction_result = await verify_jurisdiction_compliance(answer, sources, retrieval_set)
        verification_results["jurisdiction"] = {
            "valid": jurisdiction_result.valid,
            "confidence": jurisdiction_result.confidence,
            "flags": jurisdiction_result.flags,
            "details": jurisdiction_result.details
        }
        all_flags.extend([f"jurisdiction_{flag}" for flag in jurisdiction_result.flags])
        log.info("verify.jurisdiction_check.complete", valid=jurisdiction_result.valid)
        
    except Exception as e:
        log.error("verify.jurisdiction_check.error", error=str(e))
        verification_results["jurisdiction"] = {
            "valid": False,
            "confidence": 0.3,
            "flags": ["jurisdiction_verification_error"],
            "error": str(e)
        }
        all_flags.append("jurisdiction_verification_error")
    
    try:
        # 5. Hallucination Detection
        log.info("verify.hallucination_check.start")
        hallucination_result = await verify_hallucination_detection(answer, sources, retrieval_set)
        verification_results["hallucination"] = {
            "valid": hallucination_result.valid,
            "confidence": hallucination_result.confidence,
            "flags": hallucination_result.flags,
            "details": hallucination_result.details
        }
        all_flags.extend([f"hallucination_{flag}" for flag in hallucination_result.flags])
        log.info("verify.hallucination_check.complete", valid=hallucination_result.valid)
        
    except Exception as e:
        log.error("verify.hallucination_check.error", error=str(e))
        verification_results["hallucination"] = {
            "valid": False,
            "confidence": 0.3,
            "flags": ["hallucination_verification_error"],
            "error": str(e)
        }
        all_flags.append("hallucination_verification_error")
    
    # Calculate overall verification result
    overall_result = _calculate_overall_verification(verification_results, all_flags)
    
    log.info("verify.comprehensive.complete",
            overall_valid=overall_result["valid"],
            overall_confidence=overall_result["confidence"],
            total_flags=len(all_flags))
    
    return overall_result


def _calculate_overall_verification(verification_results: Dict[str, Any], 
                                  all_flags: List[str]) -> Dict[str, Any]:
    """Calculate overall verification result from individual checks"""
    
    # Extract individual results
    checks = ["statute", "precedent", "limitation", "jurisdiction", "hallucination"]
    
    valid_checks = []
    confidences = []
    
    for check in checks:
        if check in verification_results:
            result = verification_results[check]
            valid_checks.append(result.get("valid", False))
            confidences.append(result.get("confidence", 0.3))
        else:
            valid_checks.append(False)
            confidences.append(0.3)
    
    # Overall validity: all critical checks must pass
    # Hallucination and statute alignment are most critical
    critical_checks = {
        "hallucination": verification_results.get("hallucination", {}).get("valid", False),
        "statute": verification_results.get("statute", {}).get("valid", False),
        "jurisdiction": verification_results.get("jurisdiction", {}).get("valid", False)
    }
    
    # Other checks can have warnings but don't fail the entire verification
    warning_checks = {
        "precedent": verification_results.get("precedent", {}).get("valid", True),
        "limitation": verification_results.get("limitation", {}).get("valid", True)
    }
    
    # Overall validity: critical checks must pass
    overall_valid = all(critical_checks.values())
    
    # Calculate weighted confidence
    weights = {
        "hallucination": 0.3,  # Most important
        "statute": 0.25,
        "jurisdiction": 0.2,
        "precedent": 0.15,
        "limitation": 0.1
    }
    
    overall_confidence = sum(
        verification_results.get(check, {}).get("confidence", 0.3) * weight
        for check, weight in weights.items()
    )
    
    # Apply penalties for warnings
    warning_penalty = 0.0
    for check, valid in warning_checks.items():
        if not valid:
            warning_penalty += 0.05  # Small penalty for warnings
    
    overall_confidence = max(0.0, overall_confidence - warning_penalty)
    
    # Determine verification level
    if overall_valid and overall_confidence >= 0.8:
        verification_level = "high"
    elif overall_valid and overall_confidence >= 0.6:
        verification_level = "medium"
    elif overall_valid:
        verification_level = "low"
    else:
        verification_level = "failed"
    
    # Generate summary message
    if not overall_valid:
        if not critical_checks["hallucination"]:
            summary = "Verification failed: Potential fabricated citations or hallucinations detected"
        elif not critical_checks["statute"]:
            summary = "Verification failed: Statutory citation or interpretation errors"
        elif not critical_checks["jurisdiction"]:
            summary = "Verification failed: Jurisdictional compliance issues"
        else:
            summary = "Verification failed: Multiple critical issues detected"
    else:
        warning_count = sum(1 for valid in warning_checks.values() if not valid)
        if warning_count > 0:
            summary = f"Verification passed with {warning_count} warning(s)"
        else:
            summary = "All verification checks passed"
    
    return {
        "valid": overall_valid,
        "confidence": overall_confidence,
        "flags": all_flags,
        "verification_level": verification_level,
        "summary": summary,
        "individual_results": verification_results,
        "critical_checks": critical_checks,
        "warning_checks": warning_checks,
        "total_checks": len(checks),
        "passed_checks": sum(valid_checks),
        "failed_checks": len(checks) - sum(valid_checks)
    }


async def verify_basic(answer: str) -> Dict[str, Any]:
    """
    Basic verification for backward compatibility
    Returns simplified result format
    """
    
    # For basic verification, just run hallucination detection
    # as it's the most critical for preventing fabricated content
    try:
        hallucination_result = await verify_hallucination_detection(answer, [], [])
        
        return {
            "valid": hallucination_result.valid,
            "confidence": hallucination_result.confidence,
            "flags": hallucination_result.flags
        }
        
    except Exception as e:
        log.error("verify.basic.error", error=str(e))
        return {
            "valid": False,
            "confidence": 0.3,
            "flags": ["verification_error"]
        }


