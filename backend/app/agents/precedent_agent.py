from __future__ import annotations

import re
from typing import Any, Dict, List
import structlog

from openai import OpenAI
from app.core.config import get_settings
from app.agents.base import AgentOutput

log = structlog.get_logger()


class PrecedentAgent:
    name = "precedent"

    async def run(self, query: str, packs: List[Dict[str, Any]], matter_docs: List[Dict[str, Any]]) -> AgentOutput:
        """
        Analyze precedents and case law relevant to the query
        Focus on binding vs persuasive precedents, ratio decidendi, and legal principles
        """
        
        log.info("precedent_agent.start", query_length=len(query))
        
        # Analyze case law hierarchy and precedential value
        precedent_analysis = self._analyze_precedent_hierarchy(packs)
        
        # Extract legal principles and ratios
        legal_principles = self._extract_legal_principles(packs)
        
        # Check for conflicting precedents
        conflicts = self._detect_precedent_conflicts(packs)
        
        # Build comprehensive precedent analysis
        reasoning = await self._analyze_precedents(query, precedent_analysis, legal_principles, conflicts)
        
        # Extract sources with precedential weight
        sources = self._extract_precedent_sources(packs, precedent_analysis)
        confidence = self._calculate_confidence(precedent_analysis, legal_principles, conflicts)
        
        log.info("precedent_agent.complete",
                confidence=confidence,
                binding_precedents=precedent_analysis["binding_count"],
                persuasive_precedents=precedent_analysis["persuasive_count"],
                conflicts_detected=len(conflicts))
        
        return AgentOutput(
            reasoning=reasoning,
            sources=sources,
            confidence=confidence
        )

    def _analyze_precedent_hierarchy(self, packs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the hierarchy and binding nature of precedents"""
        
        sc_cases = []       # Supreme Court (binding on all)
        hc_cases = []       # High Court (binding on subordinates)
        tribunal_cases = [] # Tribunals/Commissions (persuasive)
        
        binding_count = 0
        persuasive_count = 0
        
        for pack in packs:
            court = pack.get("court", "UNKNOWN")
            title = pack.get("title", "")
            neutral_cite = pack.get("neutral_cite", "")
            reporter_cite = pack.get("reporter_cite", "")
            
            case_info = {
                "authority_id": pack.get("authority_id"),
                "title": title,
                "court": court,
                "neutral_cite": neutral_cite,
                "reporter_cite": reporter_cite,
                "date": pack.get("date"),
                "bench": pack.get("bench", ""),
                "pack": pack
            }
            
            if court == "SC":
                sc_cases.append(case_info)
                binding_count += 1
            elif court.startswith("HC-"):
                hc_cases.append(case_info)
                binding_count += 1  # Binding on subordinates
            elif court in ["TRIBUNAL", "COMMISSION"]:
                tribunal_cases.append(case_info)
                persuasive_count += 1
            else:
                persuasive_count += 1
        
        return {
            "sc_cases": sc_cases,
            "hc_cases": hc_cases,
            "tribunal_cases": tribunal_cases,
            "binding_count": binding_count,
            "persuasive_count": persuasive_count,
            "total_precedents": len(packs)
        }

    def _extract_legal_principles(self, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract legal principles and ratio decidendi from cases"""
        
        principles = []
        
        for pack in packs:
            title = pack.get("title", "")
            
            # Look for common legal principle indicators
            principle_indicators = [
                "held", "principle", "ratio", "law laid down", "legal position",
                "rule", "doctrine", "test", "criteria", "standard"
            ]
            
            # Check for landmark case indicators
            landmark_indicators = [
                "overrule", "clarify", "establish", "settle", "pronounce",
                "landmark", "constitution bench", "larger bench"
            ]
            
            is_landmark = any(indicator in title.lower() for indicator in landmark_indicators)
            has_principle = any(indicator in title.lower() for indicator in principle_indicators)
            
            if has_principle or is_landmark:
                principles.append({
                    "authority_id": pack.get("authority_id"),
                    "title": title,
                    "court": pack.get("court", ""),
                    "is_landmark": is_landmark,
                    "principle_type": self._classify_principle_type(title),
                    "neutral_cite": pack.get("neutral_cite", "")
                })
        
        return principles

    def _classify_principle_type(self, title: str) -> str:
        """Classify the type of legal principle"""
        
        title_lower = title.lower()
        
        if any(word in title_lower for word in ["interpret", "construction", "meaning"]):
            return "interpretation"
        elif any(word in title_lower for word in ["procedure", "process", "method"]):
            return "procedural"
        elif any(word in title_lower for word in ["liable", "damages", "compensation"]):
            return "liability"
        elif any(word in title_lower for word in ["jurisdiction", "power", "authority"]):
            return "jurisdiction"
        elif any(word in title_lower for word in ["constitutional", "fundamental", "article"]):
            return "constitutional"
        elif any(word in title_lower for word in ["criminal", "penal", "punishment"]):
            return "criminal"
        elif any(word in title_lower for word in ["contract", "agreement", "obligation"]):
            return "contract"
        else:
            return "general"

    def _detect_precedent_conflicts(self, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect potential conflicts between precedents"""
        
        conflicts = []
        
        # Look for explicit conflict indicators
        conflict_keywords = [
            "overrule", "distinguish", "not follow", "differ", "contrary",
            "inconsistent", "conflict", "divergent", "opposite"
        ]
        
        for pack in packs:
            title = pack.get("title", "")
            
            for keyword in conflict_keywords:
                if keyword in title.lower():
                    conflicts.append({
                        "authority_id": pack.get("authority_id"),
                        "title": title,
                        "court": pack.get("court", ""),
                        "conflict_type": keyword,
                        "neutral_cite": pack.get("neutral_cite", "")
                    })
                    break
        
        # Detect potential conflicts between same-level courts
        # (This is a simplified check - full implementation would need semantic analysis)
        hc_cases = [p for p in packs if p.get("court", "").startswith("HC-")]
        if len(hc_cases) > 1:
            # Check for divergent HC decisions on similar issues
            for i, case1 in enumerate(hc_cases):
                for case2 in hc_cases[i+1:]:
                    if self._cases_might_conflict(case1, case2):
                        conflicts.append({
                            "type": "potential_hc_divergence",
                            "case1": case1.get("title", ""),
                            "case2": case2.get("title", ""),
                            "court1": case1.get("court", ""),
                            "court2": case2.get("court", "")
                        })
        
        return conflicts

    def _cases_might_conflict(self, case1: Dict[str, Any], case2: Dict[str, Any]) -> bool:
        """Simple heuristic to detect potential conflicts between cases"""
        
        title1 = case1.get("title", "").lower()
        title2 = case2.get("title", "").lower()
        
        # Check for similar key terms but different outcomes
        similar_terms = 0
        conflict_terms = 0
        
        key_terms = ["liability", "damages", "jurisdiction", "procedure", "interpretation"]
        for term in key_terms:
            if term in title1 and term in title2:
                similar_terms += 1
        
        conflict_indicators = [
            ("allow", "dismiss"), ("grant", "reject"), ("liable", "not liable"),
            ("valid", "invalid"), ("constitutional", "unconstitutional")
        ]
        
        for term1, term2 in conflict_indicators:
            if (term1 in title1 and term2 in title2) or (term2 in title1 and term1 in title2):
                conflict_terms += 1
        
        return similar_terms >= 2 and conflict_terms >= 1

    async def _analyze_precedents(self, query: str, precedent_analysis: Dict[str, Any],
                                 legal_principles: List[Dict[str, Any]], 
                                 conflicts: List[Dict[str, Any]]) -> str:
        """Perform comprehensive precedent analysis using LLM"""
        
        settings = get_settings()
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build context for LLM
        context_parts = []
        
        # Supreme Court precedents (most authoritative)
        if precedent_analysis["sc_cases"]:
            sc_titles = [case["title"] for case in precedent_analysis["sc_cases"][:3]]
            context_parts.append(f"Supreme Court precedents (binding): {'; '.join(sc_titles)}")
        
        # High Court precedents
        if precedent_analysis["hc_cases"]:
            hc_titles = [case["title"] for case in precedent_analysis["hc_cases"][:3]]
            context_parts.append(f"High Court precedents: {'; '.join(hc_titles)}")
        
        # Legal principles identified
        if legal_principles:
            principle_summary = [f"{p['title']} ({p['principle_type']})" for p in legal_principles[:3]]
            context_parts.append(f"Key legal principles: {'; '.join(principle_summary)}")
        
        # Conflicts or contradictions
        if conflicts:
            conflict_summary = [f"{c.get('title', c.get('type', ''))}" for c in conflicts[:2]]
            context_parts.append(f"Potential conflicts/distinctions: {'; '.join(conflict_summary)}")
        
        context = "\n".join(context_parts) if context_parts else "No clear precedents found."
        
        prompt = f"""As a precedent analysis specialist, analyze the case law relevant to this legal query.

Query: {query}

Precedent Context:
{context}

Provide a comprehensive analysis covering:
1. **Binding Precedents**: Supreme Court and relevant High Court decisions that must be followed
2. **Legal Principles**: Key ratio decidendi and established legal principles
3. **Precedential Hierarchy**: How different court decisions interact and their relative authority
4. **Distinguishing Factors**: How precedents apply or can be distinguished from current facts
5. **Conflicts/Evolution**: Any conflicting precedents and how courts have resolved them

Focus on:
- Binding vs persuasive authority
- Ratio decidendi vs obiter dicta
- Recent developments and judicial trends
- Specific factual contexts and their relevance
- How precedents establish or modify legal tests/standards

Be precise about which court decided what and the binding nature of each precedent. If precedents conflict, explain how courts typically resolve such conflicts."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_GEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=900
            )
            
            content = response.choices[0].message.content
            return content or "Unable to generate precedent analysis."
            
        except Exception as e:
            log.error("precedent_agent.llm_error", error=str(e))
            return f"Precedent analysis based on available context: {context[:500]}..."

    def _extract_precedent_sources(self, packs: List[Dict[str, Any]], 
                                  precedent_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sources prioritized by precedential value"""
        
        sources = []
        
        # Prioritize Supreme Court cases
        for case in precedent_analysis["sc_cases"]:
            pack = case["pack"]
            para_ids = [p.get("para_id", 0) for p in pack.get("paras", [])]
            sources.append({
                "authority_id": case["authority_id"],
                "para_ids": para_ids,
                "relevance": "binding_sc_precedent",
                "title": case["title"],
                "court": case["court"],
                "precedential_weight": "binding"
            })
        
        # Then High Court cases
        for case in precedent_analysis["hc_cases"]:
            if len(sources) >= 5:
                break
            pack = case["pack"]
            para_ids = [p.get("para_id", 0) for p in pack.get("paras", [])]
            sources.append({
                "authority_id": case["authority_id"],
                "para_ids": para_ids,
                "relevance": "binding_hc_precedent",
                "title": case["title"],
                "court": case["court"],
                "precedential_weight": "binding"
            })
        
        # Finally other authorities if needed
        for case in precedent_analysis["tribunal_cases"]:
            if len(sources) >= 5:
                break
            pack = case["pack"]
            para_ids = [p.get("para_id", 0) for p in pack.get("paras", [])]
            sources.append({
                "authority_id": case["authority_id"],
                "para_ids": para_ids,
                "relevance": "persuasive_authority",
                "title": case["title"],
                "court": case["court"],
                "precedential_weight": "persuasive"
            })
        
        return sources

    def _calculate_confidence(self, precedent_analysis: Dict[str, Any],
                            legal_principles: List[Dict[str, Any]],
                            conflicts: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on precedent quality and consistency"""
        
        base_confidence = 0.3
        
        # Strong boost for Supreme Court precedents
        sc_boost = min(0.4, precedent_analysis["binding_count"] * 0.15)
        base_confidence += sc_boost
        
        # Moderate boost for High Court precedents
        hc_boost = min(0.2, len(precedent_analysis["hc_cases"]) * 0.08)
        base_confidence += hc_boost
        
        # Boost for clear legal principles
        if legal_principles:
            landmark_count = sum(1 for p in legal_principles if p["is_landmark"])
            principle_boost = min(0.25, len(legal_principles) * 0.05 + landmark_count * 0.1)
            base_confidence += principle_boost
        
        # Penalty for conflicts (uncertainty)
        if conflicts:
            conflict_penalty = min(0.2, len(conflicts) * 0.08)
            base_confidence -= conflict_penalty
        
        # Boost for multiple consistent precedents
        if precedent_analysis["total_precedents"] >= 3:
            consistency_boost = 0.1
            base_confidence += consistency_boost
        
        return min(0.95, max(0.1, base_confidence))
