from __future__ import annotations

import re
from typing import Any, Dict, List
import structlog

from openai import OpenAI
from app.core.config import get_settings
from app.agents.base import AgentOutput

log = structlog.get_logger()


class EthicsAgent:
    name = "ethics"

    async def run(self, query: str, packs: List[Dict[str, Any]], matter_docs: List[Dict[str, Any]]) -> AgentOutput:
        """
        Analyze professional conduct, ethical considerations, and Bar Council rules
        Focus on advocate duties, conflict of interest, and professional standards
        """
        
        log.info("ethics_agent.start", query_length=len(query))
        
        # Identify ethical issues and considerations
        ethical_issues = self._identify_ethical_issues(query, packs)
        
        # Check for conflict of interest indicators
        conflict_indicators = self._check_conflict_indicators(query, packs, matter_docs)
        
        # Analyze professional conduct requirements
        conduct_requirements = self._analyze_conduct_requirements(query, packs)
        
        # Check Bar Council rules and regulations
        bar_council_rules = self._check_bar_council_rules(query, packs)
        
        # Identify disclosure and transparency requirements
        disclosure_requirements = self._identify_disclosure_requirements(query, packs)
        
        # Build comprehensive ethics analysis
        reasoning = await self._analyze_ethics(query, ethical_issues, conflict_indicators,
                                             conduct_requirements, bar_council_rules, disclosure_requirements)
        
        sources = self._extract_ethics_sources(packs, ethical_issues, bar_council_rules)
        confidence = self._calculate_confidence(ethical_issues, conflict_indicators, conduct_requirements)
        
        log.info("ethics_agent.complete",
                confidence=confidence,
                ethical_issues=len(ethical_issues),
                conflict_indicators=len(conflict_indicators),
                conduct_requirements=len(conduct_requirements))
        
        return AgentOutput(
            reasoning=reasoning,
            sources=sources,
            confidence=confidence
        )

    def _identify_ethical_issues(self, query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential ethical issues from query and authorities"""
        
        ethical_issues = []
        
        # Common ethical issue categories
        ethical_categories = {
            "conflict_of_interest": {
                "keywords": ["conflict", "interest", "adverse", "opposing", "client", "former client"],
                "description": "Potential conflict of interest with current or former clients"
            },
            "confidentiality": {
                "keywords": ["confidential", "privilege", "secret", "disclosure", "information"],
                "description": "Attorney-client privilege and confidentiality obligations"
            },
            "competence": {
                "keywords": ["competent", "qualified", "expertise", "knowledge", "skill"],
                "description": "Duty to provide competent representation"
            },
            "diligence": {
                "keywords": ["diligent", "promptly", "reasonable effort", "delay", "neglect"],
                "description": "Duty of diligence and prompt representation"
            },
            "truthfulness": {
                "keywords": ["false", "misleading", "misrepresent", "truth", "candor"],
                "description": "Duty of truthfulness to courts and clients"
            },
            "fees": {
                "keywords": ["fee", "reasonable", "excessive", "contingent", "payment"],
                "description": "Reasonable fees and fee arrangements"
            },
            "solicitation": {
                "keywords": ["solicit", "advertise", "barratry", "champerty", "maintenance"],
                "description": "Rules against improper solicitation and advertising"
            },
            "court_conduct": {
                "keywords": ["court", "judge", "respect", "dignity", "contempt", "professional"],
                "description": "Professional conduct before courts and tribunals"
            }
        }
        
        query_lower = query.lower()
        
        # Check query for ethical keywords
        for category, details in ethical_categories.items():
            issue_score = 0
            relevant_keywords = []
            
            for keyword in details["keywords"]:
                if keyword in query_lower:
                    issue_score += 1
                    relevant_keywords.append(keyword)
            
            if issue_score > 0:
                ethical_issues.append({
                    "category": category,
                    "description": details["description"],
                    "issue_score": issue_score,
                    "relevant_keywords": relevant_keywords,
                    "source": "query",
                    "severity": self._assess_ethical_severity(category, issue_score)
                })
        
        # Check authorities for ethical issues
        for pack in packs:
            title = pack.get("title", "").lower()
            
            for category, details in ethical_categories.items():
                for keyword in details["keywords"]:
                    if keyword in title:
                        ethical_issues.append({
                            "category": category,
                            "description": details["description"],
                            "source": "authority",
                            "authority_id": pack.get("authority_id"),
                            "title": pack.get("title"),
                            "court": pack.get("court"),
                            "severity": "medium"
                        })
                        break  # Only add once per authority per category
        
        return ethical_issues

    def _assess_ethical_severity(self, category: str, score: int) -> str:
        """Assess severity of ethical issue"""
        
        high_risk_categories = ["conflict_of_interest", "confidentiality", "truthfulness"]
        
        if category in high_risk_categories:
            return "high" if score >= 2 else "medium"
        else:
            return "medium" if score >= 2 else "low"

    def _check_conflict_indicators(self, query: str, packs: List[Dict[str, Any]], 
                                 matter_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for conflict of interest indicators"""
        
        conflict_indicators = []
        
        # Conflict patterns in query
        conflict_patterns = {
            "adverse_parties": {
                "patterns": [r"against.*client", r"oppose.*client", r"adverse.*to"],
                "description": "Representation adverse to current or former client"
            },
            "same_matter": {
                "patterns": [r"same.*matter", r"related.*matter", r"substantially.*related"],
                "description": "Representation in same or substantially related matter"
            },
            "confidential_info": {
                "patterns": [r"confidential.*information", r"privileged.*information", r"client.*secret"],
                "description": "Use of confidential information from former client"
            },
            "family_relation": {
                "patterns": [r"family.*member", r"spouse", r"relative", r"personal.*interest"],
                "description": "Personal or family relationship creating conflict"
            },
            "financial_interest": {
                "patterns": [r"financial.*interest", r"business.*relationship", r"investment"],
                "description": "Financial interest in subject matter"
            }
        }
        
        query_lower = query.lower()
        
        for conflict_type, details in conflict_patterns.items():
            for pattern in details["patterns"]:
                if re.search(pattern, query_lower):
                    conflict_indicators.append({
                        "type": conflict_type,
                        "description": details["description"],
                        "pattern": pattern,
                        "source": "query",
                        "risk_level": self._assess_conflict_risk(conflict_type)
                    })
        
        # Check for conflict indicators in matter documents
        # This is a simplified check - real implementation would need more sophisticated analysis
        for doc in matter_docs:
            doc_info = doc.get("content", "").lower() if isinstance(doc.get("content"), str) else ""
            
            if any(term in doc_info for term in ["former client", "adverse party", "conflict"]):
                conflict_indicators.append({
                    "type": "document_indicator",
                    "description": "Potential conflict indicated in matter documents",
                    "source": "matter_document",
                    "risk_level": "medium"
                })
        
        return conflict_indicators

    def _assess_conflict_risk(self, conflict_type: str) -> str:
        """Assess risk level of conflict type"""
        
        high_risk = ["adverse_parties", "same_matter", "confidential_info"]
        medium_risk = ["family_relation", "financial_interest"]
        
        if conflict_type in high_risk:
            return "high"
        elif conflict_type in medium_risk:
            return "medium"
        else:
            return "low"

    def _analyze_conduct_requirements(self, query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze professional conduct requirements"""
        
        conduct_requirements = []
        
        # Professional conduct standards
        conduct_standards = {
            "zealous_advocacy": {
                "indicators": ["represent", "advocate", "defend", "pursue"],
                "requirement": "Duty to zealously advocate within bounds of law",
                "rule_reference": "Professional Standards Rule 1.1"
            },
            "client_communication": {
                "indicators": ["inform", "communicate", "update", "consult"],
                "requirement": "Duty to keep client informed and communicate effectively",
                "rule_reference": "Professional Standards Rule 1.4"
            },
            "confidentiality_duty": {
                "indicators": ["confidential", "secret", "privilege", "disclose"],
                "requirement": "Duty to maintain client confidentiality",
                "rule_reference": "Professional Standards Rule 1.6"
            },
            "competent_representation": {
                "indicators": ["competent", "knowledge", "skill", "thorough"],
                "requirement": "Duty to provide competent representation",
                "rule_reference": "Professional Standards Rule 1.1"
            },
            "avoid_conflicts": {
                "indicators": ["conflict", "adverse", "interest", "impaired"],
                "requirement": "Duty to avoid conflicts of interest",
                "rule_reference": "Professional Standards Rule 1.7"
            },
            "court_candor": {
                "indicators": ["court", "tribunal", "judge", "false", "misleading"],
                "requirement": "Duty of candor to tribunal",
                "rule_reference": "Professional Standards Rule 3.3"
            }
        }
        
        query_lower = query.lower()
        
        for standard, details in conduct_standards.items():
            relevance_score = 0
            relevant_indicators = []
            
            for indicator in details["indicators"]:
                if indicator in query_lower:
                    relevance_score += 1
                    relevant_indicators.append(indicator)
            
            # Check authorities for conduct references
            for pack in packs:
                title = pack.get("title", "").lower()
                for indicator in details["indicators"]:
                    if indicator in title:
                        relevance_score += 0.5
                        break
            
            if relevance_score > 0:
                conduct_requirements.append({
                    "standard": standard,
                    "requirement": details["requirement"],
                    "rule_reference": details["rule_reference"],
                    "relevance_score": relevance_score,
                    "relevant_indicators": relevant_indicators,
                    "applicability": "high" if relevance_score >= 2 else "medium" if relevance_score >= 1 else "low"
                })
        
        return conduct_requirements

    def _check_bar_council_rules(self, query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check applicable Bar Council rules and regulations"""
        
        bar_rules = []
        
        # Common Bar Council of India rules and their applications
        bci_rules = {
            "Rule 6": {
                "subject": "Standards of Professional Conduct and Etiquette",
                "keywords": ["conduct", "etiquette", "professional", "behavior"],
                "description": "General standards of professional conduct"
            },
            "Rule 7": {
                "subject": "Restriction on Practice",
                "keywords": ["practice", "restriction", "business", "trade"],
                "description": "Restrictions on carrying on business while practicing law"
            },
            "Rule 8": {
                "subject": "Contempt of Court",
                "keywords": ["contempt", "court", "disrespect", "dignity"],
                "description": "Avoiding contempt of court and maintaining court dignity"
            },
            "Rule 9": {
                "subject": "Misconduct in Relation to the Courts",
                "keywords": ["misconduct", "court", "false", "misleading"],
                "description": "Professional misconduct in relation to courts"
            },
            "Rule 11": {
                "subject": "Misconduct in Relation to Clients",
                "keywords": ["client", "misconduct", "fee", "money", "property"],
                "description": "Professional misconduct in relation to clients"
            },
            "Rule 15": {
                "subject": "Advertising and Solicitation",
                "keywords": ["advertise", "solicit", "publicity", "tout"],
                "description": "Restrictions on advertising and solicitation"
            },
            "Rule 20": {
                "subject": "Conflict of Interest",
                "keywords": ["conflict", "interest", "adverse", "client"],
                "description": "Rules regarding conflict of interest"
            }
        }
        
        query_lower = query.lower()
        
        for rule_num, rule_details in bci_rules.items():
            rule_relevance = 0
            matching_keywords = []
            
            for keyword in rule_details["keywords"]:
                if keyword in query_lower:
                    rule_relevance += 1
                    matching_keywords.append(keyword)
            
            # Check authorities for rule references
            for pack in packs:
                title = pack.get("title", "").lower()
                if rule_num.lower() in title or rule_details["subject"].lower() in title:
                    rule_relevance += 1
                    break
            
            if rule_relevance > 0:
                bar_rules.append({
                    "rule_number": rule_num,
                    "subject": rule_details["subject"],
                    "description": rule_details["description"],
                    "relevance_score": rule_relevance,
                    "matching_keywords": matching_keywords,
                    "applicability": "high" if rule_relevance >= 2 else "medium"
                })
        
        return bar_rules

    def _identify_disclosure_requirements(self, query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify disclosure and transparency requirements"""
        
        disclosure_requirements = []
        
        # Types of disclosures required
        disclosure_types = {
            "conflict_disclosure": {
                "triggers": ["conflict", "interest", "adverse", "related"],
                "requirement": "Disclose conflicts of interest to clients",
                "when": "Before representation begins or when conflict arises"
            },
            "fee_disclosure": {
                "triggers": ["fee", "cost", "expense", "billing"],
                "requirement": "Disclose fee structure and arrangements",
                "when": "At commencement of representation"
            },
            "scope_disclosure": {
                "triggers": ["scope", "limited", "representation", "responsibility"],
                "requirement": "Disclose scope and limitations of representation",
                "when": "At commencement of representation"
            },
            "risk_disclosure": {
                "triggers": ["risk", "likelihood", "probability", "outcome"],
                "requirement": "Disclose material risks and likely outcomes",
                "when": "During representation as circumstances develop"
            },
            "settlement_disclosure": {
                "triggers": ["settle", "settlement", "offer", "negotiate"],
                "requirement": "Disclose settlement offers and terms",
                "when": "Promptly upon receipt"
            }
        }
        
        query_lower = query.lower()
        
        for disclosure_type, details in disclosure_types.items():
            trigger_count = 0
            relevant_triggers = []
            
            for trigger in details["triggers"]:
                if trigger in query_lower:
                    trigger_count += 1
                    relevant_triggers.append(trigger)
            
            if trigger_count > 0:
                disclosure_requirements.append({
                    "type": disclosure_type,
                    "requirement": details["requirement"],
                    "when": details["when"],
                    "trigger_count": trigger_count,
                    "relevant_triggers": relevant_triggers,
                    "urgency": "immediate" if trigger_count >= 2 else "routine"
                })
        
        return disclosure_requirements

    async def _analyze_ethics(self, query: str, ethical_issues: List[Dict[str, Any]],
                            conflict_indicators: List[Dict[str, Any]],
                            conduct_requirements: List[Dict[str, Any]],
                            bar_council_rules: List[Dict[str, Any]],
                            disclosure_requirements: List[Dict[str, Any]]) -> str:
        """Perform comprehensive ethics analysis using LLM"""
        
        settings = get_settings()
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build context for LLM
        context_parts = []
        
        if ethical_issues:
            ethics_summary = [f"{ei['category']}: {ei['description']} ({ei.get('severity', 'medium')})" 
                            for ei in ethical_issues[:5]]
            context_parts.append(f"Ethical issues identified: {'; '.join(ethics_summary)}")
        
        if conflict_indicators:
            conflict_summary = [f"{ci['type']}: {ci['description']} (risk: {ci['risk_level']})" 
                              for ci in conflict_indicators]
            context_parts.append(f"Conflict indicators: {'; '.join(conflict_summary)}")
        
        if conduct_requirements:
            conduct_summary = [f"{cr['standard']}: {cr['requirement']}" for cr in conduct_requirements]
            context_parts.append(f"Professional conduct requirements: {'; '.join(conduct_summary)}")
        
        if bar_council_rules:
            rules_summary = [f"{br['rule_number']}: {br['subject']}" for br in bar_council_rules]
            context_parts.append(f"Applicable Bar Council rules: {'; '.join(rules_summary)}")
        
        if disclosure_requirements:
            disclosure_summary = [f"{dr['type']}: {dr['requirement']}" for dr in disclosure_requirements]
            context_parts.append(f"Disclosure requirements: {'; '.join(disclosure_summary)}")
        
        context = "\n".join(context_parts) if context_parts else "No specific ethical issues identified."
        
        prompt = f"""As a legal ethics specialist, analyze the professional conduct and ethical considerations for this legal matter.

Query: {query}

Ethics Context:
{context}

Provide a comprehensive ethical analysis covering:
1. **Professional Conduct Standards**: Applicable standards and requirements
2. **Conflict of Interest**: Any potential conflicts and required actions
3. **Client Duties**: Duties owed to clients (competence, diligence, communication, confidentiality)
4. **Court Duties**: Duties owed to courts and tribunals (candor, respect, compliance)
5. **Bar Council Rules**: Applicable BCI rules and professional standards
6. **Required Disclosures**: Information that must be disclosed to clients or courts
7. **Risk Management**: Steps to ensure ethical compliance

Focus on:
- Specific ethical rules and their application
- Required actions to maintain compliance
- Potential disciplinary risks and consequences
- Best practices for ethical representation
- Documentation and disclosure requirements
- Conflict resolution and management strategies

Be practical and specific about compliance steps. If ethical issues are identified, provide clear guidance on resolution. If the matter appears ethically straightforward, confirm compliance requirements."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_GEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # Low temperature for precise ethical guidance
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return content or "Unable to generate ethics analysis."
            
        except Exception as e:
            log.error("ethics_agent.llm_error", error=str(e))
            return f"Ethics analysis based on available context: {context[:500]}..."

    def _extract_ethics_sources(self, packs: List[Dict[str, Any]], 
                              ethical_issues: List[Dict[str, Any]],
                              bar_council_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract sources relevant to ethics analysis"""
        
        sources = []
        
        # Add authorities mentioned in ethical issues
        for issue in ethical_issues:
            if issue.get("authority_id"):
                sources.append({
                    "authority_id": issue["authority_id"],
                    "para_ids": [],
                    "relevance": "ethical_issue",
                    "title": issue.get("title", ""),
                    "court": issue.get("court", ""),
                    "ethical_category": issue["category"]
                })
        
        # Add ethics-related authorities
        ethics_keywords = ["professional conduct", "bar council", "ethics", "misconduct", "discipline"]
        
        for pack in packs:
            title = pack.get("title", "").lower()
            if any(keyword in title for keyword in ethics_keywords):
                authority_id = pack.get("authority_id")
                if authority_id and authority_id not in [s["authority_id"] for s in sources]:
                    para_ids = [p.get("para_id", 0) for p in pack.get("paras", [])]
                    sources.append({
                        "authority_id": authority_id,
                        "para_ids": para_ids,
                        "relevance": "ethics_related",
                        "title": pack.get("title", ""),
                        "court": pack.get("court", "")
                    })
        
        # Fill remaining slots with general authorities
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
                    "court": pack.get("court", "")
                })
        
        return sources

    def _calculate_confidence(self, ethical_issues: List[Dict[str, Any]],
                            conflict_indicators: List[Dict[str, Any]],
                            conduct_requirements: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on ethics analysis completeness"""
        
        base_confidence = 0.5  # Base confidence for ethics analysis
        
        # Boost for identified ethical issues (more specific analysis)
        if ethical_issues:
            ethics_boost = min(0.3, len(ethical_issues) * 0.06)
            base_confidence += ethics_boost
            
            # Extra boost for high-severity issues (more critical analysis)
            high_severity_count = sum(1 for ei in ethical_issues if ei.get("severity") == "high")
            if high_severity_count > 0:
                base_confidence += min(0.15, high_severity_count * 0.05)
        
        # Boost for conflict analysis
        if conflict_indicators:
            conflict_boost = min(0.25, len(conflict_indicators) * 0.08)
            base_confidence += conflict_boost
        
        # Boost for conduct requirements analysis
        if conduct_requirements:
            conduct_boost = min(0.2, len(conduct_requirements) * 0.04)
            base_confidence += conduct_boost
        
        # Penalty if no ethical considerations found (might indicate incomplete analysis)
        if not (ethical_issues or conflict_indicators or conduct_requirements):
            base_confidence *= 0.7
        
        return min(0.90, base_confidence)  # Cap at 90% for ethics analysis
