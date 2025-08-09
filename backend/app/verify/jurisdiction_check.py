from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple
import structlog

log = structlog.get_logger()


class JurisdictionVerifyResult:
    def __init__(self, valid: bool, confidence: float, flags: List[str], details: Dict[str, Any]):
        self.valid = valid
        self.confidence = confidence
        self.flags = flags
        self.details = details


async def verify_jurisdiction_compliance(answer: str, sources: List[Dict[str, Any]], 
                                       retrieval_set: List[Dict[str, Any]]) -> JurisdictionVerifyResult:
    """
    Verify that only proper jurisdictional authorities are cited
    Focus on SC/HC hierarchy and exclude tribunals/foreign courts for MVP
    """
    
    log.info("jurisdiction_verify.start", answer_length=len(answer), sources_count=len(sources))
    
    # Analyze court hierarchy in sources
    court_analysis = _analyze_court_hierarchy(retrieval_set)
    
    # Check for non-permissible authorities
    authority_compliance = _check_authority_compliance(court_analysis)
    
    # Verify territorial jurisdiction
    territorial_verification = _verify_territorial_jurisdiction(answer, retrieval_set)
    
    # Check subject matter jurisdiction
    subject_matter_verification = _verify_subject_matter_jurisdiction(answer, retrieval_set)
    
    # Verify proper court hierarchy usage
    hierarchy_verification = _verify_hierarchy_usage(court_analysis, answer)
    
    # Calculate overall validity
    valid, confidence, flags = _calculate_jurisdiction_validity(
        court_analysis, authority_compliance, territorial_verification,
        subject_matter_verification, hierarchy_verification
    )
    
    details = {
        "court_analysis": court_analysis,
        "authority_compliance": authority_compliance,
        "territorial_verification": territorial_verification,
        "subject_matter_verification": subject_matter_verification,
        "hierarchy_verification": hierarchy_verification
    }
    
    log.info("jurisdiction_verify.complete", 
            valid=valid, 
            confidence=confidence, 
            flags_count=len(flags))
    
    return JurisdictionVerifyResult(valid, confidence, flags, details)


def _analyze_court_hierarchy(retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the court hierarchy and authority levels in sources"""
    
    # Define Indian court hierarchy
    court_levels = {
        # Supreme Court (highest)
        "SC": {"level": 1, "name": "Supreme Court", "binding_on": ["HC", "TRIBUNAL", "DISTRICT"], "permissible": True},
        
        # High Courts
        "HC-DEL": {"level": 2, "name": "Delhi High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-BOM": {"level": 2, "name": "Bombay High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-CAL": {"level": 2, "name": "Calcutta High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-MAD": {"level": 2, "name": "Madras High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-KAR": {"level": 2, "name": "Karnataka High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-GUJ": {"level": 2, "name": "Gujarat High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-RAJ": {"level": 2, "name": "Rajasthan High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-MP": {"level": 2, "name": "Madhya Pradesh High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-UP": {"level": 2, "name": "Allahabad High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-CHD": {"level": 2, "name": "Punjab & Haryana High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-KER": {"level": 2, "name": "Kerala High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-AP": {"level": 2, "name": "Andhra Pradesh High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-TS": {"level": 2, "name": "Telangana High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-ORI": {"level": 2, "name": "Orissa High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-JHA": {"level": 2, "name": "Jharkhand High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-CG": {"level": 2, "name": "Chhattisgarh High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-GAU": {"level": 2, "name": "Gauhati High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-JK": {"level": 2, "name": "Jammu & Kashmir High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-HP": {"level": 2, "name": "Himachal Pradesh High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-UTT": {"level": 2, "name": "Uttarakhand High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-SIK": {"level": 2, "name": "Sikkim High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-TRI": {"level": 2, "name": "Tripura High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-MAN": {"level": 2, "name": "Manipur High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        "HC-MEG": {"level": 2, "name": "Meghalaya High Court", "binding_on": ["TRIBUNAL", "DISTRICT"], "permissible": True},
        
        # Lower courts/tribunals (not permissible for MVP)
        "TRIBUNAL": {"level": 3, "name": "Tribunal", "binding_on": [], "permissible": False},
        "NCLAT": {"level": 3, "name": "NCLAT", "binding_on": [], "permissible": False},
        "NCLT": {"level": 3, "name": "NCLT", "binding_on": [], "permissible": False},
        "AFT": {"level": 3, "name": "Armed Forces Tribunal", "binding_on": [], "permissible": False},
        "CAT": {"level": 3, "name": "Central Administrative Tribunal", "binding_on": [], "permissible": False},
        "ITAT": {"level": 3, "name": "Income Tax Appellate Tribunal", "binding_on": [], "permissible": False},
        "TDSAT": {"level": 3, "name": "Telecom Disputes Settlement Tribunal", "binding_on": [], "permissible": False},
        "CESTAT": {"level": 3, "name": "Customs, Excise & Service Tax Appellate Tribunal", "binding_on": [], "permissible": False},
        "DISTRICT": {"level": 4, "name": "District Court", "binding_on": [], "permissible": False},
        "SESSIONS": {"level": 4, "name": "Sessions Court", "binding_on": [], "permissible": False},
        
        # Foreign courts (not permissible)
        "UK": {"level": 99, "name": "UK Courts", "binding_on": [], "permissible": False},
        "US": {"level": 99, "name": "US Courts", "binding_on": [], "permissible": False},
        "FOREIGN": {"level": 99, "name": "Foreign Courts", "binding_on": [], "permissible": False}
    }
    
    court_distribution = {}
    non_permissible_courts = []
    permissible_courts = []
    
    for item in retrieval_set:
        court = item.get("court", "UNKNOWN")
        title = item.get("title", "")
        
        # Classify court
        if court in court_levels:
            court_info = court_levels[court]
            if court not in court_distribution:
                court_distribution[court] = {
                    "count": 0,
                    "level": court_info["level"],
                    "name": court_info["name"],
                    "permissible": court_info["permissible"],
                    "cases": []
                }
            
            court_distribution[court]["count"] += 1
            court_distribution[court]["cases"].append({
                "title": title,
                "authority_id": item.get("authority_id"),
                "neutral_cite": item.get("neutral_cite"),
                "reporter_cite": item.get("reporter_cite")
            })
            
            if court_info["permissible"]:
                permissible_courts.append(court)
            else:
                non_permissible_courts.append(court)
        
        else:
            # Try to identify unknown courts
            court_type = _identify_court_type(court, title)
            if court_type:
                if court_type not in court_distribution:
                    court_distribution[court_type] = {
                        "count": 0,
                        "level": 99,
                        "name": "Unknown/Other",
                        "permissible": False,
                        "cases": []
                    }
                court_distribution[court_type]["count"] += 1
                non_permissible_courts.append(court_type)
    
    # Calculate compliance statistics
    total_authorities = len(retrieval_set)
    permissible_count = sum(court_distribution[court]["count"] 
                          for court in court_distribution 
                          if court_distribution[court]["permissible"])
    non_permissible_count = total_authorities - permissible_count
    
    compliance_rate = permissible_count / total_authorities if total_authorities > 0 else 1.0
    
    return {
        "court_distribution": court_distribution,
        "total_authorities": total_authorities,
        "permissible_count": permissible_count,
        "non_permissible_count": non_permissible_count,
        "compliance_rate": compliance_rate,
        "non_permissible_courts": list(set(non_permissible_courts)),
        "permissible_courts": list(set(permissible_courts))
    }


def _identify_court_type(court_code: str, title: str) -> str:
    """Identify court type from code or title"""
    
    title_lower = title.lower()
    court_lower = court_code.lower()
    
    # Tribunal indicators
    tribunal_keywords = [
        "tribunal", "itat", "nclat", "nclt", "aft", "cat", "tdsat", "cestat",
        "appellate tribunal", "disputes settlement", "administrative tribunal"
    ]
    
    if any(keyword in title_lower or keyword in court_lower for keyword in tribunal_keywords):
        return "TRIBUNAL"
    
    # District court indicators
    district_keywords = ["district", "sessions", "magistrate", "additional", "civil judge"]
    
    if any(keyword in title_lower for keyword in district_keywords):
        return "DISTRICT"
    
    # Foreign court indicators
    foreign_keywords = ["privy council", "house of lords", "uk", "england", "us", "america"]
    
    if any(keyword in title_lower for keyword in foreign_keywords):
        return "FOREIGN"
    
    return "UNKNOWN"


def _check_authority_compliance(court_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Check compliance with permissible authority guidelines"""
    
    compliance_rate = court_analysis["compliance_rate"]
    non_permissible_courts = court_analysis["non_permissible_courts"]
    non_permissible_count = court_analysis["non_permissible_count"]
    
    violations = []
    
    # Check for tribunal usage
    if any("TRIBUNAL" in court or "NCLT" in court or "NCLAT" in court 
           for court in non_permissible_courts):
        violations.append("tribunal_authorities_cited")
    
    # Check for district court usage
    if any("DISTRICT" in court or "SESSIONS" in court 
           for court in non_permissible_courts):
        violations.append("lower_court_authorities_cited")
    
    # Check for foreign court usage
    if any("FOREIGN" in court or "UK" in court or "US" in court 
           for court in non_permissible_courts):
        violations.append("foreign_authorities_cited")
    
    # Severity assessment
    if compliance_rate >= 0.9:
        severity = "low"
    elif compliance_rate >= 0.7:
        severity = "medium"
    else:
        severity = "high"
    
    return {
        "compliant": compliance_rate >= 0.8,
        "compliance_rate": compliance_rate,
        "violations": violations,
        "severity": severity,
        "non_permissible_count": non_permissible_count,
        "recommendation": _get_compliance_recommendation(violations, severity)
    }


def _get_compliance_recommendation(violations: List[str], severity: str) -> str:
    """Get recommendation for compliance issues"""
    
    if not violations:
        return "All authorities are from permissible jurisdictions"
    
    recommendations = []
    
    if "tribunal_authorities_cited" in violations:
        recommendations.append("Replace tribunal decisions with SC/HC precedents on the same legal issue")
    
    if "lower_court_authorities_cited" in violations:
        recommendations.append("Use binding HC/SC precedents instead of district court decisions")
    
    if "foreign_authorities_cited" in violations:
        recommendations.append("Focus on Indian jurisprudence; foreign decisions have limited persuasive value")
    
    if severity == "high":
        recommendations.append("Major jurisdictional concerns - significant revision needed")
    
    return "; ".join(recommendations)


def _verify_territorial_jurisdiction(answer: str, retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify territorial jurisdiction considerations"""
    
    answer_lower = answer.lower()
    
    # Look for territorial jurisdiction indicators
    territorial_keywords = [
        "jurisdiction", "territorial", "cause of action arose", "subject matter",
        "pecuniary jurisdiction", "local limits", "where", "location", "place"
    ]
    
    has_territorial_discussion = any(keyword in answer_lower for keyword in territorial_keywords)
    
    # Analyze geographical spread of authorities
    hc_jurisdictions = set()
    for item in retrieval_set:
        court = item.get("court", "")
        if court.startswith("HC-"):
            hc_jurisdictions.add(court)
    
    # Check for multi-jurisdictional authorities
    jurisdiction_diversity = len(hc_jurisdictions)
    
    territorial_score = 1.0
    flags = []
    
    # If multiple HC jurisdictions without discussion, flag it
    if jurisdiction_diversity > 2 and not has_territorial_discussion:
        flags.append("multiple_jurisdictions_without_discussion")
        territorial_score -= 0.2
    
    # If territorial keywords present, boost score
    if has_territorial_discussion:
        territorial_score = min(1.0, territorial_score + 0.1)
    
    return {
        "has_territorial_discussion": has_territorial_discussion,
        "jurisdiction_diversity": jurisdiction_diversity,
        "hc_jurisdictions": list(hc_jurisdictions),
        "territorial_score": territorial_score,
        "flags": flags,
        "verified": len(flags) == 0
    }


def _verify_subject_matter_jurisdiction(answer: str, retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify subject matter jurisdiction appropriateness"""
    
    answer_lower = answer.lower()
    
    # Identify legal subject matter from answer
    subject_matters = {
        "constitutional": ["constitution", "fundamental rights", "article", "constitutional"],
        "criminal": ["criminal", "penal", "ipc", "crpc", "bail", "charge", "prosecution"],
        "civil": ["civil", "contract", "tort", "property", "damages", "suit"],
        "commercial": ["commercial", "company", "contract", "trade", "business"],
        "family": ["family", "marriage", "divorce", "maintenance", "custody"],
        "service": ["service", "employment", "pension", "promotion", "termination"],
        "taxation": ["tax", "income tax", "gst", "customs", "excise"],
        "labour": ["labour", "industrial", "workers", "union", "bonus"],
        "intellectual_property": ["trademark", "copyright", "patent", "ip"],
        "environmental": ["environment", "pollution", "forest", "wildlife"],
        "human_rights": ["human rights", "liberty", "detention", "torture"]
    }
    
    identified_subjects = []
    for subject, keywords in subject_matters.items():
        if any(keyword in answer_lower for keyword in keywords):
            identified_subjects.append(subject)
    
    # Check if authorities match subject matter
    subject_authority_match = []
    
    for item in retrieval_set:
        title = item.get("title", "").lower()
        court = item.get("court", "")
        
        for subject in identified_subjects:
            subject_keywords = subject_matters[subject]
            if any(keyword in title for keyword in subject_keywords):
                subject_authority_match.append({
                    "subject": subject,
                    "authority": item.get("title", ""),
                    "court": court
                })
                break
    
    match_rate = len(subject_authority_match) / len(retrieval_set) if retrieval_set else 1.0
    
    # Special jurisdiction checks
    special_jurisdictions = []
    
    # Check for specialized court requirements
    if "constitutional" in identified_subjects:
        sc_constitutional = any(item.get("court") == "SC" for item in retrieval_set)
        if not sc_constitutional:
            special_jurisdictions.append("constitutional_matter_needs_sc_precedent")
    
    if "commercial" in identified_subjects:
        # Commercial courts have specialized jurisdiction
        special_jurisdictions.append("consider_commercial_court_jurisdiction")
    
    return {
        "identified_subjects": identified_subjects,
        "subject_authority_match": subject_authority_match,
        "match_rate": match_rate,
        "special_jurisdictions": special_jurisdictions,
        "verified": match_rate >= 0.6 and len(special_jurisdictions) <= 1,
        "score": match_rate - (len(special_jurisdictions) * 0.1)
    }


def _verify_hierarchy_usage(court_analysis: Dict[str, Any], answer: str) -> Dict[str, Any]:
    """Verify proper usage of court hierarchy"""
    
    answer_lower = answer.lower()
    court_distribution = court_analysis["court_distribution"]
    
    # Check for hierarchy-aware language
    hierarchy_keywords = [
        "binding", "persuasive", "bound by", "supreme court", "high court",
        "precedent", "authority", "decided by", "binding on"
    ]
    
    has_hierarchy_awareness = any(keyword in answer_lower for keyword in hierarchy_keywords)
    
    # Analyze hierarchy composition
    sc_cases = court_distribution.get("SC", {}).get("count", 0)
    hc_cases = sum(court_distribution[court]["count"] 
                   for court in court_distribution 
                   if court.startswith("HC-"))
    
    # Check for proper precedence
    hierarchy_score = 0.7  # Base score
    
    if sc_cases > 0:
        hierarchy_score += 0.2  # SC precedents boost score
    
    if has_hierarchy_awareness:
        hierarchy_score += 0.1  # Hierarchy awareness boost
    
    # Check for inverted hierarchy (lower courts overriding higher courts)
    hierarchy_violations = []
    
    # If SC precedents exist, they should be given precedence
    if sc_cases > 0 and "supreme court" not in answer_lower:
        hierarchy_violations.append("sc_precedent_not_emphasized")
    
    return {
        "has_hierarchy_awareness": has_hierarchy_awareness,
        "sc_cases": sc_cases,
        "hc_cases": hc_cases,
        "hierarchy_violations": hierarchy_violations,
        "hierarchy_score": min(1.0, hierarchy_score),
        "verified": len(hierarchy_violations) == 0
    }


def _calculate_jurisdiction_validity(court_analysis: Dict[str, Any],
                                   authority_compliance: Dict[str, Any],
                                   territorial_verification: Dict[str, Any],
                                   subject_matter_verification: Dict[str, Any],
                                   hierarchy_verification: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """Calculate overall jurisdiction validity and confidence"""
    
    flags = []
    
    # Authority compliance check
    if not authority_compliance["compliant"]:
        flags.append("non_permissible_authorities_cited")
        if authority_compliance["severity"] == "high":
            flags.append("major_jurisdictional_violations")
    
    # Territorial jurisdiction check
    if not territorial_verification["verified"]:
        flags.extend(territorial_verification["flags"])
    
    # Subject matter jurisdiction check  
    if not subject_matter_verification["verified"]:
        flags.append("subject_matter_jurisdiction_mismatch")
    
    # Hierarchy usage check
    if not hierarchy_verification["verified"]:
        flags.append("improper_court_hierarchy_usage")
    
    # Calculate overall confidence
    weights = {
        "authority_compliance": 0.4,
        "territorial": 0.2,
        "subject_matter": 0.2,
        "hierarchy": 0.2
    }
    
    overall_confidence = (
        authority_compliance["compliance_rate"] * weights["authority_compliance"] +
        territorial_verification["territorial_score"] * weights["territorial"] +
        subject_matter_verification["score"] * weights["subject_matter"] +
        hierarchy_verification["hierarchy_score"] * weights["hierarchy"]
    )
    
    # Determine validity
    valid = (
        authority_compliance["compliant"] and
        territorial_verification["verified"] and
        subject_matter_verification["verified"] and
        hierarchy_verification["verified"]
    )
    
    return valid, max(0.0, overall_confidence), flags
