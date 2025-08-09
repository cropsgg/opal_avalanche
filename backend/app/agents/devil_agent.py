from __future__ import annotations

import re
from typing import Any, Dict, List
import structlog

from openai import OpenAI
from app.core.config import get_settings
from app.agents.base import AgentOutput

log = structlog.get_logger()


class DevilAgent:
    name = "devil"

    async def run(self, query: str, packs: List[Dict[str, Any]], matter_docs: List[Dict[str, Any]]) -> AgentOutput:
        """
        Present counterarguments and challenge the primary position
        Focus on weaknesses, alternative interpretations, and opposing precedents
        """
        
        log.info("devil_agent.start", query_length=len(query))
        
        # Identify potential counterarguments
        counterarguments = self._identify_counterarguments(query, packs)
        
        # Find opposing precedents and interpretations
        opposing_precedents = self._find_opposing_precedents(packs)
        
        # Identify weaknesses in the position
        weaknesses = self._identify_position_weaknesses(query, packs)
        
        # Find alternative legal interpretations
        alternative_interpretations = self._find_alternative_interpretations(query, packs)
        
        # Build comprehensive devil's advocate analysis
        reasoning = await self._analyze_counterposition(query, counterarguments, opposing_precedents,
                                                      weaknesses, alternative_interpretations)
        
        sources = self._extract_counterargument_sources(packs, opposing_precedents, counterarguments)
        confidence = self._calculate_confidence(counterarguments, opposing_precedents, weaknesses)
        
        log.info("devil_agent.complete",
                confidence=confidence,
                counterarguments=len(counterarguments),
                opposing_precedents=len(opposing_precedents),
                weaknesses=len(weaknesses))
        
        return AgentOutput(
            reasoning=reasoning,
            sources=sources,
            confidence=confidence
        )

    def _identify_counterarguments(self, query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential counterarguments to the query position"""
        
        counterarguments = []
        
        # Analyze query for implicit position
        query_position = self._extract_query_position(query)
        
        # Common legal counterargument patterns
        counterargument_categories = {
            "procedural_defects": {
                "triggers": ["file", "apply", "seek", "petition", "claim"],
                "counters": ["jurisdiction", "limitation", "locus standi", "procedure", "maintainability"]
            },
            "substantive_challenges": {
                "triggers": ["liable", "responsible", "breach", "violation"],
                "counters": ["no duty", "no causation", "defence", "exception", "justification"]
            },
            "evidentiary_challenges": {
                "triggers": ["prove", "evidence", "show", "establish"],
                "counters": ["burden of proof", "insufficient evidence", "hearsay", "inadmissible"]
            },
            "alternative_interpretations": {
                "triggers": ["means", "interpret", "construction", "provision"],
                "counters": ["plain meaning", "legislative intent", "contextual interpretation", "harmonious construction"]
            },
            "policy_arguments": {
                "triggers": ["public interest", "policy", "welfare", "justice"],
                "counters": ["competing interests", "unintended consequences", "precedent implications", "judicial restraint"]
            }
        }
        
        query_lower = query.lower()
        
        for category, patterns in counterargument_categories.items():
            # Check if query contains trigger words
            triggers_found = [trigger for trigger in patterns["triggers"] if trigger in query_lower]
            
            if triggers_found:
                for counter in patterns["counters"]:
                    counterarguments.append({
                        "category": category,
                        "trigger": triggers_found[0],
                        "counterargument": counter,
                        "description": f"Challenge based on {counter}",
                        "source": "pattern_analysis"
                    })
        
        # Look for counterarguments in authority titles
        counter_keywords = [
            "distinguish", "not applicable", "exception", "limited to",
            "overrule", "contrary", "different", "distinguish",
            "inapplicable", "distinguishable", "factually different"
        ]
        
        for pack in packs:
            title = pack.get("title", "").lower()
            for keyword in counter_keywords:
                if keyword in title:
                    counterarguments.append({
                        "category": "precedent_challenge",
                        "counterargument": keyword,
                        "description": f"Authority suggests {keyword}",
                        "source": "authority",
                        "authority_id": pack.get("authority_id"),
                        "title": pack.get("title"),
                        "court": pack.get("court")
                    })
        
        return counterarguments

    def _extract_query_position(self, query: str) -> Dict[str, Any]:
        """Extract the implicit position or stance from the query"""
        
        query_lower = query.lower()
        
        # Identify position indicators
        positive_indicators = ["can", "should", "entitled", "right", "liable", "valid", "legal"]
        negative_indicators = ["cannot", "should not", "not entitled", "no right", "not liable", "invalid", "illegal"]
        
        position_strength = 0
        indicators_found = []
        
        for indicator in positive_indicators:
            if indicator in query_lower:
                position_strength += 1
                indicators_found.append(("positive", indicator))
        
        for indicator in negative_indicators:
            if indicator in query_lower:
                position_strength -= 1
                indicators_found.append(("negative", indicator))
        
        return {
            "strength": position_strength,
            "indicators": indicators_found,
            "likely_position": "positive" if position_strength > 0 else "negative" if position_strength < 0 else "neutral"
        }

    def _find_opposing_precedents(self, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find precedents that might oppose the primary position"""
        
        opposing_precedents = []
        
        # Keywords indicating opposing or limiting precedents
        opposing_keywords = [
            "dismiss", "reject", "deny", "refuse", "decline",
            "not liable", "no cause", "insufficient", "fail",
            "distinguish", "overrule", "limited", "narrow",
            "exception", "special circumstances", "factually different"
        ]
        
        for pack in packs:
            title = pack.get("title", "").lower()
            court = pack.get("court", "")
            
            opposition_score = 0
            opposing_terms = []
            
            for keyword in opposing_keywords:
                if keyword in title:
                    opposition_score += 1
                    opposing_terms.append(keyword)
            
            if opposition_score > 0:
                opposing_precedents.append({
                    "authority_id": pack.get("authority_id"),
                    "title": pack.get("title"),
                    "court": court,
                    "opposition_score": opposition_score,
                    "opposing_terms": opposing_terms,
                    "neutral_cite": pack.get("neutral_cite"),
                    "reporter_cite": pack.get("reporter_cite"),
                    "precedential_weight": self._get_precedential_weight(court)
                })
        
        # Sort by opposition score and precedential weight
        opposing_precedents.sort(key=lambda x: (x["opposition_score"], x["precedential_weight"]), reverse=True)
        
        return opposing_precedents

    def _get_precedential_weight(self, court: str) -> float:
        """Get precedential weight of court"""
        
        if court == "SC":
            return 1.0
        elif court.startswith("HC-"):
            return 0.8
        elif court in ["TRIBUNAL", "COMMISSION"]:
            return 0.6
        else:
            return 0.5

    def _identify_position_weaknesses(self, query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential weaknesses in the legal position"""
        
        weaknesses = []
        
        # Common legal position weaknesses
        weakness_categories = {
            "factual_weaknesses": {
                "indicators": ["facts", "evidence", "proof", "witness", "document"],
                "description": "Potential factual or evidentiary weaknesses"
            },
            "legal_precedent_gaps": {
                "indicators": ["no precedent", "novel", "first", "unclear", "ambiguous"],
                "description": "Lack of clear precedential support"
            },
            "procedural_vulnerabilities": {
                "indicators": ["procedure", "jurisdiction", "limitation", "locus standi"],
                "description": "Procedural challenges and technicalities"
            },
            "policy_concerns": {
                "indicators": ["policy", "consequences", "implications", "public interest"],
                "description": "Policy arguments against the position"
            },
            "alternative_remedies": {
                "indicators": ["alternative", "other remedy", "different approach"],
                "description": "Availability of alternative legal remedies"
            }
        }
        
        query_lower = query.lower()
        
        for category, details in weakness_categories.items():
            weakness_score = 0
            relevant_terms = []
            
            for indicator in details["indicators"]:
                if indicator in query_lower:
                    weakness_score += 1
                    relevant_terms.append(indicator)
            
            # Check authorities for weakness indicators
            for pack in packs:
                title = pack.get("title", "").lower()
                for indicator in details["indicators"]:
                    if indicator in title:
                        weakness_score += 0.5
                        if pack.get("authority_id") not in [t for t in relevant_terms if isinstance(t, dict)]:
                            relevant_terms.append({
                                "authority_id": pack.get("authority_id"),
                                "title": pack.get("title")
                            })
            
            if weakness_score > 0:
                weaknesses.append({
                    "category": category,
                    "description": details["description"],
                    "weakness_score": weakness_score,
                    "relevant_terms": relevant_terms,
                    "severity": "high" if weakness_score >= 2 else "medium" if weakness_score >= 1 else "low"
                })
        
        return weaknesses

    def _find_alternative_interpretations(self, query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find alternative legal interpretations"""
        
        alternatives = []
        
        # Look for interpretation-related authorities
        interpretation_keywords = [
            "interpret", "construction", "meaning", "scope", "extent",
            "plain meaning", "literal", "purposive", "harmonious",
            "contextual", "legislative intent", "parliamentary intent"
        ]
        
        for pack in packs:
            title = pack.get("title", "").lower()
            
            interpretation_score = 0
            interpretation_types = []
            
            for keyword in interpretation_keywords:
                if keyword in title:
                    interpretation_score += 1
                    interpretation_types.append(keyword)
            
            if interpretation_score > 0:
                alternatives.append({
                    "authority_id": pack.get("authority_id"),
                    "title": pack.get("title"),
                    "court": pack.get("court"),
                    "interpretation_score": interpretation_score,
                    "interpretation_types": interpretation_types,
                    "description": f"Alternative interpretation based on {', '.join(interpretation_types)}"
                })
        
        # Look for conflicting interpretations
        conflict_patterns = [
            r"differ.*interpretation",
            r"contrary.*view",
            r"alternative.*approach",
            r"different.*construction",
            r"competing.*interpretations"
        ]
        
        for pack in packs:
            title = pack.get("title", "").lower()
            for pattern in conflict_patterns:
                if re.search(pattern, title):
                    alternatives.append({
                        "authority_id": pack.get("authority_id"),
                        "title": pack.get("title"),
                        "court": pack.get("court"),
                        "conflict_type": pattern,
                        "description": "Authority suggests conflicting interpretation"
                    })
        
        return alternatives

    async def _analyze_counterposition(self, query: str, counterarguments: List[Dict[str, Any]],
                                     opposing_precedents: List[Dict[str, Any]],
                                     weaknesses: List[Dict[str, Any]],
                                     alternative_interpretations: List[Dict[str, Any]]) -> str:
        """Perform comprehensive devil's advocate analysis using LLM"""
        
        settings = get_settings()
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build context for LLM
        context_parts = []
        
        if counterarguments:
            counter_summary = [f"{ca['category']}: {ca['counterargument']}" for ca in counterarguments[:5]]
            context_parts.append(f"Potential counterarguments: {'; '.join(counter_summary)}")
        
        if opposing_precedents:
            opposing_summary = [f"{op['title']} (court: {op['court']}, terms: {', '.join(op['opposing_terms'])})" 
                              for op in opposing_precedents[:3]]
            context_parts.append(f"Opposing precedents: {'; '.join(opposing_summary)}")
        
        if weaknesses:
            weakness_summary = [f"{w['category']}: {w['description']} ({w['severity']})" for w in weaknesses]
            context_parts.append(f"Position weaknesses: {'; '.join(weakness_summary)}")
        
        if alternative_interpretations:
            alt_summary = [f"{ai['description']}" for ai in alternative_interpretations[:3]]
            context_parts.append(f"Alternative interpretations: {'; '.join(alt_summary)}")
        
        context = "\n".join(context_parts) if context_parts else "Limited counterargument information available."
        
        prompt = f"""As a devil's advocate legal analyst, challenge the position implied in this query and present the strongest counterarguments.

Query: {query}

Counterargument Context:
{context}

Provide a thorough devil's advocate analysis covering:
1. **Strongest Counterarguments**: Most compelling arguments against the implied position
2. **Opposing Precedents**: Case law that contradicts or limits the position
3. **Procedural Challenges**: Technical and procedural obstacles
4. **Factual/Evidentiary Weaknesses**: Potential problems with proof or evidence
5. **Alternative Legal Interpretations**: Different ways to interpret relevant law
6. **Policy Counterarguments**: Broader policy reasons against the position

Focus on:
- Genuine legal obstacles and challenges
- Precedents that distinguish or limit favorable cases
- Procedural technicalities that could defeat the claim
- Burden of proof and evidentiary challenges
- Alternative constructions of statutes/precedents
- Practical and policy considerations

Be rigorous and intellectually honest. Present the opposition's best case, not strawman arguments. Identify the most serious challenges that need to be addressed. If counterarguments are weak, explain why. If they are strong, highlight the key vulnerabilities."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_GEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,  # Slightly higher for creative counterarguments
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return content or "Unable to generate counterargument analysis."
            
        except Exception as e:
            log.error("devil_agent.llm_error", error=str(e))
            return f"Counterargument analysis based on available context: {context[:500]}..."

    def _extract_counterargument_sources(self, packs: List[Dict[str, Any]], 
                                       opposing_precedents: List[Dict[str, Any]],
                                       counterarguments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract sources that support counterarguments"""
        
        sources = []
        
        # Prioritize opposing precedents
        for precedent in opposing_precedents[:3]:
            if precedent.get("authority_id"):
                sources.append({
                    "authority_id": precedent["authority_id"],
                    "para_ids": [],  # Will be filled by retrieval
                    "relevance": "opposing_precedent",
                    "title": precedent["title"],
                    "court": precedent["court"],
                    "opposition_score": precedent["opposition_score"],
                    "opposing_terms": precedent["opposing_terms"]
                })
        
        # Add authorities mentioned in counterarguments
        for counter in counterarguments:
            if counter.get("authority_id") and counter["authority_id"] not in [s["authority_id"] for s in sources]:
                sources.append({
                    "authority_id": counter["authority_id"],
                    "para_ids": [],
                    "relevance": "counterargument_support",
                    "title": counter.get("title", ""),
                    "court": counter.get("court", ""),
                    "counterargument_type": counter["category"]
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
                    "relevance": "general_context",
                    "title": pack.get("title", ""),
                    "court": pack.get("court", "")
                })
        
        return sources

    def _calculate_confidence(self, counterarguments: List[Dict[str, Any]],
                            opposing_precedents: List[Dict[str, Any]],
                            weaknesses: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on strength of counterarguments found"""
        
        base_confidence = 0.3
        
        # Boost for identified counterarguments
        if counterarguments:
            base_confidence += min(0.3, len(counterarguments) * 0.04)
        
        # Strong boost for opposing precedents (especially from higher courts)
        if opposing_precedents:
            precedent_boost = 0
            for precedent in opposing_precedents:
                weight = precedent["precedential_weight"]
                score = precedent["opposition_score"]
                precedent_boost += weight * score * 0.08
            base_confidence += min(0.4, precedent_boost)
        
        # Boost for identified weaknesses
        if weaknesses:
            weakness_boost = 0
            for weakness in weaknesses:
                severity_multiplier = {"high": 0.1, "medium": 0.06, "low": 0.03}
                weakness_boost += severity_multiplier.get(weakness["severity"], 0.03)
            base_confidence += min(0.2, weakness_boost)
        
        # Extra boost if multiple categories of challenges found
        challenge_categories = set()
        if counterarguments:
            challenge_categories.update([ca["category"] for ca in counterarguments])
        if weaknesses:
            challenge_categories.update([w["category"] for w in weaknesses])
        
        if len(challenge_categories) >= 3:
            base_confidence += 0.15  # Comprehensive challenge analysis
        
        return min(0.90, base_confidence)  # Cap at 90% for devil's advocate role
