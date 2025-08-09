from __future__ import annotations

import re
from typing import Any, Dict, List
import structlog

from openai import OpenAI
from app.core.config import get_settings
from app.agents.base import AgentOutput

log = structlog.get_logger()


class StatuteAgent:
    name = "statute"

    async def run(self, query: str, packs: List[Dict[str, Any]], matter_docs: List[Dict[str, Any]]) -> AgentOutput:
        """
        Analyze statutory provisions and sections relevant to the query
        Focus on specific sections, articles, and their interpretation
        """
        
        log.info("statute_agent.start", query_length=len(query))
        
        # Extract statute-related context from packs
        statute_context = self._extract_statute_context(packs)
        
        # Get relevant statutes from query
        query_statutes = self._extract_statutes_from_query(query)
        
        # Build comprehensive statutory analysis
        reasoning = await self._analyze_statutes(query, statute_context, query_statutes, matter_docs)
        
        # Extract sources and calculate confidence
        sources = self._extract_sources(packs, statute_context)
        confidence = self._calculate_confidence(statute_context, query_statutes, reasoning)
        
        log.info("statute_agent.complete", 
                confidence=confidence,
                sources_count=len(sources),
                statutes_found=len(query_statutes))
        
        return AgentOutput(
            reasoning=reasoning,
            sources=sources,
            confidence=confidence
        )

    def _extract_statute_context(self, packs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract statute-related information from retrieval packs"""
        
        statutes_found = set()
        sections_found = set()
        articles_found = set()
        relevant_packs = []
        
        for pack in packs:
            # Check for statute tags in metadata
            metadata = pack.get("metadata", {})
            statute_tags = metadata.get("statute_tags", [])
            
            if statute_tags:
                statutes_found.update(statute_tags)
                relevant_packs.append(pack)
            
            # Extract sections and articles from title and content
            title = pack.get("title", "")
            self._extract_sections_articles(title, sections_found, articles_found)
            
            # Check paragraphs for statute references
            for para in pack.get("paras", []):
                para_text = para.get("text", "")
                self._extract_sections_articles(para_text, sections_found, articles_found)
        
        return {
            "statutes": list(statutes_found),
            "sections": list(sections_found),
            "articles": list(articles_found),
            "relevant_packs": relevant_packs,
            "total_statute_references": len(statutes_found) + len(sections_found) + len(articles_found)
        }

    def _extract_sections_articles(self, text: str, sections: set, articles: set) -> None:
        """Extract section and article references from text"""
        
        # Section patterns
        section_patterns = [
            r'Section\s+(\d+[A-Z]?)\s+of\s+([^,\n\.]+)',
            r'[Ss]ection\s+(\d+[A-Z]?)',
            r'Sec\.\s*(\d+[A-Z]?)',
            r'S\.\s*(\d+[A-Z]?)'
        ]
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                sections.add(f"Section {match.group(1)}")
        
        # Article patterns
        article_patterns = [
            r'Article\s+(\d+[A-Z]?)\s+of\s+([^,\n\.]+)',
            r'[Aa]rticle\s+(\d+[A-Z]?)',
            r'Art\.\s*(\d+[A-Z]?)'
        ]
        
        for pattern in article_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                articles.add(f"Article {match.group(1)}")

    def _extract_statutes_from_query(self, query: str) -> List[str]:
        """Extract statute references from the user query"""
        
        statutes = []
        
        # Common Indian statutes
        statute_patterns = {
            r'\bIPC\b|\bIndian Penal Code\b': 'Indian Penal Code',
            r'\bCrPC\b|\bCode of Criminal Procedure\b': 'Code of Criminal Procedure',
            r'\bCPC\b|\bCode of Civil Procedure\b': 'Code of Civil Procedure',
            r'\bEvidence Act\b|\bIndian Evidence Act\b': 'Indian Evidence Act',
            r'\bContract Act\b|\bIndian Contract Act\b': 'Indian Contract Act',
            r'\bConstitution\b|\bIndian Constitution\b': 'Constitution of India',
            r'\bNI Act\b|\bNegotiable Instruments Act\b': 'Negotiable Instruments Act',
            r'\bTransfer of Property Act\b': 'Transfer of Property Act',
            r'\bSale of Goods Act\b': 'Sale of Goods Act',
            r'\bPartnership Act\b': 'Indian Partnership Act',
            r'\bCompanies Act\b': 'Companies Act',
            r'\bArbitration Act\b|\bArbitration and Conciliation Act\b': 'Arbitration and Conciliation Act'
        }
        
        for pattern, statute_name in statute_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                statutes.append(statute_name)
        
        # Extract specific section/article numbers from query
        section_matches = re.findall(r'[Ss]ection\s+(\d+[A-Z]?)', query)
        article_matches = re.findall(r'[Aa]rticle\s+(\d+[A-Z]?)', query)
        
        for section in section_matches:
            statutes.append(f"Section {section}")
        
        for article in article_matches:
            statutes.append(f"Article {article}")
        
        return statutes

    async def _analyze_statutes(self, query: str, statute_context: Dict[str, Any], 
                               query_statutes: List[str], matter_docs: List[Dict[str, Any]]) -> str:
        """Perform comprehensive statutory analysis using LLM"""
        
        settings = get_settings()
        
        # Return mock analysis if no API key configured
        if not settings.OPENAI_API_KEY:
            log.warning("statute_agent.no_api_key", message="Using mock analysis for development")
            return self._generate_mock_analysis(query, statute_context, query_statutes)
        
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            log.error("statute_agent.openai_error", error=str(e))
            return self._generate_mock_analysis(query, statute_context, query_statutes)
        
        # Build context for LLM
        context_parts = []
        
        if statute_context["statutes"]:
            context_parts.append(f"Relevant statutes found: {', '.join(statute_context['statutes'])}")
        
        if statute_context["sections"]:
            context_parts.append(f"Sections referenced: {', '.join(statute_context['sections'])}")
        
        if statute_context["articles"]:
            context_parts.append(f"Articles referenced: {', '.join(statute_context['articles'])}")
        
        if query_statutes:
            context_parts.append(f"Statutes mentioned in query: {', '.join(query_statutes)}")
        
        # Include relevant pack titles for context
        relevant_titles = [pack.get("title", "") for pack in statute_context["relevant_packs"]]
        if relevant_titles:
            context_parts.append(f"Relevant authority titles: {'; '.join(relevant_titles[:3])}")
        
        context = "\n".join(context_parts) if context_parts else "No specific statutory references found."
        
        prompt = f"""As a statute analysis specialist, analyze the statutory provisions relevant to this legal query.

Query: {query}

Statutory Context:
{context}

Provide a focused analysis covering:
1. **Applicable Statutes**: Which specific laws/acts apply and why
2. **Relevant Sections/Articles**: Key provisions and their scope
3. **Interpretation**: How these provisions should be understood
4. **Requirements**: What conditions/elements must be satisfied
5. **Exceptions/Limitations**: Any exceptions or limiting factors

Focus on:
- Exact statutory language and its meaning
- Required elements and their proof
- Procedural vs substantive provisions
- Mandatory vs directory requirements
- Penalty/consequence provisions

Be precise about section numbers and statutory language. If no clear statutory provisions apply, explain what general legal principles might govern."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_GEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            return content or "Unable to generate statutory analysis."
            
        except Exception as e:
            log.error("statute_agent.llm_error", error=str(e))
            return f"Statutory analysis based on available context: {context[:500]}..."

    def _extract_sources(self, packs: List[Dict[str, Any]], 
                        statute_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract source authorities with statutory relevance"""
        
        sources = []
        
        # Prioritize packs with statute references
        for pack in statute_context["relevant_packs"]:
            authority_id = pack.get("authority_id")
            if authority_id:
                para_ids = [p.get("para_id", 0) for p in pack.get("paras", [])]
                sources.append({
                    "authority_id": authority_id,
                    "para_ids": para_ids,
                    "relevance": "statutory_reference",
                    "title": pack.get("title", ""),
                    "court": pack.get("court", "")
                })
        
        # Add other high-scoring packs if we need more sources
        if len(sources) < 3:
            for pack in packs:
                if pack not in statute_context["relevant_packs"]:
                    authority_id = pack.get("authority_id")
                    if authority_id:
                        para_ids = [p.get("para_id", 0) for p in pack.get("paras", [])]
                        sources.append({
                            "authority_id": authority_id,
                            "para_ids": para_ids,
                            "relevance": "general",
                            "title": pack.get("title", ""),
                            "court": pack.get("court", "")
                        })
                
                if len(sources) >= 5:  # Limit total sources
                    break
        
        return sources

    def _calculate_confidence(self, statute_context: Dict[str, Any], 
                            query_statutes: List[str], reasoning: str) -> float:
        """Calculate confidence based on statutory coverage and specificity"""
        
        base_confidence = 0.3
        
        # Boost for specific statute references found
        if statute_context["total_statute_references"] > 0:
            base_confidence += min(0.3, statute_context["total_statute_references"] * 0.1)
        
        # Boost for query statutes that were addressed
        if query_statutes:
            addressed_statutes = sum(1 for statute in query_statutes 
                                   if statute.lower() in reasoning.lower())
            coverage_ratio = addressed_statutes / len(query_statutes)
            base_confidence += coverage_ratio * 0.25
        
        # Boost for specific section/article numbers mentioned
        section_mentions = len(re.findall(r'[Ss]ection\s+\d+', reasoning))
        article_mentions = len(re.findall(r'[Aa]rticle\s+\d+', reasoning))
        base_confidence += min(0.15, (section_mentions + article_mentions) * 0.03)
        
        # Boost for relevant authorities
        if statute_context["relevant_packs"]:
            base_confidence += min(0.2, len(statute_context["relevant_packs"]) * 0.05)
        
        return min(0.95, base_confidence)
    
    def _generate_mock_analysis(self, query: str, statute_context: Dict[str, Any], 
                               query_statutes: List[str]) -> str:
        """Generate mock statutory analysis for development mode"""
        
        analysis_parts = [
            "**STATUTORY ANALYSIS** (Development Mode - Mock Response)",
            "",
            f"**Query**: {query[:100]}..." if len(query) > 100 else f"**Query**: {query}",
            ""
        ]
        
        if query_statutes:
            analysis_parts.extend([
                "**Applicable Statutes:**",
                f"The query references: {', '.join(query_statutes)}",
                ""
            ])
        
        if statute_context["statutes"]:
            analysis_parts.extend([
                "**Relevant Legal Provisions:**",
                f"Found references to: {', '.join(list(statute_context['statutes'])[:3])}",
                ""
            ])
        
        if statute_context["sections"]:
            analysis_parts.extend([
                "**Specific Sections:**",
                f"Key sections: {', '.join(list(statute_context['sections'])[:5])}",
                ""
            ])
        
        analysis_parts.extend([
            "**Legal Analysis:**",
            "This is a mock response for development purposes. In production, this would contain:",
            "- Detailed interpretation of relevant statutory provisions",
            "- Application of law to the specific factual scenario",
            "- Identification of key legal principles and precedents",
            "- Analysis of compliance requirements and procedural aspects",
            "",
            "**Note**: Configure OpenAI API key for actual legal analysis."
        ])
        
        return "\n".join(analysis_parts)
