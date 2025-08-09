from __future__ import annotations

import re
from typing import Dict, Optional
import structlog
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

log = structlog.get_logger()

# Default weights for each agent by subdomain
_SUBDOMAIN_WEIGHTS: Dict[str, Dict[str, float]] = {
    "constitutional": {
        "statute": 1.8,      # High - Constitutional provisions critical
        "precedent": 1.6,    # High - SC precedents very important
        "limitation": 0.8,   # Low - Less time-sensitive
        "risk": 1.2,         # Medium - Constitutional matters high-stake
        "devil": 1.4,        # Medium-High - Important to test arguments
        "ethics": 1.1,       # Medium - Professional duties relevant
        "drafting": 0.9,     # Low - Less about drafting
    },
    "criminal": {
        "statute": 1.7,      # High - IPC/CrPC provisions critical
        "precedent": 1.5,    # High - Criminal precedents important
        "limitation": 1.6,   # High - Time limits critical in criminal law
        "risk": 1.8,         # Very High - Liberty at stake
        "devil": 1.3,        # Medium-High - Important for defense
        "ethics": 1.4,       # Medium-High - Professional conduct critical
        "drafting": 0.7,     # Low - Less about drafting
    },
    "civil": {
        "statute": 1.3,      # Medium - CPC and other civil laws
        "precedent": 1.4,    # Medium-High - Case law important
        "limitation": 1.8,   # Very High - Limitation Act critical
        "risk": 1.2,         # Medium - Financial/reputational risks
        "devil": 1.1,        # Medium - Challenge arguments
        "ethics": 1.0,       # Medium - Standard professional duties
        "drafting": 1.3,     # Medium - Pleadings important
    },
    "contract": {
        "statute": 1.4,      # Medium-High - Contract Act provisions
        "precedent": 1.3,    # Medium - Contractual interpretation cases
        "limitation": 1.5,   # High - Time limits for breach claims
        "risk": 1.4,         # Medium-High - Commercial risks
        "devil": 1.2,        # Medium - Contract interpretation challenges
        "ethics": 1.0,       # Medium - Standard duties
        "drafting": 1.6,     # High - Contract drafting important
    },
    "corporate": {
        "statute": 1.6,      # High - Companies Act, SEBI regulations
        "precedent": 1.2,    # Medium - Corporate precedents
        "limitation": 1.1,   # Medium - Some time limitations
        "risk": 1.7,         # Very High - Regulatory and financial risks
        "devil": 1.3,        # Medium-High - Regulatory challenges
        "ethics": 1.5,       # High - Corporate governance ethics
        "drafting": 1.4,     # Medium-High - Corporate documents
    },
    "taxation": {
        "statute": 1.9,      # Very High - Tax statutes critical
        "precedent": 1.4,    # Medium-High - Tax precedents
        "limitation": 1.7,   # High - Assessment time limits
        "risk": 1.6,         # High - Financial penalties
        "devil": 1.1,        # Medium - Tax interpretation challenges
        "ethics": 1.0,       # Medium - Standard duties
        "drafting": 1.0,     # Medium - Returns and representations
    },
    "property": {
        "statute": 1.5,      # High - Transfer of Property Act, etc.
        "precedent": 1.6,    # High - Property law precedents important
        "limitation": 1.9,   # Very High - Limitation Act critical
        "risk": 1.3,         # Medium-High - Property value risks
        "devil": 1.2,        # Medium - Title challenges
        "ethics": 1.0,       # Medium - Standard duties
        "drafting": 1.5,     # High - Property documents
    },
    "family": {
        "statute": 1.4,      # Medium-High - Personal laws
        "precedent": 1.5,    # High - Family law precedents
        "limitation": 1.3,   # Medium-High - Some time limits
        "risk": 1.1,         # Medium - Personal/financial risks
        "devil": 1.0,        # Medium - Family disputes
        "ethics": 1.6,       # High - Sensitive family matters
        "drafting": 1.2,     # Medium - Family settlements
    },
    "intellectual_property": {
        "statute": 1.7,      # High - IP statutes critical
        "precedent": 1.3,    # Medium-High - IP precedents
        "limitation": 1.4,   # Medium-High - Filing deadlines
        "risk": 1.5,         # High - IP value and infringement risks
        "devil": 1.4,        # Medium-High - IP challenges common
        "ethics": 1.1,       # Medium - Professional duties
        "drafting": 1.6,     # High - IP applications and agreements
    },
    "general": {  # Default fallback
    "statute": 1.0,
    "precedent": 1.0,
    "limitation": 1.0,
    "risk": 1.0,
    "devil": 1.0,
    "ethics": 1.0,
    "drafting": 1.0,
}
}

# In-memory cache for weights (in production, this would be in Redis/database)
_WEIGHTS_CACHE: Dict[str, Dict[str, float]] = {}
_CACHE_TIMESTAMP: Dict[str, datetime] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def get_subdomain(query: str) -> str:
    """Classify query into legal subdomain for specialized weight selection"""
    
    query_lower = query.lower()
    
    # Subdomain classification patterns
    subdomain_patterns = {
        "constitutional": [
            r"fundamental\s+right", r"article\s+\d+", r"constitution", r"constitutional",
            r"directive\s+principle", r"writ\s+petition", r"mandamus", r"certiorari",
            r"habeas\s+corpus", r"quo\s+warranto", r"prohibition"
        ],
        "criminal": [
            r"ipc", r"indian\s+penal\s+code", r"crpc", r"criminal", r"fir", r"charge",
            r"prosecution", r"conviction", r"sentence", r"bail", r"custody",
            r"murder", r"theft", r"fraud", r"cheating", r"assault"
        ],
        "civil": [
            r"cpc", r"civil\s+procedure", r"suit", r"plaint", r"damages", r"decree",
            r"injunction", r"specific\s+performance", r"declaration", r"possession",
            r"recovery", r"partition"
        ],
        "contract": [
            r"contract", r"agreement", r"breach", r"performance", r"consideration",
            r"offer", r"acceptance", r"terms", r"conditions", r"obligation",
            r"indian\s+contract\s+act"
        ],
        "corporate": [
            r"company", r"corporate", r"director", r"shareholder", r"companies\s+act",
            r"sebi", r"nclt", r"board", r"dividend", r"merger", r"acquisition",
            r"compliance", r"governance"
        ],
        "taxation": [
            r"income\s+tax", r"gst", r"tax", r"assessment", r"penalty", r"refund",
            r"return", r"customs", r"excise", r"vat", r"tds", r"advance\s+tax"
        ],
        "property": [
            r"property", r"land", r"title", r"ownership", r"possession", r"transfer",
            r"sale", r"purchase", r"lease", r"mortgage", r"easement", r"registration"
        ],
        "family": [
            r"marriage", r"divorce", r"custody", r"maintenance", r"alimony",
            r"succession", r"inheritance", r"adoption", r"guardian", r"minor"
        ],
        "intellectual_property": [
            r"patent", r"trademark", r"copyright", r"design", r"ip", r"infringement",
            r"licensing", r"royalty", r"brand", r"invention"
        ]
    }
    
    # Score each subdomain
    subdomain_scores = {}
    for subdomain, patterns in subdomain_patterns.items():
        score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, query_lower))
            score += matches
        
        if score > 0:
            subdomain_scores[subdomain] = score
    
    # Return highest scoring subdomain, or 'general' if none
    if subdomain_scores:
        best_subdomain = max(subdomain_scores.keys(), key=lambda k: subdomain_scores[k])
        log.debug("subdomain.classified", 
                 query_preview=query[:100],
                 subdomain=best_subdomain,
                 score=subdomain_scores[best_subdomain])
        return best_subdomain
    
    log.debug("subdomain.default", query_preview=query[:100])
    return "general"


def get_weights(subdomain: str) -> Dict[str, float]:
    """Get current weights for a subdomain"""
    
    # Check cache first
    now = datetime.now()
    if (subdomain in _WEIGHTS_CACHE and 
        subdomain in _CACHE_TIMESTAMP and
        (now - _CACHE_TIMESTAMP[subdomain]).total_seconds() < CACHE_TTL_SECONDS):
        return _WEIGHTS_CACHE[subdomain].copy()
    
    # Get default weights for subdomain
    if subdomain in _SUBDOMAIN_WEIGHTS:
        weights = _SUBDOMAIN_WEIGHTS[subdomain].copy()
    else:
        weights = _SUBDOMAIN_WEIGHTS["general"].copy()
    
    # TODO: In production, load from database and merge with defaults
    # weights = await _load_weights_from_db(subdomain, weights)
    
    # Update cache
    _WEIGHTS_CACHE[subdomain] = weights.copy()
    _CACHE_TIMESTAMP[subdomain] = now
    
    return weights


def update_weights(subdomain: str, new_weights: Dict[str, float]) -> None:
    """Update weights for a subdomain"""
    
    # Update cache immediately
    _WEIGHTS_CACHE[subdomain] = new_weights.copy()
    _CACHE_TIMESTAMP[subdomain] = datetime.now()
    
    # TODO: In production, persist to database
    # await _save_weights_to_db(subdomain, new_weights)
    
    log.info("weights.updated", 
            subdomain=subdomain,
            weights=new_weights)


def get_weight(agent: str, subdomain: Optional[str] = None) -> float:
    """Get weight for a specific agent in a subdomain - legacy function"""
    
    if not subdomain:
        subdomain = "general"
    
    weights = get_weights(subdomain)
    return weights.get(agent, 1.0)


def reset_weights(subdomain: str) -> None:
    """Reset weights to default for a subdomain"""
    
    if subdomain in _SUBDOMAIN_WEIGHTS:
        default_weights = _SUBDOMAIN_WEIGHTS[subdomain].copy()
    else:
        default_weights = _SUBDOMAIN_WEIGHTS["general"].copy()
    
    update_weights(subdomain, default_weights)
    log.info("weights.reset", subdomain=subdomain)


def get_all_subdomains() -> list[str]:
    """Get list of all configured subdomains"""
    return list(_SUBDOMAIN_WEIGHTS.keys())


# TODO: Database persistence functions for production
async def _load_weights_from_db(subdomain: str, default_weights: Dict[str, float]) -> Dict[str, float]:
    """Load weights from database and merge with defaults"""
    # This would load from a database table like:
    # CREATE TABLE agent_weights (
    #     subdomain VARCHAR(50),
    #     agent VARCHAR(20),
    #     weight FLOAT,
    #     updated_at TIMESTAMP
    # );
    return default_weights  # Placeholder


async def _save_weights_to_db(subdomain: str, weights: Dict[str, float]) -> None:
    """Save weights to database"""
    # This would save to database with conflict resolution
    pass  # Placeholder


