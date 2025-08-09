from __future__ import annotations

from typing import Dict, Any, List, Literal
from uuid import UUID
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.security import current_user
from app.db.session import get_db
from app.billing.subscription import SubscriptionManager
from app.billing.credits import add_credits, get_credit_balance, get_usage_summary

router = APIRouter()


class SubscriptionInfo(BaseModel):
    plan: str
    plan_name: str
    monthly_cost: int
    credits_balance: int
    included_credits: int
    daily_query_limit: int | None
    features: List[str]
    renews_at: date | None
    usage_this_month: Dict[str, int]


class PlanUpgradeRequest(BaseModel):
    new_plan: Literal["free", "starter", "professional", "enterprise"]
    billing_cycle: Literal["monthly", "yearly"] = "monthly"


class CreditPurchaseRequest(BaseModel):
    package: Literal["small", "medium", "large", "bulk"]
    payment_method_id: str  # Stripe payment method ID


class UsageAnalytics(BaseModel):
    period_days: int
    total_queries: int
    total_credits_spent: int
    total_credits_added: int
    net_credits: int
    current_balance: int
    daily_breakdown: List[Dict[str, Any]]


@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Get user's current subscription information"""
    user_id = user["id"]
    
    try:
        manager = SubscriptionManager()
        subscription = await manager.get_user_subscription(db, user_id)
        
        # Get usage for this month
        usage = await get_usage_summary(db, user_id, days=30)
        
        return SubscriptionInfo(
            plan=subscription["plan"],
            plan_name=subscription["plan_details"]["name"],
            monthly_cost=subscription["plan_details"]["monthly_cost"],
            credits_balance=subscription["credits_balance"],
            included_credits=subscription["plan_details"]["included_credits"],
            daily_query_limit=subscription["plan_details"]["daily_query_limit"],
            features=subscription["plan_details"]["features"],
            renews_at=subscription["renews_at"],
            usage_this_month={
                "queries": usage["total_transactions"],
                "credits_spent": usage["credits_spent"],
                "credits_added": usage["credits_added"]
            }
        )
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("subscription.get_info_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription information"
        )


@router.get("/plans")
async def get_available_plans():
    """Get all available subscription plans"""
    manager = SubscriptionManager()
    
    return {
        "plans": manager.PLANS,
        "credit_packages": {
            "small": {"credits": 100, "cost_usd": 9.99, "bonus_credits": 0},
            "medium": {"credits": 500, "cost_usd": 39.99, "bonus_credits": 50},
            "large": {"credits": 1000, "cost_usd": 69.99, "bonus_credits": 150},
            "bulk": {"credits": 5000, "cost_usd": 299.99, "bonus_credits": 1000}
        },
        "comparison": {
            "features": {
                "document_upload_limit": {
                    "free": "5MB",
                    "starter": "50MB", 
                    "professional": "200MB",
                    "enterprise": "1GB"
                },
                "daily_queries": {
                    "free": 3,
                    "starter": 20,
                    "professional": 100,
                    "enterprise": "Unlimited"
                },
                "exports": {
                    "free": "Limited (10/month)",
                    "starter": "Unlimited",
                    "professional": "Unlimited",
                    "enterprise": "Unlimited"
                },
                "api_access": {
                    "free": False,
                    "starter": False,
                    "professional": True,
                    "enterprise": True
                },
                "priority_support": {
                    "free": False,
                    "starter": False,
                    "professional": True,
                    "enterprise": True
                }
            }
        }
    }


@router.post("/upgrade")
async def upgrade_subscription(
    request: PlanUpgradeRequest,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade or change subscription plan"""
    user_id = user["id"]
    
    import structlog
    log = structlog.get_logger()
    log.info("subscription.upgrade_request", 
            user_id=user_id, 
            new_plan=request.new_plan,
            billing_cycle=request.billing_cycle)
    
    try:
        manager = SubscriptionManager()
        
        # Get current subscription
        current_sub = await manager.get_user_subscription(db, user_id)
        current_plan = current_sub["plan"]
        
        if current_plan == request.new_plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Already subscribed to {request.new_plan} plan"
            )
        
        # Perform upgrade/downgrade
        result = await manager.change_subscription(db, user_id, request.new_plan)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        log.info("subscription.upgrade_success",
                user_id=user_id,
                old_plan=current_plan,
                new_plan=request.new_plan,
                prorated_amount=result["prorated_amount"])
        
        return {
            "status": "success",
            "old_plan": current_plan,
            "new_plan": request.new_plan,
            "effective_date": result["effective_date"],
            "prorated_amount": result["prorated_amount"],
            "new_credits_balance": result["new_credits_balance"],
            "message": f"Successfully upgraded to {request.new_plan} plan"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error("subscription.upgrade_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade subscription"
        )


@router.post("/cancel")
async def cancel_subscription(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Cancel subscription (downgrade to free plan)"""
    user_id = user["id"]
    
    import structlog
    log = structlog.get_logger()
    log.info("subscription.cancel_request", user_id=user_id)
    
    try:
        manager = SubscriptionManager()
        
        # Get current subscription
        current_sub = await manager.get_user_subscription(db, user_id)
        current_plan = current_sub["plan"]
        
        if current_plan == "free":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already on free plan"
            )
        
        # Cancel subscription (downgrade to free)
        result = await manager.cancel_subscription(db, user_id)
        
        log.info("subscription.cancel_success", 
                user_id=user_id,
                old_plan=current_plan,
                effective_date=result["effective_date"])
        
        return {
            "status": "cancelled",
            "old_plan": current_plan,
            "new_plan": "free",
            "effective_date": result["effective_date"],
            "remaining_credits": result["remaining_credits"],
            "message": "Subscription cancelled successfully. You'll remain on your current plan until the end of the billing period."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error("subscription.cancel_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.post("/credits/purchase")
async def purchase_credits(
    request: CreditPurchaseRequest,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Purchase additional credits"""
    user_id = user["id"]
    
    import structlog
    log = structlog.get_logger()
    log.info("credits.purchase_request", 
            user_id=user_id, 
            package=request.package,
            payment_method_id=request.payment_method_id)
    
    try:
        # Credit packages with pricing
        packages = {
            "small": {"credits": 100, "cost_usd": 9.99, "bonus": 0},
            "medium": {"credits": 500, "cost_usd": 39.99, "bonus": 50},
            "large": {"credits": 1000, "cost_usd": 69.99, "bonus": 150},
            "bulk": {"credits": 5000, "cost_usd": 299.99, "bonus": 1000}
        }
        
        if request.package not in packages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credit package"
            )
        
        package_info = packages[request.package]
        total_credits = package_info["credits"] + package_info["bonus"]
        cost_usd = package_info["cost_usd"]
        
        # TODO: Process payment with Stripe using payment_method_id
        # For now, simulate successful payment
        payment_successful = True
        transaction_id = f"pi_mock_{datetime.utcnow().isoformat()}"
        
        if not payment_successful:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Payment failed"
            )
        
        # Add credits to user account
        success = await add_credits(
            db, user_id, total_credits, 
            f"Credit purchase - {request.package} package"
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add credits to account"
            )
        
        # Get new balance
        new_balance = await get_credit_balance(db, user_id)
        
        log.info("credits.purchase_success",
                user_id=user_id,
                package=request.package,
                credits_added=total_credits,
                cost_usd=cost_usd,
                new_balance=new_balance,
                transaction_id=transaction_id)
        
        return {
            "status": "success",
            "package": request.package,
            "credits_purchased": package_info["credits"],
            "bonus_credits": package_info["bonus"],
            "total_credits_added": total_credits,
            "cost_usd": cost_usd,
            "new_balance": new_balance,
            "transaction_id": transaction_id,
            "message": f"Successfully purchased {total_credits} credits"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error("credits.purchase_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process credit purchase"
        )


@router.get("/usage", response_model=UsageAnalytics)
async def get_usage_analytics(
    days: int = 30,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed usage analytics for user"""
    user_id = user["id"]
    
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be between 1 and 365"
        )
    
    try:
        # Get overall usage summary
        usage = await get_usage_summary(db, user_id, days)
        
        # Get daily breakdown
        daily_query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as queries,
                SUM(CASE WHEN credits_delta < 0 THEN ABS(credits_delta) ELSE 0 END) as credits_spent
            FROM billing_ledger 
            WHERE user_id = :user_id 
            AND created_at >= NOW() - (:days || ' days')::interval
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 100
        """
        
        result = await db.execute(text(daily_query), {"user_id": user_id, "days": days})
        daily_data = result.fetchall()
        
        daily_breakdown = [
            {
                "date": row[0].isoformat() if row[0] else None,
                "queries": row[1] or 0,
                "credits_spent": row[2] or 0
            }
            for row in daily_data
        ]
        
        return UsageAnalytics(
            period_days=days,
            total_queries=usage["total_transactions"],
            total_credits_spent=usage["credits_spent"],
            total_credits_added=usage["credits_added"],
            net_credits=usage["net_credits"],
            current_balance=usage["current_balance"],
            daily_breakdown=daily_breakdown
        )
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("subscription.usage_analytics_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage analytics"
        )


@router.get("/limits")
async def check_usage_limits(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Check current usage against plan limits"""
    user_id = user["id"]
    
    try:
        manager = SubscriptionManager()
        
        # Check various limits
        query_limit_check = await manager.check_usage_limits(db, user_id, "query")
        api_access_check = await manager.check_usage_limits(db, user_id, "api_access")
        
        subscription = await manager.get_user_subscription(db, user_id)
        
        # Get current usage
        daily_queries = await manager._get_daily_query_count(db, user_id)
        
        return {
            "plan": subscription["plan"],
            "credits_balance": subscription["credits_balance"],
            "daily_queries": {
                "used_today": daily_queries,
                "limit": subscription["plan_details"]["daily_query_limit"],
                "can_query": query_limit_check["allowed"],
                "limit_type": "unlimited" if subscription["plan_details"]["daily_query_limit"] is None else "limited"
            },
            "features": {
                "api_access": api_access_check["allowed"],
                "exports_unlimited": "exports_unlimited" in subscription["plan_details"]["features"],
                "priority_support": "priority_support" in subscription["plan_details"]["features"]
            },
            "status": {
                "can_make_queries": query_limit_check["allowed"],
                "needs_upgrade": not query_limit_check["allowed"] or subscription["credits_balance"] <= 0
            }
        }
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("subscription.limits_check_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check usage limits"
        )


@router.get("/billing-history")
async def get_billing_history(
    limit: int = 50,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's billing transaction history"""
    user_id = user["id"]
    
    if limit < 1 or limit > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 200"
        )
    
    try:
        billing_query = """
            SELECT 
                id,
                run_id,
                credits_delta,
                cost_usd,
                created_at,
                CASE 
                    WHEN credits_delta > 0 THEN 'credit_purchase'
                    WHEN run_id IS NOT NULL THEN 'query_usage'
                    ELSE 'other'
                END as transaction_type
            FROM billing_ledger 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT :limit
        """
        
        result = await db.execute(text(billing_query), {"user_id": user_id, "limit": limit})
        transactions = result.fetchall()
        
        history = []
        for tx in transactions:
            history.append({
                "id": str(tx[0]),
                "run_id": str(tx[1]) if tx[1] else None,
                "credits_delta": tx[2],
                "cost_usd": float(tx[3]) if tx[3] else None,
                "created_at": tx[4].isoformat() if tx[4] else None,
                "transaction_type": tx[5],
                "description": _generate_transaction_description(tx[5], tx[2], tx[1])
            })
        
        return {
            "transactions": history,
            "total_returned": len(history),
            "has_more": len(history) == limit
        }
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("subscription.billing_history_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve billing history"
        )


def _generate_transaction_description(tx_type: str, credits_delta: int, run_id: str | None) -> str:
    """Generate human-readable transaction description"""
    if tx_type == "credit_purchase":
        return f"Credit purchase (+{credits_delta} credits)"
    elif tx_type == "query_usage":
        return f"Query processing ({credits_delta} credits)"
    elif credits_delta > 0:
        return f"Credit addition (+{credits_delta} credits)"
    elif credits_delta < 0:
        return f"Credit usage ({credits_delta} credits)"
    else:
        return "Transaction"
