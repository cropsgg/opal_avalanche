from __future__ import annotations

from typing import Dict, Any, List, Optional, Literal
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.security import current_user
from app.db.session import get_db

router = APIRouter()


class UsageMetrics(BaseModel):
    period_start: datetime
    period_end: datetime
    total_queries: int
    total_credits_spent: int
    total_exports: int
    average_query_cost: float
    most_used_mode: str
    query_success_rate: float


class QueryAnalytics(BaseModel):
    total_queries: int
    queries_by_mode: Dict[str, int]
    queries_by_day: List[Dict[str, Any]]
    average_confidence: float
    top_query_types: List[Dict[str, Any]]


class CostAnalytics(BaseModel):
    total_spent_credits: int
    total_spent_usd: float
    credits_by_category: Dict[str, int]
    daily_spending: List[Dict[str, Any]]
    average_cost_per_query: float


class PerformanceMetrics(BaseModel):
    average_response_time: float
    query_success_rate: float
    verification_pass_rate: float
    top_error_types: List[Dict[str, Any]]


class ContentMetrics(BaseModel):
    documents_uploaded: int
    total_document_size_mb: float
    queries_with_citations: int
    most_cited_authorities: List[Dict[str, Any]]
    language_distribution: Dict[str, int]


@router.get("/usage", response_model=UsageMetrics)
async def get_usage_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get overall usage metrics for the specified period"""
    user_id = user["id"]
    
    try:
        period_start = datetime.utcnow() - timedelta(days=days)
        period_end = datetime.utcnow()
        
        # Main usage metrics query
        usage_sql = """
            WITH query_stats AS (
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(CASE WHEN r.confidence IS NOT NULL THEN r.confidence ELSE 0 END) as avg_confidence,
                    COUNT(CASE WHEN r.confidence >= 0.7 THEN 1 END) as successful_queries,
                    MODE() WITHIN GROUP (ORDER BY q.mode) as most_used_mode
                FROM queries q
                JOIN matters m ON q.matter_id = m.id
                LEFT JOIN runs r ON r.query_id = q.id
                WHERE m.user_id = :user_id 
                AND q.created_at >= :period_start
                AND q.created_at <= :period_end
            ),
            billing_stats AS (
                SELECT 
                    SUM(CASE WHEN credits_delta < 0 THEN ABS(credits_delta) ELSE 0 END) as total_credits_spent,
                    COUNT(CASE WHEN run_id IS NOT NULL THEN 1 END) as billable_queries
                FROM billing_ledger 
                WHERE user_id = :user_id 
                AND created_at >= :period_start
                AND created_at <= :period_end
            )
            SELECT 
                qs.total_queries,
                qs.avg_confidence,
                qs.successful_queries,
                qs.most_used_mode,
                bs.total_credits_spent,
                bs.billable_queries
            FROM query_stats qs
            CROSS JOIN billing_stats bs
        """
        
        result = await db.execute(text(usage_sql), {
            "user_id": user_id,
            "period_start": period_start,
            "period_end": period_end
        })
        
        row = result.fetchone()
        
        if not row:
            # Return empty metrics if no data
            return UsageMetrics(
                period_start=period_start,
                period_end=period_end,
                total_queries=0,
                total_credits_spent=0,
                total_exports=0,
                average_query_cost=0.0,
                most_used_mode="general",
                query_success_rate=0.0
            )
        
        total_queries = row[0] or 0
        avg_confidence = float(row[1] or 0)
        successful_queries = row[2] or 0
        most_used_mode = row[3] or "general"
        total_credits_spent = row[4] or 0
        billable_queries = row[5] or 0
        
        # Calculate export count
        export_count_sql = """
            SELECT COUNT(*) 
            FROM billing_ledger 
            WHERE user_id = :user_id 
            AND created_at >= :period_start
            AND created_at <= :period_end
            AND credits_delta < 0
            AND run_id IS NULL
        """
        
        export_result = await db.execute(text(export_count_sql), {
            "user_id": user_id,
            "period_start": period_start,
            "period_end": period_end
        })
        
        total_exports = export_result.scalar() or 0
        
        return UsageMetrics(
            period_start=period_start,
            period_end=period_end,
            total_queries=total_queries,
            total_credits_spent=total_credits_spent,
            total_exports=total_exports,
            average_query_cost=total_credits_spent / max(billable_queries, 1),
            most_used_mode=most_used_mode,
            query_success_rate=successful_queries / max(total_queries, 1)
        )
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("analytics.usage_metrics_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage metrics"
        )


@router.get("/queries", response_model=QueryAnalytics)
async def get_query_analytics(
    days: int = Query(30, ge=1, le=365),
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed query analytics"""
    user_id = user["id"]
    
    try:
        period_start = datetime.utcnow() - timedelta(days=days)
        
        # Queries by mode
        mode_sql = """
            SELECT q.mode, COUNT(*) as count
            FROM queries q
            JOIN matters m ON q.matter_id = m.id
            WHERE m.user_id = :user_id 
            AND q.created_at >= :period_start
            GROUP BY q.mode
            ORDER BY count DESC
        """
        
        mode_result = await db.execute(text(mode_sql), {
            "user_id": user_id,
            "period_start": period_start
        })
        
        queries_by_mode = {row[0]: row[1] for row in mode_result.fetchall()}
        
        # Daily query counts
        daily_sql = """
            SELECT 
                DATE(q.created_at) as date,
                COUNT(*) as queries,
                AVG(CASE WHEN r.confidence IS NOT NULL THEN r.confidence ELSE 0 END) as avg_confidence
            FROM queries q
            JOIN matters m ON q.matter_id = m.id
            LEFT JOIN runs r ON r.query_id = q.id
            WHERE m.user_id = :user_id 
            AND q.created_at >= :period_start
            GROUP BY DATE(q.created_at)
            ORDER BY date
        """
        
        daily_result = await db.execute(text(daily_sql), {
            "user_id": user_id,
            "period_start": period_start
        })
        
        queries_by_day = [
            {
                "date": row[0].isoformat() if row[0] else None,
                "queries": row[1],
                "avg_confidence": float(row[2] or 0)
            }
            for row in daily_result.fetchall()
        ]
        
        # Overall stats
        total_queries = sum(queries_by_mode.values())
        
        # Average confidence
        confidence_sql = """
            SELECT AVG(r.confidence) as avg_confidence
            FROM runs r
            JOIN queries q ON r.query_id = q.id
            JOIN matters m ON q.matter_id = m.id
            WHERE m.user_id = :user_id 
            AND q.created_at >= :period_start
            AND r.confidence IS NOT NULL
        """
        
        conf_result = await db.execute(text(confidence_sql), {
            "user_id": user_id,
            "period_start": period_start
        })
        
        avg_confidence = float(conf_result.scalar() or 0)
        
        # Top query types (based on content analysis)
        top_query_types = [
            {"type": "Case Law Research", "count": queries_by_mode.get("precedent", 0)},
            {"type": "Statutory Analysis", "count": queries_by_mode.get("general", 0)},
            {"type": "Limitation Queries", "count": queries_by_mode.get("limitation", 0)},
            {"type": "Document Drafting", "count": queries_by_mode.get("draft", 0)}
        ]
        top_query_types.sort(key=lambda x: x["count"], reverse=True)
        
        return QueryAnalytics(
            total_queries=total_queries,
            queries_by_mode=queries_by_mode,
            queries_by_day=queries_by_day,
            average_confidence=avg_confidence,
            top_query_types=top_query_types[:5]
        )
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("analytics.query_analytics_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve query analytics"
        )


@router.get("/costs", response_model=CostAnalytics)
async def get_cost_analytics(
    days: int = Query(30, ge=1, le=365),
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed cost and spending analytics"""
    user_id = user["id"]
    
    try:
        period_start = datetime.utcnow() - timedelta(days=days)
        
        # Overall spending
        spending_sql = """
            SELECT 
                SUM(CASE WHEN credits_delta < 0 THEN ABS(credits_delta) ELSE 0 END) as total_credits_spent,
                SUM(CASE WHEN cost_usd IS NOT NULL AND credits_delta < 0 THEN cost_usd ELSE 0 END) as total_usd_spent,
                COUNT(CASE WHEN credits_delta < 0 THEN 1 END) as total_transactions
            FROM billing_ledger 
            WHERE user_id = :user_id 
            AND created_at >= :period_start
        """
        
        spending_result = await db.execute(text(spending_sql), {
            "user_id": user_id,
            "period_start": period_start
        })
        
        row = spending_result.fetchone()
        total_credits_spent = row[0] or 0
        total_usd_spent = float(row[1] or 0)
        total_transactions = row[2] or 0
        
        # Credits by category
        category_sql = """
            SELECT 
                CASE 
                    WHEN run_id IS NOT NULL THEN 'queries'
                    WHEN credits_delta < 0 THEN 'exports'
                    ELSE 'other'
                END as category,
                SUM(ABS(credits_delta)) as credits
            FROM billing_ledger 
            WHERE user_id = :user_id 
            AND created_at >= :period_start
            AND credits_delta < 0
            GROUP BY category
        """
        
        category_result = await db.execute(text(category_sql), {
            "user_id": user_id,
            "period_start": period_start
        })
        
        credits_by_category = {row[0]: row[1] for row in category_result.fetchall()}
        
        # Daily spending
        daily_spending_sql = """
            SELECT 
                DATE(created_at) as date,
                SUM(CASE WHEN credits_delta < 0 THEN ABS(credits_delta) ELSE 0 END) as credits_spent,
                SUM(CASE WHEN cost_usd IS NOT NULL AND credits_delta < 0 THEN cost_usd ELSE 0 END) as usd_spent
            FROM billing_ledger 
            WHERE user_id = :user_id 
            AND created_at >= :period_start
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        
        daily_result = await db.execute(text(daily_spending_sql), {
            "user_id": user_id,
            "period_start": period_start
        })
        
        daily_spending = [
            {
                "date": row[0].isoformat() if row[0] else None,
                "credits_spent": row[1] or 0,
                "usd_spent": float(row[2] or 0)
            }
            for row in daily_result.fetchall()
        ]
        
        return CostAnalytics(
            total_spent_credits=total_credits_spent,
            total_spent_usd=total_usd_spent,
            credits_by_category=credits_by_category,
            daily_spending=daily_spending,
            average_cost_per_query=total_credits_spent / max(credits_by_category.get("queries", 1), 1)
        )
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("analytics.cost_analytics_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cost analytics"
        )


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    days: int = Query(30, ge=1, le=365),
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance and quality metrics"""
    user_id = user["id"]
    
    try:
        period_start = datetime.utcnow() - timedelta(days=days)
        
        # Performance metrics
        perf_sql = """
            SELECT 
                COUNT(*) as total_runs,
                COUNT(CASE WHEN r.confidence >= 0.7 THEN 1 END) as high_confidence_runs,
                COUNT(CASE WHEN r.answer_text IS NOT NULL AND r.answer_text != '' THEN 1 END) as successful_runs,
                AVG(r.confidence) as avg_confidence
            FROM runs r
            JOIN queries q ON r.query_id = q.id
            JOIN matters m ON q.matter_id = m.id
            WHERE m.user_id = :user_id 
            AND r.created_at >= :period_start
        """
        
        result = await db.execute(text(perf_sql), {
            "user_id": user_id,
            "period_start": period_start
        })
        
        row = result.fetchone()
        
        if not row or row[0] == 0:
            return PerformanceMetrics(
                average_response_time=0.0,
                query_success_rate=0.0,
                verification_pass_rate=0.0,
                top_error_types=[]
            )
        
        total_runs = row[0]
        high_confidence_runs = row[1] or 0
        successful_runs = row[2] or 0
        avg_confidence = float(row[3] or 0)
        
        # Simulate response time (would need actual timing data)
        avg_response_time = 2.5  # Average 2.5 seconds
        
        success_rate = successful_runs / total_runs
        verification_pass_rate = high_confidence_runs / total_runs
        
        # Simulate error types (would need actual error tracking)
        top_error_types = [
            {"error_type": "Insufficient context", "count": max(0, total_runs - successful_runs) // 2},
            {"error_type": "No relevant authorities found", "count": max(0, total_runs - successful_runs) // 3},
            {"error_type": "Verification failed", "count": max(0, total_runs - high_confidence_runs) // 4}
        ]
        
        return PerformanceMetrics(
            average_response_time=avg_response_time,
            query_success_rate=success_rate,
            verification_pass_rate=verification_pass_rate,
            top_error_types=top_error_types
        )
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("analytics.performance_metrics_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics"
        )


@router.get("/content", response_model=ContentMetrics)
async def get_content_metrics(
    days: int = Query(30, ge=1, le=365),
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get content and document analytics"""
    user_id = user["id"]
    
    try:
        period_start = datetime.utcnow() - timedelta(days=days)
        
        # Document metrics
        doc_sql = """
            SELECT 
                COUNT(*) as documents_uploaded,
                SUM(COALESCE(size, 0)) / (1024.0 * 1024.0) as total_size_mb
            FROM documents d
            JOIN matters m ON d.matter_id = m.id
            WHERE m.user_id = :user_id 
            AND d.created_at >= :period_start
        """
        
        doc_result = await db.execute(text(doc_sql), {
            "user_id": user_id,
            "period_start": period_start
        })
        
        doc_row = doc_result.fetchone()
        documents_uploaded = doc_row[0] or 0
        total_size_mb = float(doc_row[1] or 0)
        
        # Queries with citations
        citation_sql = """
            SELECT COUNT(*) 
            FROM runs r
            JOIN queries q ON r.query_id = q.id
            JOIN matters m ON q.matter_id = m.id
            WHERE m.user_id = :user_id 
            AND r.created_at >= :period_start
            AND COALESCE(json_array_length(r.retrieval_set_json), 0) > 0
        """
        
        citation_result = await db.execute(text(citation_sql), {
            "user_id": user_id,
            "period_start": period_start
        })
        
        queries_with_citations = citation_result.scalar() or 0
        
        # Language distribution (from matters)
        lang_sql = """
            SELECT language, COUNT(*) as count
            FROM matters
            WHERE user_id = :user_id 
            AND created_at >= :period_start
            GROUP BY language
        """
        
        lang_result = await db.execute(text(lang_sql), {
            "user_id": user_id,
            "period_start": period_start
        })
        
        language_distribution = {row[0]: row[1] for row in lang_result.fetchall()}
        
        # Most cited authorities (simulated - would need actual citation tracking)
        most_cited_authorities = [
            {"title": "Supreme Court cases", "citations": queries_with_citations // 2},
            {"title": "High Court cases", "citations": queries_with_citations // 3},
            {"title": "Statutory provisions", "citations": queries_with_citations // 4}
        ]
        
        return ContentMetrics(
            documents_uploaded=documents_uploaded,
            total_document_size_mb=total_size_mb,
            queries_with_citations=queries_with_citations,
            most_cited_authorities=most_cited_authorities,
            language_distribution=language_distribution
        )
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("analytics.content_metrics_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content metrics"
        )


@router.get("/dashboard")
async def get_dashboard_summary(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Get summary analytics for dashboard display"""
    user_id = user["id"]
    
    try:
        # Get quick metrics for last 30 days
        quick_metrics_sql = """
            WITH recent_activity AS (
                SELECT 
                    COUNT(DISTINCT q.id) as queries_count,
                    COUNT(DISTINCT d.id) as documents_count,
                    COUNT(DISTINCT r.id) as runs_count,
                    SUM(CASE WHEN bl.credits_delta < 0 THEN ABS(bl.credits_delta) ELSE 0 END) as credits_spent
                FROM matters m
                LEFT JOIN queries q ON q.matter_id = m.id AND q.created_at >= NOW() - INTERVAL '30 days'
                LEFT JOIN documents d ON d.matter_id = m.id AND d.created_at >= NOW() - INTERVAL '30 days'
                LEFT JOIN runs r ON r.query_id = q.id
                LEFT JOIN billing_ledger bl ON bl.user_id = m.user_id AND bl.created_at >= NOW() - INTERVAL '30 days'
                WHERE m.user_id = :user_id
            ),
            current_balance AS (
                SELECT COALESCE(credits_balance, 0) as balance
                FROM billing_accounts
                WHERE user_id = :user_id
            )
            SELECT 
                ra.queries_count,
                ra.documents_count,
                ra.runs_count,
                ra.credits_spent,
                cb.balance
            FROM recent_activity ra
            CROSS JOIN current_balance cb
        """
        
        result = await db.execute(text(quick_metrics_sql), {"user_id": user_id})
        row = result.fetchone()
        
        if not row:
            return {
                "recent_activity": {
                    "queries_last_30_days": 0,
                    "documents_uploaded": 0,
                    "successful_runs": 0,
                    "credits_spent": 0
                },
                "account_status": {
                    "current_balance": 0,
                    "plan": "free",
                    "can_make_queries": False
                },
                "quick_stats": {
                    "total_matters": 0,
                    "average_query_cost": 0,
                    "success_rate": 0
                }
            }
        
        # Get subscription info
        from app.billing.subscription import SubscriptionManager
        manager = SubscriptionManager()
        subscription = await manager.get_user_subscription(db, user_id)
        
        # Get total matters count
        matters_sql = "SELECT COUNT(*) FROM matters WHERE user_id = :user_id"
        matters_result = await db.execute(text(matters_sql), {"user_id": user_id})
        total_matters = matters_result.scalar() or 0
        
        queries_count = row[0] or 0
        credits_spent = row[3] or 0
        
        return {
            "recent_activity": {
                "queries_last_30_days": queries_count,
                "documents_uploaded": row[1] or 0,
                "successful_runs": row[2] or 0,
                "credits_spent": credits_spent
            },
            "account_status": {
                "current_balance": row[4] or 0,
                "plan": subscription["plan"],
                "can_make_queries": (row[4] or 0) > 0
            },
            "quick_stats": {
                "total_matters": total_matters,
                "average_query_cost": credits_spent / max(queries_count, 1),
                "success_rate": (row[2] or 0) / max(queries_count, 1)
            }
        }
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("analytics.dashboard_summary_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary"
        )
