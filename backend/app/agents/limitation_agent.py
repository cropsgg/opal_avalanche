from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import structlog

from openai import OpenAI
from app.core.config import get_settings
from app.agents.base import AgentOutput

log = structlog.get_logger()


class LimitationAgent:
    name = "limitation"

    async def run(self, query: str, packs: List[Dict[str, Any]], matter_docs: List[Dict[str, Any]]) -> AgentOutput:
        """
        Analyze limitation periods and time-barred claims
        Focus on Limitation Act provisions, computation of time, and exceptions
        """
        
        log.info("limitation_agent.start", query_length=len(query))
        
        # Extract limitation-related context
        limitation_context = self._extract_limitation_context(query, packs)
        
        # Analyze applicable limitation periods
        limitation_periods = self._identify_limitation_periods(limitation_context)
        
        # Calculate time computations if dates are available
        time_calculations = self._calculate_limitation_periods(limitation_context, matter_docs)
        
        # Check for exceptions and extensions
        exceptions = self._identify_exceptions(limitation_context, packs)
        
        # Build comprehensive limitation analysis
        reasoning = await self._analyze_limitation(query, limitation_context, limitation_periods, 
                                                 time_calculations, exceptions)
        
        sources = self._extract_sources(packs, limitation_context)
        confidence = self._calculate_confidence(limitation_context, limitation_periods, time_calculations)
        
        log.info("limitation_agent.complete",
                confidence=confidence,
                periods_identified=len(limitation_periods),
                exceptions_found=len(exceptions),
                time_sensitive=bool(time_calculations))
        
        return AgentOutput(
            reasoning=reasoning,
            sources=sources,
            confidence=confidence
        )

    def _extract_limitation_context(self, query: str, packs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract limitation-related information from query and packs"""
        
        # Time-related keywords in query
        time_keywords = [
            "limitation", "time-barred", "prescribed", "barred by time",
            "limitation act", "article", "schedule", "period", "years",
            "months", "days", "from the date", "accrual", "cause of action",
            "knowledge", "discovery", "fraud", "mistake", "disability"
        ]
        
        query_has_limitation = any(keyword in query.lower() for keyword in time_keywords)
        
        # Extract dates from query
        query_dates = self._extract_dates_from_text(query)
        
        # Extract cause of action type
        cause_of_action = self._identify_cause_of_action(query)
        
        # Find limitation-related authorities
        limitation_authorities = []
        for pack in packs:
            title = pack.get("title", "").lower()
            if any(keyword in title for keyword in ["limitation", "prescribed", "time-barred", "article"]):
                limitation_authorities.append(pack)
        
        # Extract specific article numbers mentioned
        article_numbers = re.findall(r'[Aa]rticle\s+(\d+)', query)
        article_numbers.extend(self._find_articles_in_packs(packs))
        
        return {
            "query_has_limitation": query_has_limitation,
            "query_dates": query_dates,
            "cause_of_action": cause_of_action,
            "limitation_authorities": limitation_authorities,
            "article_numbers": list(set(article_numbers)),
            "time_sensitive": bool(query_dates) or query_has_limitation
        }

    def _extract_dates_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates and their context from text"""
        
        dates = []
        
        # Date patterns
        date_patterns = [
            (r'(\d{1,2})[\./-](\d{1,2})[\./-](\d{4})', 'dd/mm/yyyy'),
            (r'(\d{4})[\./-](\d{1,2})[\./-](\d{1,2})', 'yyyy/mm/dd'),
            (r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})', 'dd Month yyyy'),
            (r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})', 'Month dd yyyy')
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
                    elif format_type == 'Month dd yyyy':
                        month = month_map.get(match.group(1).lower(), 1)
                        day = int(match.group(2))
                        year = int(match.group(3))
                    
                    if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2030:
                        date_obj = datetime(year, month, day)
                        
                        # Extract context around the date
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end].strip()
                        
                        dates.append({
                            "date": date_obj,
                            "text": match.group(0),
                            "context": context,
                            "format": format_type
                        })
                        
                except (ValueError, IndexError):
                    continue
        
        return dates

    def _identify_cause_of_action(self, query: str) -> str:
        """Identify the type of legal cause of action"""
        
        query_lower = query.lower()
        
        cause_types = {
            "contract": ["contract", "breach", "agreement", "obligation", "payment", "performance"],
            "tort": ["tort", "negligence", "defamation", "damages", "injury", "accident"],
            "property": ["property", "possession", "title", "ownership", "recovery", "eviction"],
            "suit_for_money": ["money", "debt", "loan", "recovery", "payment", "amount"],
            "specific_performance": ["specific performance", "execution", "decree"],
            "declaration": ["declaration", "declaratory", "title", "right"],
            "injunction": ["injunction", "restraint", "prohibit", "prevent"],
            "partition": ["partition", "division", "share"],
            "probate": ["will", "probate", "succession", "estate"],
            "criminal": ["complaint", "cognizance", "fir", "charge", "prosecution"]
        }
        
        for cause_type, keywords in cause_types.items():
            if any(keyword in query_lower for keyword in keywords):
                return cause_type
        
        return "general"

    def _find_articles_in_packs(self, packs: List[Dict[str, Any]]) -> List[str]:
        """Find Limitation Act article numbers in authority packs"""
        
        articles = []
        
        for pack in packs:
            title = pack.get("title", "")
            
            # Look for article numbers in titles
            article_matches = re.findall(r'[Aa]rticle\s+(\d+)', title)
            articles.extend(article_matches)
            
            # Check paras for article references
            for para in pack.get("paras", []):
                para_text = para.get("text", "")
                para_articles = re.findall(r'[Aa]rticle\s+(\d+)', para_text)
                articles.extend(para_articles)
        
        return articles

    def _identify_limitation_periods(self, limitation_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify applicable limitation periods based on cause of action"""
        
        # Common limitation periods under Indian Limitation Act
        limitation_schedule = {
            "contract": {"period": 3, "unit": "years", "article": "113", "description": "To recover money payable under a contract"},
            "suit_for_money": {"period": 3, "unit": "years", "article": "113", "description": "To recover money payable"},
            "tort": {"period": 3, "unit": "years", "article": "114", "description": "For compensation for tortious act"},
            "property": {"period": 12, "unit": "years", "article": "111", "description": "To recover possession of property"},
            "specific_performance": {"period": 3, "unit": "years", "article": "113", "description": "For specific performance"},
            "declaration": {"period": 3, "unit": "years", "article": "113", "description": "For declaration"},
            "injunction": {"period": 3, "unit": "years", "article": "113", "description": "For injunction"},
            "partition": {"period": 30, "unit": "years", "article": "144", "description": "For partition"},
            "probate": {"period": 12, "unit": "years", "article": "136", "description": "To establish will"},
            "criminal": {"period": 6, "unit": "months", "article": "468", "description": "CrPC limitation for complaints"}
        }
        
        periods = []
        cause_of_action = limitation_context["cause_of_action"]
        
        # Add specific period for identified cause of action
        if cause_of_action in limitation_schedule:
            periods.append(limitation_schedule[cause_of_action])
        
        # Add periods for any specifically mentioned articles
        article_periods = {
            "113": {"period": 3, "unit": "years", "description": "Residual article for contracts"},
            "114": {"period": 3, "unit": "years", "description": "For compensation for wrongs"},
            "111": {"period": 12, "unit": "years", "description": "To recover possession"},
            "58": {"period": 3, "unit": "years", "description": "For money deposited"},
            "59": {"period": 3, "unit": "years", "description": "For money payable for necessaries"},
            "137": {"period": 1, "unit": "year", "description": "To set aside transfer by guardian"}
        }
        
        for article_num in limitation_context["article_numbers"]:
            if article_num in article_periods:
                period_info = article_periods[article_num].copy()
                period_info["article"] = article_num
                periods.append(period_info)
        
        # Default general period if nothing specific found
        if not periods and limitation_context["query_has_limitation"]:
            periods.append({
                "period": 3, "unit": "years", "article": "113", 
                "description": "General limitation period"
            })
        
        return periods

    def _calculate_limitation_periods(self, limitation_context: Dict[str, Any], 
                                    matter_docs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Calculate limitation periods if dates are available"""
        
        if not limitation_context["query_dates"]:
            return None
        
        calculations = {}
        
        # Use the first date found as cause of action accrual date
        accrual_date = limitation_context["query_dates"][0]["date"]
        
        # Calculate limitation periods for each identified period
        for period_info in self._identify_limitation_periods(limitation_context):
            period_value = period_info["period"]
            unit = period_info["unit"]
            article = period_info["article"]
            
            if unit == "years":
                expiry_date = accrual_date + timedelta(days=365 * period_value)
            elif unit == "months":
                expiry_date = accrual_date + timedelta(days=30 * period_value)
            elif unit == "days":
                expiry_date = accrual_date + timedelta(days=period_value)
            else:
                continue
            
            days_remaining = (expiry_date - datetime.now()).days
            is_expired = days_remaining < 0
            
            calculations[article] = {
                "accrual_date": accrual_date,
                "expiry_date": expiry_date,
                "days_remaining": days_remaining,
                "is_expired": is_expired,
                "period": f"{period_value} {unit}",
                "article": article,
                "description": period_info["description"]
            }
        
        return calculations

    def _identify_exceptions(self, limitation_context: Dict[str, Any], 
                           packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify exceptions to limitation periods"""
        
        exceptions = []
        
        # Common exceptions under Limitation Act
        exception_keywords = {
            "fraud": {"section": "17", "description": "Time runs from discovery of fraud"},
            "mistake": {"section": "17", "description": "Time runs from discovery of mistake"},
            "disability": {"section": "6", "description": "Extension for minors/unsound mind"},
            "acknowledgment": {"section": "18", "description": "Fresh period from acknowledgment"},
            "part_payment": {"section": "19", "description": "Fresh period from part payment"},
            "legal_disability": {"section": "6", "description": "Disability of plaintiff"},
            "continuing_wrong": {"section": "22", "description": "Fresh period for continuing wrongs"},
            "concealment": {"section": "17", "description": "Fraudulent concealment"}
        }
        
        query_lower = limitation_context.get("query", "").lower() if "query" in limitation_context else ""
        
        # Check for exception keywords in query
        for exception, details in exception_keywords.items():
            if exception in query_lower:
                exceptions.append({
                    "type": exception,
                    "section": details["section"],
                    "description": details["description"],
                    "source": "query"
                })
        
        # Check for exceptions in authority titles
        for pack in packs:
            title = pack.get("title", "").lower()
            for exception, details in exception_keywords.items():
                if exception in title:
                    exceptions.append({
                        "type": exception,
                        "section": details["section"],
                        "description": details["description"],
                        "source": "authority",
                        "authority_id": pack.get("authority_id"),
                        "title": pack.get("title")
                    })
        
        return exceptions

    async def _analyze_limitation(self, query: str, limitation_context: Dict[str, Any],
                                limitation_periods: List[Dict[str, Any]],
                                time_calculations: Optional[Dict[str, Any]],
                                exceptions: List[Dict[str, Any]]) -> str:
        """Perform comprehensive limitation analysis using LLM"""
        
        settings = get_settings()
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build context for LLM
        context_parts = []
        
        if limitation_periods:
            periods_summary = [f"Article {p['article']}: {p['period']} {p['unit']} - {p['description']}" 
                             for p in limitation_periods]
            context_parts.append(f"Applicable limitation periods: {'; '.join(periods_summary)}")
        
        if time_calculations:
            calc_summary = []
            for article, calc in time_calculations.items():
                status = "EXPIRED" if calc["is_expired"] else f"{calc['days_remaining']} days remaining"
                calc_summary.append(f"Article {article}: {status}")
            context_parts.append(f"Time calculations: {'; '.join(calc_summary)}")
        
        if exceptions:
            exception_summary = [f"{e['type']} (Section {e['section']})" for e in exceptions]
            context_parts.append(f"Possible exceptions: {'; '.join(exception_summary)}")
        
        if limitation_context["article_numbers"]:
            context_parts.append(f"Articles mentioned: {', '.join(limitation_context['article_numbers'])}")
        
        context = "\n".join(context_parts) if context_parts else "No specific limitation information found."
        
        prompt = f"""As a limitation law specialist, analyze the time limitations relevant to this legal query.

Query: {query}

Limitation Context:
{context}

Provide a comprehensive analysis covering:
1. **Applicable Articles**: Which articles of the Limitation Act apply and why
2. **Limitation Period**: Exact time period and when it starts running
3. **Accrual of Cause of Action**: When the limitation period begins
4. **Current Status**: Whether the claim is within time or time-barred
5. **Exceptions/Extensions**: Any exceptions that may apply (fraud, mistake, disability, acknowledgment)
6. **Computation Rules**: How time is calculated (excluding certain days, etc.)

Focus on:
- Specific article numbers and their requirements
- Point in time when cause of action accrues
- Effect of acknowledgments and part payments
- Disability provisions and their impact
- Continuing wrongs and successive limitations
- Section 5 applications for condonation of delay

Be precise about dates and time calculations. If the matter appears time-barred, explain potential exceptions. If information is insufficient for precise calculation, state what additional information is needed."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_GEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for precise legal calculations
                max_tokens=900
            )
            
            content = response.choices[0].message.content
            return content or "Unable to generate limitation analysis."
            
        except Exception as e:
            log.error("limitation_agent.llm_error", error=str(e))
            return f"Limitation analysis based on available context: {context[:500]}..."

    def _extract_sources(self, packs: List[Dict[str, Any]], 
                        limitation_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sources relevant to limitation analysis"""
        
        sources = []
        
        # Prioritize limitation-specific authorities
        for pack in limitation_context["limitation_authorities"]:
            authority_id = pack.get("authority_id")
            if authority_id:
                para_ids = [p.get("para_id", 0) for p in pack.get("paras", [])]
                sources.append({
                    "authority_id": authority_id,
                    "para_ids": para_ids,
                    "relevance": "limitation_specific",
                    "title": pack.get("title", ""),
                    "court": pack.get("court", "")
                })
        
        # Add other relevant sources
        for pack in packs:
            if pack not in limitation_context["limitation_authorities"] and len(sources) < 5:
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
        
        return sources

    def _calculate_confidence(self, limitation_context: Dict[str, Any],
                            limitation_periods: List[Dict[str, Any]],
                            time_calculations: Optional[Dict[str, Any]]) -> float:
        """Calculate confidence based on limitation analysis completeness"""
        
        base_confidence = 0.2
        
        # Boost for limitation-specific query
        if limitation_context["query_has_limitation"]:
            base_confidence += 0.3
        
        # Boost for identified limitation periods
        if limitation_periods:
            base_confidence += min(0.3, len(limitation_periods) * 0.15)
        
        # Strong boost for time calculations
        if time_calculations:
            base_confidence += 0.3
            # Extra boost if calculations show clear status
            for calc in time_calculations.values():
                if abs(calc["days_remaining"]) > 30:  # Clear expired or safe
                    base_confidence += 0.1
                    break
        
        # Boost for specific article numbers
        if limitation_context["article_numbers"]:
            base_confidence += min(0.2, len(limitation_context["article_numbers"]) * 0.1)
        
        # Boost for limitation authorities found
        if limitation_context["limitation_authorities"]:
            base_confidence += min(0.15, len(limitation_context["limitation_authorities"]) * 0.05)
        
        return min(0.95, base_confidence)
