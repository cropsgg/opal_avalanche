from __future__ import annotations

import re
from typing import Any, Dict, List
import structlog

from openai import OpenAI
from app.core.config import get_settings
from app.agents.base import AgentOutput

log = structlog.get_logger()


class DraftingAgent:
    name = "drafting"

    async def run(self, query: str, packs: List[Dict[str, Any]], matter_docs: List[Dict[str, Any]]) -> AgentOutput:
        """
        Provide drafting suggestions for legal documents and pleadings
        Focus on structure, legal requirements, and precedent-based language
        """
        
        log.info("drafting_agent.start", query_length=len(query))
        
        # Identify document type and drafting requirements
        document_type = self._identify_document_type(query)
        
        # Extract relevant precedent language and clauses
        precedent_clauses = self._extract_precedent_clauses(packs, document_type)
        
        # Identify legal requirements and essential elements
        legal_requirements = self._identify_legal_requirements(query, packs, document_type)
        
        # Build comprehensive drafting guidance
        reasoning = await self._build_drafting_guidance(query, document_type, precedent_clauses, legal_requirements)
        
        sources = self._extract_drafting_sources(packs, precedent_clauses)
        confidence = self._calculate_confidence(document_type, precedent_clauses, legal_requirements)
        
        log.info("drafting_agent.complete",
                confidence=confidence,
                document_type=document_type,
                precedent_clauses=len(precedent_clauses))
        
        return AgentOutput(
            reasoning=reasoning,
            sources=sources,
            confidence=confidence
        )

    def _identify_document_type(self, query: str) -> str:
        """Identify the type of document to be drafted"""
        
        query_lower = query.lower()
        
        document_types = {
            "plaint": ["plaint", "suit", "filing suit", "civil suit"],
            "written_statement": ["written statement", "defense", "reply"],
            "application": ["application", "petition", "misc application"],
            "appeal": ["appeal", "appellate", "first appeal"],
            "writ_petition": ["writ", "mandamus", "certiorari"],
            "bail_application": ["bail", "anticipatory bail"],
            "complaint": ["complaint", "criminal complaint"],
            "contract": ["contract", "agreement", "mou"],
            "notice": ["notice", "legal notice", "demand notice"],
            "affidavit": ["affidavit", "sworn statement"]
        }
        
        for doc_type, keywords in document_types.items():
            if any(keyword in query_lower for keyword in keywords):
                return doc_type
        
        return "general_document"

    def _extract_precedent_clauses(self, packs: List[Dict[str, Any]], document_type: str) -> List[Dict[str, Any]]:
        """Extract relevant clauses and language from precedent documents"""
        
        clauses = []
        
        # Look for standard legal phrases
        standard_phrases = [
            "without prejudice to",
            "subject to",
            "it is submitted",
            "respectfully prayed",
            "cause of action arose",
            "interest of justice"
        ]
        
        for pack in packs:
            for para in pack.get("paras", []):
                para_text = para.get("text", "")
                for phrase in standard_phrases:
                    if phrase in para_text.lower():
                        clauses.append({
                            "text": para_text[:200],
                            "phrase": phrase,
                            "authority_id": pack.get("authority_id")
                        })
                        break
        
        return clauses[:8]

    def _identify_legal_requirements(self, query: str, packs: List[Dict[str, Any]], document_type: str) -> List[Dict[str, Any]]:
        """Identify legal requirements for the document type"""
        
        requirements = []
        
        # Document-specific requirements
        doc_requirements = {
            "plaint": [
                "Cause of action disclosure",
                "Valuation and court fees",
                "Limitation period compliance", 
                "Specific relief sought"
            ],
            "application": [
                "Urgency demonstration",
                "Prima facie case",
                "Balance of convenience",
                "Irreparable injury"
            ],
            "contract": [
                "Offer and acceptance",
                "Consideration clause",
                "Terms and conditions",
                "Breach consequences"
            ]
        }
        
        basic_requirements = doc_requirements.get(document_type, [])
        
        for req in basic_requirements:
            requirements.append({
                "requirement": req,
                "type": "essential"
            })
        
        return requirements

    async def _build_drafting_guidance(self, query: str, document_type: str, 
                                     precedent_clauses: List[Dict[str, Any]],
                                     legal_requirements: List[Dict[str, Any]]) -> str:
        """Build comprehensive drafting guidance"""
        
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            return self._build_basic_guidance(document_type, legal_requirements)
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build context for LLM
        context_parts = []
        
        if document_type != "general_document":
            context_parts.append(f"Document type: {document_type.replace('_', ' ').title()}")
        
        if legal_requirements:
            req_list = [req["requirement"] for req in legal_requirements]
            context_parts.append(f"Legal requirements: {'; '.join(req_list)}")
        
        if precedent_clauses:
            clause_examples = [f"'{clause['text'][:80]}...'" for clause in precedent_clauses[:3]]
            context_parts.append(f"Precedent language: {'; '.join(clause_examples)}")
        
        context = "\n".join(context_parts) if context_parts else "General document drafting request."
        
        prompt = f"""As a legal drafting specialist, provide guidance for drafting this document.

Request: {query}

Context:
{context}

Provide drafting guidance covering:
1. Document Structure and essential sections
2. Mandatory legal requirements and elements  
3. Appropriate legal language and terminology
4. Procedural compliance requirements
5. Common mistakes to avoid

Focus on practical, actionable guidance."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_GEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content or "Unable to generate drafting guidance."
            
        except Exception as e:
            log.error("drafting_agent.llm_error", error=str(e))
            return self._build_basic_guidance(document_type, legal_requirements)

    def _build_basic_guidance(self, document_type: str, legal_requirements: List[Dict[str, Any]]) -> str:
        """Build basic drafting guidance without LLM"""
        
        guidance_parts = [
            f"DRAFTING GUIDANCE - {document_type.replace('_', ' ').title()}",
            ""
        ]
        
        if legal_requirements:
            guidance_parts.extend([
                "ESSENTIAL REQUIREMENTS:",
                *[f"• {req['requirement']}" for req in legal_requirements],
                ""
            ])
        
        guidance_parts.extend([
            "GENERAL STRUCTURE:",
            "1. Title and case details",
            "2. Factual background",
            "3. Legal grounds",
            "4. Relief sought",
            "5. Verification"
        ])
        
        return "\n".join(guidance_parts)

    def _extract_drafting_sources(self, packs: List[Dict[str, Any]], 
                                 precedent_clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract sources relevant for drafting"""
        
        sources = []
        
        # Add authorities that contain precedent clauses
        for clause in precedent_clauses:
            if clause.get("authority_id"):
                sources.append({
                    "authority_id": clause["authority_id"],
                    "para_ids": [0],
                    "relevance": "precedent_language"
                })
        
        return sources[:5]

    def _calculate_confidence(self, document_type: str, precedent_clauses: List[Dict[str, Any]],
                            legal_requirements: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on available drafting guidance"""
        
        base_confidence = 0.4
        
        # Boost for identified document type
        if document_type != "general_document":
            base_confidence += 0.2
        
        # Boost for precedent clauses found
        if precedent_clauses:
            base_confidence += min(0.2, len(precedent_clauses) * 0.04)
        
        # Boost for legal requirements identified
        if legal_requirements:
            base_confidence += min(0.15, len(legal_requirements) * 0.03)
        
        return min(0.8, base_confidence)