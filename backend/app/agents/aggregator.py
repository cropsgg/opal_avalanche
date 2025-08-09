from __future__ import annotations

import math
import json
from typing import Dict, List, Any, Optional
import structlog

from app.agents.base import AgentOutput
from app.agents.weights import get_weights, update_weights, get_subdomain
from openai import OpenAI
from app.core.config import get_settings

log = structlog.get_logger()

# Aggregation parameters
ETA = 0.15  # Learning rate for MWU updates
MIN_WEIGHT = 0.2  # Minimum weight to prevent agent suppression
MAX_WEIGHT = 5.0  # Maximum weight to prevent dominance
ALIGNMENT_THRESHOLD = 0.7  # Threshold for considering agents aligned


def aggregate(outputs: Dict[str, AgentOutput], query: str = "", subdomain: Optional[str] = None) -> Dict:
    """
    Aggregate agent outputs using confidence-weighted majority voting with MWU updates
    """
    
    if not outputs:
        return {"answer": "", "weights": {}, "aligned": [], "confidence": 0.0}
    
    log.info("aggregator.start", agents_count=len(outputs))
    
    # Determine subdomain for weight selection
    if not subdomain:
        subdomain = get_subdomain(query)
    
    # Get current weights for this subdomain
    current_weights = get_weights(subdomain)
    weights_before = current_weights.copy()
    
    # Synthesize answer using confidence-weighted approach
    synthesized_answer = _synthesize_answer(outputs, current_weights)
    
    # Determine which agents are aligned with the synthesized answer
    aligned_agents = _determine_alignment(outputs, synthesized_answer)
    
    # Update weights using MWU algorithm
    updated_weights = _update_weights_mwu(current_weights, outputs, aligned_agents)
    
    # Persist updated weights
    update_weights(subdomain, updated_weights)
    
    # Calculate overall confidence
    overall_confidence = _calculate_overall_confidence(outputs, updated_weights, aligned_agents)
    
    log.info("aggregator.complete",
            aligned_count=len(aligned_agents),
            total_agents=len(outputs),
            subdomain=subdomain,
            confidence=overall_confidence)
    
    return {
        "answer": synthesized_answer,
        "weights": updated_weights,
        "weights_before": weights_before,
        "aligned": aligned_agents,
        "confidence": overall_confidence,
        "subdomain": subdomain
    }


def _synthesize_answer(outputs: Dict[str, AgentOutput], weights: Dict[str, float]) -> str:
    """Synthesize final answer from agent outputs using weighted voting"""
    
    # For now, use weighted selection of best reasoning
    # In future, could implement more sophisticated synthesis
    
    weighted_scores = {}
    for agent_name, output in outputs.items():
        agent_weight = weights.get(agent_name, 1.0)
        confidence = output["confidence"]
        
        # Combined score: weight * confidence
        weighted_scores[agent_name] = agent_weight * confidence
    
    # Select agent with highest weighted score
    if not weighted_scores:
        return "No agent outputs available for synthesis."
    
    best_agent = max(weighted_scores.keys(), key=lambda a: weighted_scores[a])
    primary_reasoning = outputs[best_agent]["reasoning"]
    
    # Enhance with insights from other high-scoring agents
    enhanced_answer = _enhance_answer(primary_reasoning, outputs, weighted_scores, best_agent)
    
    return enhanced_answer


def _enhance_answer(primary_reasoning: str, outputs: Dict[str, AgentOutput], 
                   weighted_scores: Dict[str, float], primary_agent: str) -> str:
    """Enhance primary answer with insights from other agents"""
    
    # Get top 2-3 other agents for enhancement
    other_agents = sorted(
        [a for a in weighted_scores.keys() if a != primary_agent],
        key=lambda a: weighted_scores[a],
        reverse=True
    )[:2]
    
    if not other_agents:
        return primary_reasoning
    
    # Simple enhancement: add key insights from other agents
    enhancements = []
    
    for agent in other_agents:
        output = outputs[agent]
        reasoning = output["reasoning"]
        
        # Extract key insights (simplified approach)
        if agent == "risk" and "risk" in reasoning.lower():
            risk_insights = _extract_key_points(reasoning, ["risk", "exposure", "liability"])
            if risk_insights:
                enhancements.append(f"**Risk Considerations**: {risk_insights}")
        
        elif agent == "limitation" and "limitation" in reasoning.lower():
            limitation_insights = _extract_key_points(reasoning, ["limitation", "time", "period"])
            if limitation_insights:
                enhancements.append(f"**Limitation Analysis**: {limitation_insights}")
        
        elif agent == "devil" and ("challenge" in reasoning.lower() or "counter" in reasoning.lower()):
            counter_insights = _extract_key_points(reasoning, ["challenge", "weakness", "counter"])
            if counter_insights:
                enhancements.append(f"**Potential Challenges**: {counter_insights}")
    
    # Combine primary reasoning with enhancements
    if enhancements:
        enhanced = f"{primary_reasoning}\n\n" + "\n\n".join(enhancements)
        return enhanced
    
    return primary_reasoning


def _extract_key_points(text: str, keywords: List[str]) -> str:
    """Extract key points from text containing specified keywords"""
    
    sentences = text.split('. ')
    key_sentences = []
    
    for sentence in sentences[:5]:  # Limit to first 5 sentences
        if any(keyword in sentence.lower() for keyword in keywords):
            key_sentences.append(sentence.strip())
    
    return '. '.join(key_sentences[:2])  # Return up to 2 key sentences


def _determine_alignment(outputs: Dict[str, AgentOutput], synthesized_answer: str) -> List[str]:
    """Determine which agents are aligned with the synthesized answer"""
    
    aligned_agents = []
    
    # Simple alignment heuristic based on reasoning similarity
    # In production, this could use semantic similarity or LLM-based alignment
    
    for agent_name, output in outputs.items():
        agent_reasoning = output["reasoning"]
        confidence = output["confidence"]
        
        # High confidence agents are more likely to be aligned
        if confidence >= 0.7:
            alignment_score = _calculate_alignment_score(agent_reasoning, synthesized_answer)
            if alignment_score >= ALIGNMENT_THRESHOLD:
                aligned_agents.append(agent_name)
        elif confidence >= 0.5:
            # Lower bar for medium confidence agents
            alignment_score = _calculate_alignment_score(agent_reasoning, synthesized_answer)
            if alignment_score >= 0.5:
                aligned_agents.append(agent_name)
    
    # Ensure at least one agent is aligned (the primary contributor)
    if not aligned_agents and outputs:
        # Find agent with highest confidence
        best_agent = max(outputs.keys(), key=lambda a: outputs[a]["confidence"])
        aligned_agents.append(best_agent)
    
    return aligned_agents


def _calculate_alignment_score(agent_reasoning: str, synthesized_answer: str) -> float:
    """Calculate alignment score between agent reasoning and synthesized answer"""
    
    # Simple keyword-based alignment for MVP
    agent_words = set(agent_reasoning.lower().split())
    answer_words = set(synthesized_answer.lower().split())
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall'}
    
    agent_words = agent_words - stop_words
    answer_words = answer_words - stop_words
    
    if not agent_words or not answer_words:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(agent_words & answer_words)
    union = len(agent_words | answer_words)
    
    return intersection / union if union > 0 else 0.0


def _update_weights_mwu(current_weights: Dict[str, float], outputs: Dict[str, AgentOutput], 
                       aligned_agents: List[str]) -> Dict[str, float]:
    """Update weights using Multiplicative Weights Update (MWU) algorithm"""
    
    updated_weights = current_weights.copy()
    
    for agent_name in outputs.keys():
        current_weight = updated_weights.get(agent_name, 1.0)
        
        if agent_name in aligned_agents:
            # Reward aligned agents
            new_weight = current_weight * math.exp(ETA)
        else:
            # Penalize misaligned agents
            new_weight = current_weight * math.exp(-ETA)
        
        # Clamp weights to prevent extreme values
        new_weight = max(MIN_WEIGHT, min(MAX_WEIGHT, new_weight))
        updated_weights[agent_name] = new_weight
    
    return updated_weights


def _calculate_overall_confidence(outputs: Dict[str, AgentOutput], weights: Dict[str, float],
                                aligned_agents: List[str]) -> float:
    """Calculate overall confidence based on agent outputs and alignment"""
    
    if not outputs:
        return 0.0
    
    # Weight-adjusted confidence calculation
    total_weighted_confidence = 0.0
    total_weights = 0.0
    
    for agent_name, output in outputs.items():
        agent_weight = weights.get(agent_name, 1.0)
        agent_confidence = output["confidence"]
        
        # Boost confidence for aligned agents
        if agent_name in aligned_agents:
            adjusted_confidence = min(1.0, agent_confidence * 1.1)
        else:
            adjusted_confidence = agent_confidence * 0.9
        
        total_weighted_confidence += agent_weight * adjusted_confidence
        total_weights += agent_weight
    
    base_confidence = total_weighted_confidence / total_weights if total_weights > 0 else 0.0
    
    # Boost for high alignment
    alignment_ratio = len(aligned_agents) / len(outputs)
    alignment_boost = alignment_ratio * 0.1
    
    final_confidence = min(0.95, base_confidence + alignment_boost)
    
    return final_confidence


# Legacy function for backwards compatibility
def aggregate_simple(outputs: Dict[str, AgentOutput]) -> Dict:
    """Simple aggregation - legacy function"""
    if not outputs:
        return {"answer": "", "weights": {}, "aligned": []}
    # Pick the highest confidence output
    top = max(outputs.items(), key=lambda kv: kv[1]["confidence"])
    return {"answer": top[1]["reasoning"], "weights": {}, "aligned": [top[0]]}


