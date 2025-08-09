from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple, Optional
import structlog

log = structlog.get_logger()


class LimitationVerifyResult:
    def __init__(self, valid: bool, confidence: float, flags: List[str], details: Dict[str, Any]):
        self.valid = valid
        self.confidence = confidence
        self.flags = flags
        self.details = details


async def verify_limitation_compliance(answer: str, sources: List[Dict[str, Any]], 
                                     retrieval_set: List[Dict[str, Any]]) -> LimitationVerifyResult:
    """
    Verify limitation period calculations and compliance
    """
    
    log.info("limitation_verify.start", answer_length=len(answer), sources_count=len(sources))
    
    # Extract limitation-related information from answer
    limitation_info = _extract_limitation_info(answer)
    
    # Verify article citations
    article_verification = _verify_limitation_articles(limitation_info, retrieval_set)
    
    # Check time calculations if present
    time_verification = _verify_time_calculations(limitation_info, answer)
    
    # Verify accrual rules
    accrual_verification = _verify_accrual_rules(limitation_info, answer, retrieval_set)
    
    # Check for exception handling
    exception_verification = _verify_limitation_exceptions(limitation_info, answer, retrieval_set)
    
    # Calculate overall validity
    valid, confidence, flags = _calculate_limitation_validity(
        limitation_info, article_verification, time_verification, 
        accrual_verification, exception_verification
    )
    
    details = {
        "limitation_info": limitation_info,
        "article_verification": article_verification,
        "time_verification": time_verification,
        "accrual_verification": accrual_verification,
        "exception_verification": exception_verification
    }
    
    log.info("limitation_verify.complete", 
            valid=valid, 
            confidence=confidence, 
            flags_count=len(flags))
    
    return LimitationVerifyResult(valid, confidence, flags, details)


def _extract_limitation_info(answer: str) -> Dict[str, Any]:
    """Extract limitation-related information from the answer"""
    
    # Extract article numbers
    article_pattern = r'[Aa]rticle\s+(\d+)\s*(?:of\s+(?:the\s+)?Limitation\s+Act)?'
    articles = re.findall(article_pattern, answer)
    
    # Extract time periods
    period_patterns = [
        (r'(\d+)\s+years?', 'years'),
        (r'(\d+)\s+months?', 'months'),
        (r'(\d+)\s+days?', 'days'),
        (r'three\s+years?', 'years'),
        (r'one\s+year', 'years'),
        (r'twelve\s+years?', 'years'),
        (r'thirty\s+years?', 'years')
    ]
    
    periods = []
    for pattern, unit in period_patterns:
        matches = re.findall(pattern, answer, re.IGNORECASE)
        for match in matches:
            try:
                if match.isdigit():
                    periods.append({"value": int(match), "unit": unit})
                elif match.lower() in ["three", "3"]:
                    periods.append({"value": 3, "unit": unit})
                elif match.lower() in ["one", "1"]:
                    periods.append({"value": 1, "unit": unit})
                elif match.lower() in ["twelve", "12"]:
                    periods.append({"value": 12, "unit": unit})
                elif match.lower() in ["thirty", "30"]:
                    periods.append({"value": 30, "unit": unit})
            except ValueError:
                continue
    
    # Extract dates
    dates = _extract_dates_from_text(answer)
    
    # Extract limitation keywords
    limitation_keywords = [
        "time-barred", "barred by time", "limitation", "prescribed",
        "cause of action", "accrual", "disability", "fraud", 
        "mistake", "acknowledgment", "part payment"
    ]
    
    found_keywords = [kw for kw in limitation_keywords if kw.lower() in answer.lower()]
    
    # Extract exception indicators
    exceptions = []
    exception_patterns = {
        "fraud": r'fraud|fraudulent|concealment',
        "mistake": r'mistake|error',
        "disability": r'disability|minor|unsound mind',
        "acknowledgment": r'acknowledgment|acknowledge',
        "part_payment": r'part payment|partial payment'
    }
    
    for exception_type, pattern in exception_patterns.items():
        if re.search(pattern, answer, re.IGNORECASE):
            exceptions.append(exception_type)
    
    return {
        "articles": list(set(articles)),
        "periods": periods,
        "dates": dates,
        "keywords": found_keywords,
        "exceptions": exceptions,
        "has_limitation_content": len(articles) > 0 or len(periods) > 0 or len(found_keywords) > 0
    }


def _extract_dates_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract dates from text"""
    
    dates = []
    
    # Date patterns
    date_patterns = [
        (r'(\d{1,2})[\./-](\d{1,2})[\./-](\d{4})', 'dd/mm/yyyy'),
        (r'(\d{4})[\./-](\d{1,2})[\./-](\d{1,2})', 'yyyy/mm/dd'),
        (r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})', 'dd Month yyyy')
    ]
    
    month_map = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    for pattern, format_type in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                if format_type == 'dd/mm/yyyy':
                    day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                elif format_type == 'yyyy/mm/dd':
                    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                elif format_type == 'dd Month yyyy':
                    day = int(match.group(1))
                    month = month_map.get(match.group(2).lower(), 1)
                    year = int(match.group(3))
                
                if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2030:
                    date_obj = datetime(year, month, day)
                    dates.append({
                        "date": date_obj,
                        "text": match.group(0),
                        "format": format_type
                    })
                    
            except (ValueError, IndexError):
                continue
    
    return dates


def _verify_limitation_articles(limitation_info: Dict[str, Any], 
                               retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify that limitation articles cited are accurate"""
    
    articles = limitation_info["articles"]
    
    if not articles:
        return {"verified": True, "score": 1.0, "reason": "no_articles_cited"}
    
    # Known Limitation Act articles and their periods
    standard_articles = {
        "113": {"period": 3, "unit": "years", "description": "Residual article"},
        "114": {"period": 3, "unit": "years", "description": "For compensation for wrongs"},
        "111": {"period": 12, "unit": "years", "description": "To recover possession"},
        "58": {"period": 3, "unit": "years", "description": "For money deposited"},
        "59": {"period": 3, "unit": "years", "description": "For necessaries supplied"},
        "137": {"period": 1, "unit": "year", "description": "To set aside transfer by guardian"},
        "23": {"period": 3, "unit": "years", "description": "To recover movables"},
        "65": {"period": 3, "unit": "years", "description": "Suit on bill of exchange"},
        "468": {"period": 6, "unit": "months", "description": "CrPC complaint limitation"}
    }
    
    verification_results = []
    
    for article in articles:
        if article in standard_articles:
            article_info = standard_articles[article]
            
            # Check if the periods mentioned match this article
            period_match = False
            for period in limitation_info["periods"]:
                if (period["value"] == article_info["period"] and 
                    period["unit"] == article_info["unit"]):
                    period_match = True
                    break
            
            verification_results.append({
                "article": article,
                "valid": True,
                "period_match": period_match,
                "expected_period": f"{article_info['period']} {article_info['unit']}",
                "description": article_info["description"]
            })
        else:
            # Check if article exists in sources
            found_in_sources = False
            for item in retrieval_set:
                if f"article {article}" in item.get("text", "").lower():
                    found_in_sources = True
                    break
            
            verification_results.append({
                "article": article,
                "valid": found_in_sources,
                "period_match": False,
                "found_in_sources": found_in_sources
            })
    
    valid_articles = sum(1 for r in verification_results if r["valid"])
    period_matches = sum(1 for r in verification_results if r.get("period_match", False))
    
    return {
        "results": verification_results,
        "valid_articles": valid_articles,
        "total_articles": len(articles),
        "period_matches": period_matches,
        "verification_score": valid_articles / len(articles) if articles else 1.0,
        "period_accuracy": period_matches / len(articles) if articles else 1.0
    }


def _verify_time_calculations(limitation_info: Dict[str, Any], answer: str) -> Dict[str, Any]:
    """Verify time period calculations if dates are provided"""
    
    dates = limitation_info["dates"]
    periods = limitation_info["periods"]
    
    if not dates or not periods:
        return {"verified": True, "score": 1.0, "reason": "insufficient_date_info"}
    
    calculation_errors = []
    calculation_warnings = []
    
    # Check for calculation-related text
    calculation_indicators = [
        "expired", "time-barred", "within time", "limitation period",
        "from the date", "accrued", "remaining"
    ]
    
    has_calculations = any(indicator in answer.lower() for indicator in calculation_indicators)
    
    if not has_calculations:
        return {"verified": True, "score": 0.8, "reason": "no_explicit_calculations"}
    
    # If we have one date and one period, verify the calculation
    if len(dates) >= 1 and len(periods) >= 1:
        start_date = dates[0]["date"]
        period = periods[0]
        
        # Calculate expected expiry date
        if period["unit"] == "years":
            expected_expiry = start_date + timedelta(days=365 * period["value"])
        elif period["unit"] == "months":
            expected_expiry = start_date + timedelta(days=30 * period["value"])
        elif period["unit"] == "days":
            expected_expiry = start_date + timedelta(days=period["value"])
        else:
            return {"verified": True, "score": 0.7, "reason": "unknown_period_unit"}
        
        current_date = datetime.now()
        days_remaining = (expected_expiry - current_date).days
        
        # Check if the answer's conclusion matches our calculation
        is_expired = days_remaining < 0
        
        if "time-barred" in answer.lower() or "expired" in answer.lower():
            if not is_expired:
                calculation_errors.append("claims_expired_but_calculation_shows_within_time")
        elif "within time" in answer.lower():
            if is_expired:
                calculation_errors.append("claims_within_time_but_calculation_shows_expired")
        
        return {
            "start_date": start_date.isoformat(),
            "expected_expiry": expected_expiry.isoformat(),
            "days_remaining": days_remaining,
            "is_expired": is_expired,
            "calculation_errors": calculation_errors,
            "calculation_warnings": calculation_warnings,
            "verified": len(calculation_errors) == 0,
            "score": 1.0 - (len(calculation_errors) * 0.3)
        }
    
    return {"verified": True, "score": 0.8, "reason": "complex_calculation_scenario"}


def _verify_accrual_rules(limitation_info: Dict[str, Any], answer: str, 
                         retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify that accrual rules are correctly applied"""
    
    answer_lower = answer.lower()
    
    # Check for accrual-related content
    accrual_indicators = [
        "cause of action", "accrued", "accrual", "from the date",
        "when the right to sue arises", "knowledge", "discovery"
    ]
    
    has_accrual_content = any(indicator in answer_lower for indicator in accrual_indicators)
    
    if not has_accrual_content:
        return {"verified": True, "score": 1.0, "reason": "no_accrual_discussion"}
    
    accrual_accuracy = []
    
    # Check for common accrual rules
    accrual_rules = {
        "contract_breach": ["breach", "contract", "performance"],
        "tort": ["injury", "damage", "negligence", "tort"],
        "money_recovery": ["debt", "loan", "payment", "money"],
        "property_possession": ["possession", "dispossession", "title"]
    }
    
    identified_cause = None
    for cause_type, keywords in accrual_rules.items():
        if all(any(kw in answer_lower for kw in keywords[:2]) for kw in keywords[:1]):
            identified_cause = cause_type
            break
    
    # Verify accrual rules for identified cause
    if identified_cause:
        if identified_cause == "contract_breach":
            if "breach" in answer_lower and ("performance" in answer_lower or "default" in answer_lower):
                accrual_accuracy.append({"rule": "contract_accrual", "correct": True})
            else:
                accrual_accuracy.append({"rule": "contract_accrual", "correct": False})
        
        elif identified_cause == "tort":
            if "injury" in answer_lower or "damage" in answer_lower:
                accrual_accuracy.append({"rule": "tort_accrual", "correct": True})
            else:
                accrual_accuracy.append({"rule": "tort_accrual", "correct": False})
    
    correct_rules = sum(1 for rule in accrual_accuracy if rule["correct"])
    total_rules = len(accrual_accuracy)
    
    return {
        "has_accrual_content": has_accrual_content,
        "identified_cause": identified_cause,
        "accrual_accuracy": accrual_accuracy,
        "correct_rules": correct_rules,
        "total_rules": total_rules,
        "verified": total_rules == 0 or correct_rules == total_rules,
        "score": 1.0 if total_rules == 0 else correct_rules / total_rules
    }


def _verify_limitation_exceptions(limitation_info: Dict[str, Any], answer: str,
                                retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify proper handling of limitation exceptions"""
    
    exceptions = limitation_info["exceptions"]
    answer_lower = answer.lower()
    
    if not exceptions:
        return {"verified": True, "score": 1.0, "reason": "no_exceptions_claimed"}
    
    exception_verification = []
    
    # Verify each exception type
    exception_rules = {
        "fraud": {
            "keywords": ["discovery", "knowledge", "fraud", "concealment"],
            "rule": "time runs from discovery of fraud"
        },
        "mistake": {
            "keywords": ["mistake", "error", "discovery"],
            "rule": "time runs from discovery of mistake"
        },
        "disability": {
            "keywords": ["minor", "disability", "unsound mind", "guardian"],
            "rule": "extension during disability period"
        },
        "acknowledgment": {
            "keywords": ["acknowledgment", "acknowledge", "fresh period"],
            "rule": "fresh limitation period from acknowledgment"
        },
        "part_payment": {
            "keywords": ["part payment", "partial", "fresh period"],
            "rule": "fresh limitation period from part payment"
        }
    }
    
    for exception in exceptions:
        if exception in exception_rules:
            rule_info = exception_rules[exception]
            
            # Check if proper keywords are present
            has_proper_keywords = any(kw in answer_lower for kw in rule_info["keywords"])
            
            # Check if rule is properly explained
            rule_explained = False
            if exception == "fraud" and "discovery" in answer_lower:
                rule_explained = True
            elif exception == "disability" and ("minor" in answer_lower or "disability" in answer_lower):
                rule_explained = True
            elif exception in ["acknowledgment", "part_payment"] and "fresh" in answer_lower:
                rule_explained = True
            
            exception_verification.append({
                "exception": exception,
                "has_keywords": has_proper_keywords,
                "rule_explained": rule_explained,
                "expected_rule": rule_info["rule"]
            })
    
    correct_exceptions = sum(1 for ex in exception_verification 
                           if ex["has_keywords"] and ex["rule_explained"])
    total_exceptions = len(exception_verification)
    
    return {
        "exceptions_found": exceptions,
        "exception_verification": exception_verification,
        "correct_exceptions": correct_exceptions,
        "total_exceptions": total_exceptions,
        "verified": total_exceptions == 0 or correct_exceptions >= total_exceptions * 0.7,
        "score": 1.0 if total_exceptions == 0 else correct_exceptions / total_exceptions
    }


def _calculate_limitation_validity(limitation_info: Dict[str, Any],
                                 article_verification: Dict[str, Any],
                                 time_verification: Dict[str, Any],
                                 accrual_verification: Dict[str, Any],
                                 exception_verification: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """Calculate overall limitation validity and confidence"""
    
    flags = []
    
    # Check if limitation content exists when it should
    has_limitation_content = limitation_info["has_limitation_content"]
    
    # Article verification
    article_score = article_verification["verification_score"]
    if article_score < 0.8:
        flags.append("incorrect_limitation_articles")
    
    period_accuracy = article_verification.get("period_accuracy", 1.0)
    if period_accuracy < 0.8:
        flags.append("incorrect_period_calculations")
    
    # Time calculation verification
    time_score = time_verification["score"]
    if not time_verification["verified"]:
        flags.append("limitation_calculation_errors")
    
    # Accrual verification
    accrual_score = accrual_verification["score"]
    if not accrual_verification["verified"]:
        flags.append("incorrect_accrual_rules")
    
    # Exception verification
    exception_score = exception_verification["score"]
    if not exception_verification["verified"]:
        flags.append("incorrect_exception_handling")
    
    # Calculate overall confidence
    weights = {
        "article": 0.3,
        "time": 0.25,
        "accrual": 0.25,
        "exception": 0.2
    }
    
    overall_confidence = (
        article_score * weights["article"] +
        time_score * weights["time"] +
        accrual_score * weights["accrual"] +
        exception_score * weights["exception"]
    )
    
    # Determine validity
    valid = (
        article_score >= 0.7 and
        time_verification["verified"] and
        accrual_verification["verified"] and
        exception_verification["verified"]
    )
    
    return valid, overall_confidence, flags
