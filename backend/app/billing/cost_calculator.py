from __future__ import annotations

import re
from typing import Any, Dict, List
import structlog

log = structlog.get_logger()


class CostCalculator:
    """Calculate costs for various OPAL operations"""
    
    # Base pricing structure (in credits)
    BASE_COSTS = {
        # Query costs by mode
        "query_general": 5,
        "query_precedent": 8,
        "query_limitation": 6,
        "query_draft": 10,
        
        # Additional costs
        "per_agent": 1,
        "per_verification_check": 2,
        "per_1k_tokens": 1,
        "ocr_per_page": 3,
        "export_docx": 8,
        "export_pdf": 10,
        "export_json": 5,
        "notarization": 15,
        
        # Retrieval costs
        "per_source_retrieved": 0.5,
        "premium_search": 3,
        
        # Document processing
        "document_upload": 2,
        "document_analysis": 5,
    }
    
    def calculate_query_cost(self, query: str, mode: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate cost for a query operation"""
        
        filters = filters or {}
        cost_breakdown = {}
        total_cost = 0
        
        # Base cost by mode
        base_cost = self.BASE_COSTS.get(f"query_{mode}", self.BASE_COSTS["query_general"])
        cost_breakdown["base_query"] = base_cost
        total_cost += base_cost
        
        # Token-based cost (approximate)
        estimated_tokens = len(query.split()) * 1.3  # Rough estimate
        if estimated_tokens > 100:
            token_cost = int((estimated_tokens - 100) / 1000) * self.BASE_COSTS["per_1k_tokens"]
            cost_breakdown["tokens"] = token_cost
            total_cost += token_cost
        
        # Agent execution cost (all 7 agents)
        agent_cost = 7 * self.BASE_COSTS["per_agent"]
        cost_breakdown["agents"] = agent_cost
        total_cost += agent_cost
        
        # Verification cost (5 checks)
        verification_cost = 5 * self.BASE_COSTS["per_verification_check"]
        cost_breakdown["verification"] = verification_cost
        total_cost += verification_cost
        
        # Premium features
        if filters.get("premium_search"):
            premium_cost = self.BASE_COSTS["premium_search"]
            cost_breakdown["premium_search"] = premium_cost
            total_cost += premium_cost
        
        if filters.get("notarize"):
            notary_cost = self.BASE_COSTS["notarization"]
            cost_breakdown["notarization"] = notary_cost
            total_cost += notary_cost
        
        # Complexity multiplier based on query
        complexity_multiplier = self._calculate_complexity_multiplier(query)
        if complexity_multiplier > 1.0:
            complexity_cost = int(total_cost * (complexity_multiplier - 1.0))
            cost_breakdown["complexity"] = complexity_cost
            total_cost += complexity_cost
        
        return {
            "total_credits": int(total_cost),
            "breakdown": cost_breakdown,
            "complexity_multiplier": complexity_multiplier,
            "estimated_response_time": self._estimate_response_time(query, mode)
        }
    
    def calculate_document_cost(self, file_size: int, filetype: str, 
                              pages: int = None, ocr_required: bool = False) -> Dict[str, Any]:
        """Calculate cost for document processing"""
        
        cost_breakdown = {}
        total_cost = 0
        
        # Base upload cost
        upload_cost = self.BASE_COSTS["document_upload"]
        cost_breakdown["upload"] = upload_cost
        total_cost += upload_cost
        
        # Size-based cost (per MB)
        size_mb = file_size / (1024 * 1024)
        if size_mb > 5:  # Free tier up to 5MB
            size_cost = int((size_mb - 5) * 2)  # 2 credits per MB over 5MB
            cost_breakdown["size"] = size_cost
            total_cost += size_cost
        
        # OCR cost if required
        if ocr_required and pages:
            ocr_cost = pages * self.BASE_COSTS["ocr_per_page"]
            cost_breakdown["ocr"] = ocr_cost
            total_cost += ocr_cost
        
        # Document analysis cost
        analysis_cost = self.BASE_COSTS["document_analysis"]
        cost_breakdown["analysis"] = analysis_cost
        total_cost += analysis_cost
        
        # File type multiplier
        type_multipliers = {
            "pdf": 1.0,
            "docx": 0.8,
            "doc": 0.8,
            "txt": 0.5
        }
        
        multiplier = type_multipliers.get(filetype.lower(), 1.0)
        if multiplier != 1.0:
            multiplier_cost = int(total_cost * (multiplier - 1.0))
            if multiplier_cost != 0:
                cost_breakdown["filetype_adjustment"] = multiplier_cost
                total_cost += multiplier_cost
        
        return {
            "total_credits": int(max(1, total_cost)),  # Minimum 1 credit
            "breakdown": cost_breakdown,
            "estimated_processing_time": self._estimate_processing_time(pages or 1, ocr_required)
        }
    
    def calculate_export_cost(self, format: str, run_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate cost for exporting results"""
        
        cost_breakdown = {}
        
        # Base export cost by format
        base_cost = self.BASE_COSTS.get(f"export_{format}", 5)
        cost_breakdown[f"export_{format}"] = base_cost
        total_cost = base_cost
        
        # Content complexity cost
        if run_data:
            answer_length = len(run_data.get("answer", ""))
            citations_count = len(run_data.get("citations", []))
            
            # Long answers cost more
            if answer_length > 2000:
                length_cost = int((answer_length - 2000) / 1000)
                cost_breakdown["content_length"] = length_cost
                total_cost += length_cost
            
            # Many citations cost more
            if citations_count > 5:
                citation_cost = (citations_count - 5) * 1
                cost_breakdown["citations"] = citation_cost
                total_cost += citation_cost
        
        return {
            "total_credits": int(total_cost),
            "breakdown": cost_breakdown
        }
    
    def calculate_retrieval_cost(self, sources_count: int, search_complexity: str = "basic") -> Dict[str, Any]:
        """Calculate cost for retrieval operations"""
        
        cost_breakdown = {}
        total_cost = 0
        
        # Per-source cost
        source_cost = int(sources_count * self.BASE_COSTS["per_source_retrieved"])
        cost_breakdown["sources"] = source_cost
        total_cost += source_cost
        
        # Search complexity cost
        complexity_costs = {
            "basic": 0,
            "advanced": 3,
            "semantic": 5,
            "hybrid": 8
        }
        
        complexity_cost = complexity_costs.get(search_complexity, 0)
        if complexity_cost > 0:
            cost_breakdown["search_complexity"] = complexity_cost
            total_cost += complexity_cost
        
        return {
            "total_credits": int(total_cost),
            "breakdown": cost_breakdown
        }
    
    def _calculate_complexity_multiplier(self, query: str) -> float:
        """Calculate complexity multiplier based on query characteristics"""
        
        multiplier = 1.0
        query_lower = query.lower()
        
        # Length complexity
        word_count = len(query.split())
        if word_count > 50:
            multiplier += 0.2
        elif word_count > 100:
            multiplier += 0.5
        
        # Legal complexity indicators
        complex_indicators = [
            "constitutional", "precedent", "interpretation", "conflicting",
            "multiple", "complex", "detailed", "comprehensive", "analysis"
        ]
        
        complexity_score = sum(1 for indicator in complex_indicators if indicator in query_lower)
        multiplier += complexity_score * 0.1
        
        # Multiple legal areas
        legal_areas = [
            "criminal", "civil", "contract", "tort", "property", "constitutional",
            "administrative", "tax", "labour", "family", "commercial"
        ]
        
        areas_mentioned = sum(1 for area in legal_areas if area in query_lower)
        if areas_mentioned > 2:
            multiplier += 0.3
        
        # Citation complexity
        citation_count = len(re.findall(r'[Ss]ection\s+\d+|[Aa]rticle\s+\d+', query))
        if citation_count > 3:
            multiplier += 0.2
        
        return min(2.0, multiplier)  # Cap at 2x
    
    def _estimate_response_time(self, query: str, mode: str) -> str:
        """Estimate response time for query"""
        
        base_times = {
            "general": 15,
            "precedent": 25,
            "limitation": 20,
            "draft": 35
        }
        
        base_time = base_times.get(mode, 15)
        
        # Adjust for query complexity
        complexity = self._calculate_complexity_multiplier(query)
        estimated_time = int(base_time * complexity)
        
        if estimated_time < 30:
            return "15-30 seconds"
        elif estimated_time < 60:
            return "30-60 seconds"
        elif estimated_time < 120:
            return "1-2 minutes"
        else:
            return "2+ minutes"
    
    def _estimate_processing_time(self, pages: int, ocr_required: bool) -> str:
        """Estimate document processing time"""
        
        base_time = pages * 2  # 2 seconds per page
        
        if ocr_required:
            base_time += pages * 10  # Additional 10 seconds per page for OCR
        
        if base_time < 30:
            return "Under 30 seconds"
        elif base_time < 120:
            return "1-2 minutes"
        elif base_time < 300:
            return "2-5 minutes"
        else:
            return "5+ minutes"
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """Get current pricing information"""
        
        return {
            "base_costs": self.BASE_COSTS,
            "free_tier": {
                "daily_queries": 3,
                "monthly_credits": 100,
                "document_size_mb": 5,
                "exports_per_month": 10
            },
            "subscription_tiers": {
                "starter": {
                    "monthly_cost_usd": 29,
                    "included_credits": 500,
                    "daily_queries": 20,
                    "document_size_mb": 50,
                    "priority_support": False
                },
                "professional": {
                    "monthly_cost_usd": 99,
                    "included_credits": 2000,
                    "daily_queries": 100,
                    "document_size_mb": 200,
                    "priority_support": True,
                    "api_access": True
                },
                "enterprise": {
                    "monthly_cost_usd": 299,
                    "included_credits": 8000,
                    "daily_queries": "unlimited",
                    "document_size_mb": 1000,
                    "priority_support": True,
                    "api_access": True,
                    "white_label": True
                }
            },
            "credit_packages": {
                "small": {"credits": 100, "cost_usd": 9.99},
                "medium": {"credits": 500, "cost_usd": 39.99},
                "large": {"credits": 1000, "cost_usd": 69.99},
                "bulk": {"credits": 5000, "cost_usd": 299.99}
            }
        }
