from __future__ import annotations

import re
from typing import Any, Dict, List
import structlog

from openai import OpenAI
from app.core.config import get_settings
from app.agents.base import AgentOutput

log = structlog.get_logger()


class RiskAgent:
    name = "risk"

    async def run(self, query: str, packs: List[Dict[str, Any]], matter_docs: List[Dict[str, Any]]) -> AgentOutput:
        """
        Assess legal risks, potential adverse outcomes, and strategic considerations
        Focus on liability exposure, procedural risks, and success probability
        """
        
        log.info("risk_agent.start", query_length=len(query))
        
        # Identify risk factors from query and context
        risk_factors = self._identify_risk_factors(query, packs)
        
        # Assess procedural and substantive risks
        procedural_risks = self._assess_procedural_risks(query, packs)
        substantive_risks = self._assess_substantive_risks(query, packs)
        
        # Analyze success probability indicators
        success_indicators = self._analyze_success_probability(packs)
        
        # Identify adverse precedents and outcomes
        adverse_outcomes = self._identify_adverse_outcomes(packs)
        
        # Build comprehensive risk assessment
        reasoning = await self._analyze_risks(query, risk_factors, procedural_risks, 
                                            substantive_risks, success_indicators, adverse_outcomes)
        
        sources = self._extract_risk_sources(packs, risk_factors, adverse_outcomes)
        confidence = self._calculate_confidence(risk_factors, procedural_risks, substantive_risks)
        
        log.info("risk_agent.complete",
                confidence=confidence,
                risk_factors=len(risk_factors),
                procedural_risks=len(procedural_risks),
                substantive_risks=len(substantive_risks))
        
        return AgentOutput(
            reasoning=reasoning,
            sources=sources,
            confidence=confidence
        )

    def _identify_risk_factors(self, query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential risk factors from query and authorities"""
        
        risk_factors = []
        
        # Query-based risk indicators
        query_risk_keywords = {
            "high": ["criminal", "prosecution", "arrest", "penalty", "fine", "imprisonment", "contempt"],
            "medium": ["damages", "compensation", "liability", "breach", "default", "violation"],
            "procedural": ["jurisdiction", "limitation", "procedure", "appeal", "review", "stay"],
            "financial": ["cost", "fee", "expense", "security", "deposit", "bank guarantee"],
            "reputational": ["defamation", "reputation", "public", "media", "scandal"],
            "regulatory": ["compliance", "regulation", "license", "permit", "authority", "board"]
        }
        
        query_lower = query.lower()
        for risk_type, keywords in query_risk_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    risk_factors.append({
                        "type": risk_type,
                        "factor": keyword,
                        "source": "query",
                        "severity": self._assess_keyword_severity(keyword)
                    })
        
        # Authority-based risk indicators
        for pack in packs:
            title = pack.get("title", "").lower()
            court = pack.get("court", "")
            
            # Check for adverse outcomes in case titles
            adverse_keywords = [
                "dismiss", "reject", "deny", "refuse", "decline",
                "liable", "guilty", "convicted", "penalty", "fine",
                "contempt", "breach", "violation", "default"
            ]
            
            for keyword in adverse_keywords:
                if keyword in title:
                    risk_factors.append({
                        "type": "adverse_precedent",
                        "factor": keyword,
                        "source": "authority",
                        "authority_id": pack.get("authority_id"),
                        "title": pack.get("title"),
                        "court": court,
                        "severity": self._assess_keyword_severity(keyword)
                    })
        
        return risk_factors

    def _assess_keyword_severity(self, keyword: str) -> str:
        """Assess severity level of risk keyword"""
        
        high_severity = ["criminal", "prosecution", "imprisonment", "contempt", "penalty"]
        medium_severity = ["damages", "liable", "breach", "violation", "dismiss"]
        
        if keyword in high_severity:
            return "high"
        elif keyword in medium_severity:
            return "medium"
        else:
            return "low"

    def _assess_procedural_risks(self, query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess procedural risks and compliance issues"""
        
        procedural_risks = []
        
        # Common procedural risk areas
        procedural_categories = {
            "jurisdiction": {
                "keywords": ["jurisdiction", "territorial", "pecuniary", "forum", "venue"],
                "description": "Risk of proceedings being outside proper jurisdiction"
            },
            "limitation": {
                "keywords": ["limitation", "time-barred", "prescribed", "delay"],
                "description": "Risk of claim being time-barred"
            },
            "procedure": {
                "keywords": ["procedure", "process", "service", "notice", "pleading"],
                "description": "Risk of procedural non-compliance"
            },
            "evidence": {
                "keywords": ["evidence", "proof", "witness", "document", "admissible"],
                "description": "Risk of evidential difficulties"
            },
            "appeal": {
                "keywords": ["appeal", "revision", "review", "stay", "interim"],
                "description": "Risk in appellate proceedings"
            }
        }
        
        query_lower = query.lower()
        
        for category, details in procedural_categories.items():
            risk_score = 0
            relevant_authorities = []
            
            # Check query for procedural keywords
            query_mentions = sum(1 for keyword in details["keywords"] if keyword in query_lower)
            if query_mentions > 0:
                risk_score += query_mentions * 0.3
            
            # Check authorities for procedural issues
            for pack in packs:
                title = pack.get("title", "").lower()
                title_mentions = sum(1 for keyword in details["keywords"] if keyword in title)
                if title_mentions > 0:
                    risk_score += title_mentions * 0.2
                    relevant_authorities.append(pack)
            
            if risk_score > 0:
                procedural_risks.append({
                    "category": category,
                    "description": details["description"],
                    "risk_score": min(1.0, risk_score),
                    "relevant_authorities": relevant_authorities[:3],
                    "query_mentions": query_mentions
                })
        
        return procedural_risks

    def _assess_substantive_risks(self, query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess substantive legal risks"""
        
        substantive_risks = []
        
        # Substantive risk categories
        risk_categories = {
            "liability": {
                "keywords": ["liable", "responsibility", "negligence", "breach", "fault"],
                "description": "Risk of being found liable for claims"
            },
            "damages": {
                "keywords": ["damages", "compensation", "loss", "injury", "harm"],
                "description": "Risk of significant monetary liability"
            },
            "criminal": {
                "keywords": ["criminal", "offence", "prosecution", "charge", "conviction"],
                "description": "Risk of criminal liability"
            },
            "regulatory": {
                "keywords": ["compliance", "regulation", "license", "permit", "authority"],
                "description": "Risk of regulatory action or penalties"
            },
            "contractual": {
                "keywords": ["contract", "agreement", "obligation", "performance", "default"],
                "description": "Risk of contractual breach or non-performance"
            },
            "constitutional": {
                "keywords": ["constitutional", "fundamental", "rights", "article", "writ"],
                "description": "Risk involving constitutional issues"
            }
        }
        
        query_lower = query.lower()
        
        for category, details in risk_categories.items():
            risk_indicators = []
            
            # Analyze query for risk indicators
            for keyword in details["keywords"]:
                if keyword in query_lower:
                    risk_indicators.append({
                        "source": "query",
                        "indicator": keyword,
                        "context": self._extract_context(query_lower, keyword)
                    })
            
            # Analyze authorities for risk patterns
            for pack in packs:
                title = pack.get("title", "").lower()
                for keyword in details["keywords"]:
                    if keyword in title:
                        risk_indicators.append({
                            "source": "authority",
                            "indicator": keyword,
                            "authority_id": pack.get("authority_id"),
                            "title": pack.get("title"),
                            "court": pack.get("court")
                        })
            
            if risk_indicators:
                risk_level = self._calculate_risk_level(risk_indicators)
                substantive_risks.append({
                    "category": category,
                    "description": details["description"],
                    "risk_level": risk_level,
                    "indicators": risk_indicators[:5],  # Limit indicators
                    "indicator_count": len(risk_indicators)
                })
        
        return substantive_risks

    def _extract_context(self, text: str, keyword: str) -> str:
        """Extract context around a keyword"""
        
        index = text.find(keyword)
        if index == -1:
            return ""
        
        start = max(0, index - 30)
        end = min(len(text), index + len(keyword) + 30)
        return text[start:end].strip()

    def _calculate_risk_level(self, indicators: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level from indicators"""
        
        if len(indicators) >= 5:
            return "high"
        elif len(indicators) >= 3:
            return "medium"
        elif len(indicators) >= 1:
            return "low"
        else:
            return "minimal"

    def _analyze_success_probability(self, packs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze indicators of success probability"""
        
        positive_indicators = []
        negative_indicators = []
        
        positive_keywords = [
            "allow", "grant", "accept", "approve", "uphold", "confirm",
            "succeed", "win", "favor", "relief", "remedy"
        ]
        
        negative_keywords = [
            "dismiss", "reject", "deny", "refuse", "decline", "fail",
            "lose", "adverse", "against", "negative"
        ]
        
        for pack in packs:
            title = pack.get("title", "").lower()
            court = pack.get("court", "")
            
            for keyword in positive_keywords:
                if keyword in title:
                    positive_indicators.append({
                        "keyword": keyword,
                        "authority_id": pack.get("authority_id"),
                        "title": pack.get("title"),
                        "court": court,
                        "weight": self._get_court_weight(court)
                    })
            
            for keyword in negative_keywords:
                if keyword in title:
                    negative_indicators.append({
                        "keyword": keyword,
                        "authority_id": pack.get("authority_id"),
                        "title": pack.get("title"),
                        "court": court,
                        "weight": self._get_court_weight(court)
                    })
        
        # Calculate weighted scores
        positive_score = sum(indicator["weight"] for indicator in positive_indicators)
        negative_score = sum(indicator["weight"] for indicator in negative_indicators)
        
        total_score = positive_score + negative_score
        success_probability = positive_score / total_score if total_score > 0 else 0.5
        
        return {
            "success_probability": success_probability,
            "positive_indicators": positive_indicators,
            "negative_indicators": negative_indicators,
            "positive_score": positive_score,
            "negative_score": negative_score
        }

    def _get_court_weight(self, court: str) -> float:
        """Get weight based on court hierarchy"""
        
        if court == "SC":
            return 1.0
        elif court.startswith("HC-"):
            return 0.8
        elif court in ["TRIBUNAL", "COMMISSION"]:
            return 0.6
        else:
            return 0.5

    def _identify_adverse_outcomes(self, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify authorities with adverse outcomes"""
        
        adverse_outcomes = []
        
        adverse_patterns = [
            r"dismiss.*petition",
            r"reject.*application",
            r"deny.*relief",
            r"liable.*damages",
            r"breach.*contract",
            r"violation.*provisions",
            r"contempt.*court",
            r"penalty.*imposed"
        ]
        
        for pack in packs:
            title = pack.get("title", "").lower()
            
            for pattern in adverse_patterns:
                if re.search(pattern, title):
                    adverse_outcomes.append({
                        "authority_id": pack.get("authority_id"),
                        "title": pack.get("title"),
                        "court": pack.get("court"),
                        "pattern": pattern,
                        "adverse_type": self._classify_adverse_type(pattern)
                    })
                    break  # Only count once per authority
        
        return adverse_outcomes

    def _classify_adverse_type(self, pattern: str) -> str:
        """Classify type of adverse outcome"""
        
        if "dismiss" in pattern or "reject" in pattern:
            return "procedural_dismissal"
        elif "liable" in pattern or "damages" in pattern:
            return "financial_liability"
        elif "breach" in pattern or "violation" in pattern:
            return "legal_violation"
        elif "contempt" in pattern or "penalty" in pattern:
            return "punitive_action"
        else:
            return "general_adverse"

    async def _analyze_risks(self, query: str, risk_factors: List[Dict[str, Any]],
                           procedural_risks: List[Dict[str, Any]], 
                           substantive_risks: List[Dict[str, Any]],
                           success_indicators: Dict[str, Any],
                           adverse_outcomes: List[Dict[str, Any]]) -> str:
        """Perform comprehensive risk analysis using LLM"""
        
        settings = get_settings()
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build context for LLM
        context_parts = []
        
        if risk_factors:
            risk_summary = [f"{rf['type']}: {rf['factor']} ({rf['severity']})" for rf in risk_factors[:5]]
            context_parts.append(f"Risk factors identified: {'; '.join(risk_summary)}")
        
        if procedural_risks:
            proc_summary = [f"{pr['category']}: {pr['description']}" for pr in procedural_risks]
            context_parts.append(f"Procedural risks: {'; '.join(proc_summary)}")
        
        if substantive_risks:
            subst_summary = [f"{sr['category']}: {sr['risk_level']} risk" for sr in substantive_risks]
            context_parts.append(f"Substantive risks: {'; '.join(subst_summary)}")
        
        success_prob = success_indicators.get("success_probability", 0.5)
        context_parts.append(f"Success probability indicators: {success_prob:.2f} (based on precedent outcomes)")
        
        if adverse_outcomes:
            adverse_summary = [f"{ao['adverse_type']}: {ao['title'][:50]}..." for ao in adverse_outcomes[:3]]
            context_parts.append(f"Adverse precedents: {'; '.join(adverse_summary)}")
        
        context = "\n".join(context_parts) if context_parts else "Limited risk information available."
        
        prompt = f"""As a legal risk assessment specialist, analyze the potential risks and adverse outcomes for this legal matter.

Query: {query}

Risk Context:
{context}

Provide a comprehensive risk assessment covering:
1. **Risk Overview**: Summary of key risk areas and overall risk profile
2. **Procedural Risks**: Risks related to jurisdiction, procedure, timing, and compliance
3. **Substantive Risks**: Risks related to legal liability, damages, and adverse outcomes
4. **Success Probability**: Assessment of likelihood of favorable outcome based on precedents
5. **Risk Mitigation**: Strategies to minimize identified risks
6. **Worst-Case Scenarios**: Potential adverse outcomes and their consequences

Focus on:
- Quantifying risks where possible (high/medium/low)
- Specific legal consequences and their likelihood
- Procedural pitfalls and compliance requirements
- Financial exposure and liability quantum
- Strategic considerations for risk management
- Time-sensitive risk factors

Be practical and actionable. Highlight the most critical risks that need immediate attention. If risks appear manageable, explain why. If risks are severe, suggest mitigation strategies."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_GEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return content or "Unable to generate risk analysis."
            
        except Exception as e:
            log.error("risk_agent.llm_error", error=str(e))
            return f"Risk analysis based on available context: {context[:500]}..."

    def _extract_risk_sources(self, packs: List[Dict[str, Any]], 
                            risk_factors: List[Dict[str, Any]],
                            adverse_outcomes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract sources relevant to risk assessment"""
        
        sources = []
        
        # Prioritize authorities with adverse outcomes
        for outcome in adverse_outcomes:
            if outcome.get("authority_id"):
                sources.append({
                    "authority_id": outcome["authority_id"],
                    "para_ids": [],  # Will be filled by retrieval
                    "relevance": "adverse_outcome",
                    "title": outcome["title"],
                    "court": outcome["court"],
                    "risk_type": outcome["adverse_type"]
                })
        
        # Add authorities mentioned in risk factors
        for factor in risk_factors:
            if factor.get("authority_id") and factor["authority_id"] not in [s["authority_id"] for s in sources]:
                sources.append({
                    "authority_id": factor["authority_id"],
                    "para_ids": [],
                    "relevance": "risk_factor",
                    "title": factor.get("title", ""),
                    "court": factor.get("court", ""),
                    "risk_type": factor["type"]
                })
        
        # Fill remaining slots with other authorities
        for pack in packs:
            if len(sources) >= 5:
                break
            authority_id = pack.get("authority_id")
            if authority_id and authority_id not in [s["authority_id"] for s in sources]:
                para_ids = [p.get("para_id", 0) for p in pack.get("paras", [])]
                sources.append({
                    "authority_id": authority_id,
                    "para_ids": para_ids,
                    "relevance": "general",
                    "title": pack.get("title", ""),
                    "court": pack.get("court", ""),
                    "risk_type": "general"
                })
        
        return sources

    def _calculate_confidence(self, risk_factors: List[Dict[str, Any]],
                            procedural_risks: List[Dict[str, Any]],
                            substantive_risks: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on risk assessment completeness"""
        
        base_confidence = 0.4  # Base confidence for risk assessment
        
        # Boost for identified risk factors
        if risk_factors:
            base_confidence += min(0.3, len(risk_factors) * 0.05)
        
        # Boost for procedural risk analysis
        if procedural_risks:
            base_confidence += min(0.2, len(procedural_risks) * 0.05)
        
        # Boost for substantive risk analysis
        if substantive_risks:
            base_confidence += min(0.2, len(substantive_risks) * 0.05)
        
        # Boost for high-severity risks (more specific analysis)
        high_severity_count = sum(1 for rf in risk_factors if rf.get("severity") == "high")
        if high_severity_count > 0:
            base_confidence += min(0.15, high_severity_count * 0.05)
        
        return min(0.90, base_confidence)  # Cap at 90% for risk assessment
