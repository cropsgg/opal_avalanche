from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional
import structlog

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

log = structlog.get_logger()


class SubscriptionManager:
    """Manage user subscriptions and plan upgrades/downgrades"""
    
    PLANS = {
        "free": {
            "name": "Free Tier",
            "monthly_cost": 0,
            "included_credits": 100,
            "daily_query_limit": 3,
            "features": ["basic_queries", "document_upload_5mb", "exports_limited"]
        },
        "starter": {
            "name": "Starter Plan",
            "monthly_cost": 29,
            "included_credits": 500,
            "daily_query_limit": 20,
            "features": ["all_query_modes", "document_upload_50mb", "exports_unlimited", "priority_queue"]
        },
        "professional": {
            "name": "Professional Plan", 
            "monthly_cost": 99,
            "included_credits": 2000,
            "daily_query_limit": 100,
            "features": ["all_features", "api_access", "priority_support", "document_upload_200mb", "bulk_processing"]
        },
        "enterprise": {
            "name": "Enterprise Plan",
            "monthly_cost": 299,
            "included_credits": 8000,
            "daily_query_limit": None,  # Unlimited
            "features": ["all_features", "api_access", "priority_support", "white_label", "document_upload_1gb", "custom_integrations"]
        }
    }
    
    async def get_user_subscription(self, db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Get current subscription details for user"""
        
        sql = text("""
            SELECT plan, credits_balance, renews_at, created_at
            FROM billing_accounts 
            WHERE user_id = :user_id
        """)
        
        result = (await db.execute(sql, {"user_id": user_id})).first()
        
        if not result:
            # Create free tier account
            await self.create_free_account(db, user_id)
            return {
                "plan": "free",
                "credits_balance": 100,
                "renews_at": date.today() + timedelta(days=30),
                "status": "active",
                "plan_details": self.PLANS["free"]
            }
        
        plan = result.plan
        return {
            "plan": plan,
            "credits_balance": result.credits_balance,
            "renews_at": result.renews_at,
            "status": self._get_subscription_status(result.renews_at),
            "plan_details": self.PLANS.get(plan, self.PLANS["free"]),
            "created_at": result.created_at
        }
    
    async def create_free_account(self, db: AsyncSession, user_id: str) -> None:
        """Create a free tier account for new user"""
        
        sql = text("""
            INSERT INTO billing_accounts (user_id, plan, credits_balance, renews_at)
            VALUES (:user_id, 'free', 100, :renews_at)
            ON CONFLICT (user_id) DO NOTHING
        """)
        
        renews_at = date.today() + timedelta(days=30)
        await db.execute(sql, {"user_id": user_id, "renews_at": renews_at})
        await db.commit()
        
        log.info("subscription.free_account_created", user_id=user_id)
    
    async def upgrade_subscription(self, db: AsyncSession, user_id: str, 
                                 new_plan: str, payment_method: str = "stripe") -> Dict[str, Any]:
        """Upgrade user subscription to a new plan"""
        
        if new_plan not in self.PLANS:
            raise ValueError(f"Invalid plan: {new_plan}")
        
        current_sub = await self.get_user_subscription(db, user_id)
        current_plan = current_sub["plan"]
        
        if current_plan == new_plan:
            return {"success": False, "error": "Already on this plan"}
        
        plan_details = self.PLANS[new_plan]
        
        # Calculate prorated cost if upgrading mid-cycle
        proration_amount = await self._calculate_proration(db, user_id, current_plan, new_plan)
        
        # Start subscription immediately
        start_date = date.today()
        renews_at = start_date + timedelta(days=30)
        
        # Update subscription
        sql = text("""
            UPDATE billing_accounts 
            SET plan = :plan, 
                credits_balance = credits_balance + :credits,
                renews_at = :renews_at
            WHERE user_id = :user_id
        """)
        
        await db.execute(sql, {
            "user_id": user_id,
            "plan": new_plan,
            "credits": plan_details["included_credits"],
            "renews_at": renews_at
        })
        
        # Record billing transaction
        await self._record_billing_transaction(
            db, user_id, None, plan_details["included_credits"], 
            plan_details["monthly_cost"], f"Subscription upgrade to {new_plan}"
        )
        
        await db.commit()
        
        log.info("subscription.upgraded", 
                user_id=user_id, 
                from_plan=current_plan, 
                to_plan=new_plan,
                proration=proration_amount)
        
        return {
            "success": True,
            "new_plan": new_plan,
            "credits_added": plan_details["included_credits"],
            "proration_amount": proration_amount,
            "renews_at": renews_at
        }
    
    async def renew_subscription(self, db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Renew user's current subscription"""
        
        current_sub = await self.get_user_subscription(db, user_id)
        plan = current_sub["plan"]
        
        if plan == "free":
            # Free tier auto-renews with limited credits
            new_credits = 100
            renewal_date = date.today() + timedelta(days=30)
        else:
            plan_details = self.PLANS[plan]
            new_credits = plan_details["included_credits"]
            renewal_date = current_sub["renews_at"] + timedelta(days=30)
        
        # Update subscription
        sql = text("""
            UPDATE billing_accounts
            SET credits_balance = credits_balance + :credits,
                renews_at = :renews_at
            WHERE user_id = :user_id
        """)
        
        await db.execute(sql, {
            "user_id": user_id,
            "credits": new_credits,
            "renews_at": renewal_date
        })
        
        # Record transaction
        cost = self.PLANS[plan]["monthly_cost"]
        await self._record_billing_transaction(
            db, user_id, None, new_credits, cost, f"Subscription renewal - {plan}"
        )
        
        await db.commit()
        
        log.info("subscription.renewed", user_id=user_id, plan=plan, credits_added=new_credits)
        
        return {
            "success": True,
            "credits_added": new_credits,
            "next_renewal": renewal_date,
            "cost": cost
        }
    
    async def cancel_subscription(self, db: AsyncSession, user_id: str, 
                                immediate: bool = False) -> Dict[str, Any]:
        """Cancel user subscription"""
        
        current_sub = await self.get_user_subscription(db, user_id)
        
        if current_sub["plan"] == "free":
            return {"success": False, "error": "Cannot cancel free tier"}
        
        if immediate:
            # Immediate cancellation - downgrade to free
            sql = text("""
                UPDATE billing_accounts
                SET plan = 'free',
                    credits_balance = LEAST(credits_balance, 100),
                    renews_at = :renews_at
                WHERE user_id = :user_id
            """)
            
            renews_at = date.today() + timedelta(days=30)
            await db.execute(sql, {"user_id": user_id, "renews_at": renews_at})
            
            log.info("subscription.cancelled_immediate", user_id=user_id)
            
            return {
                "success": True,
                "cancellation_type": "immediate",
                "refund_amount": self._calculate_refund(current_sub)
            }
        else:
            # End of billing cycle cancellation
            # For now, just mark in a separate cancellations table
            # or add a flag to the account
            log.info("subscription.cancelled_end_of_cycle", user_id=user_id)
            
            return {
                "success": True,
                "cancellation_type": "end_of_cycle",
                "effective_date": current_sub["renews_at"]
            }
    
    async def purchase_credits(self, db: AsyncSession, user_id: str, 
                             credits: int, cost_usd: float) -> Dict[str, Any]:
        """Purchase additional credits"""
        
        sql = text("""
            UPDATE billing_accounts
            SET credits_balance = credits_balance + :credits
            WHERE user_id = :user_id
        """)
        
        await db.execute(sql, {"user_id": user_id, "credits": credits})
        
        # Record transaction
        await self._record_billing_transaction(
            db, user_id, None, credits, cost_usd, "Credit purchase"
        )
        
        await db.commit()
        
        log.info("credits.purchased", user_id=user_id, credits=credits, cost=cost_usd)
        
        return {
            "success": True,
            "credits_added": credits,
            "cost": cost_usd,
            "new_balance": await self._get_credit_balance(db, user_id)
        }
    
    async def check_usage_limits(self, db: AsyncSession, user_id: str, 
                               operation: str) -> Dict[str, Any]:
        """Check if user can perform operation within their plan limits"""
        
        subscription = await self.get_user_subscription(db, user_id)
        plan = subscription["plan"]
        plan_details = self.PLANS[plan]
        
        # Check credit balance
        if subscription["credits_balance"] <= 0:
            return {
                "allowed": False,
                "reason": "insufficient_credits",
                "current_balance": subscription["credits_balance"]
            }
        
        # Check daily query limit
        if operation == "query":
            daily_limit = plan_details["daily_query_limit"]
            if daily_limit is not None:
                today_queries = await self._get_daily_query_count(db, user_id)
                if today_queries >= daily_limit:
                    return {
                        "allowed": False,
                        "reason": "daily_limit_exceeded",
                        "daily_limit": daily_limit,
                        "today_queries": today_queries
                    }
        
        # Check feature access
        if operation == "api_access" and "api_access" not in plan_details["features"]:
            return {
                "allowed": False,
                "reason": "feature_not_available",
                "required_plan": "professional"
            }
        
        return {
            "allowed": True,
            "credits_available": subscription["credits_balance"],
            "plan": plan
        }
    
    async def _calculate_proration(self, db: AsyncSession, user_id: str, 
                                 current_plan: str, new_plan: str) -> float:
        """Calculate prorated amount for plan change"""
        
        current_cost = self.PLANS[current_plan]["monthly_cost"]
        new_cost = self.PLANS[new_plan]["monthly_cost"]
        
        # Get days remaining in current cycle
        subscription = await self.get_user_subscription(db, user_id)
        days_remaining = (subscription["renews_at"] - date.today()).days
        
        # Calculate prorated amounts
        daily_current = current_cost / 30
        daily_new = new_cost / 30
        
        current_refund = daily_current * days_remaining
        new_charge = daily_new * days_remaining
        
        return max(0, new_charge - current_refund)
    
    def _calculate_refund(self, subscription: Dict[str, Any]) -> float:
        """Calculate refund amount for cancelled subscription"""
        
        plan = subscription["plan"]
        monthly_cost = self.PLANS[plan]["monthly_cost"]
        
        days_remaining = (subscription["renews_at"] - date.today()).days
        daily_rate = monthly_cost / 30
        
        return max(0, daily_rate * days_remaining)
    
    async def _get_daily_query_count(self, db: AsyncSession, user_id: str) -> int:
        """Get number of queries made today"""
        
        sql = text("""
            SELECT COUNT(*)
            FROM queries q
            JOIN matters m ON q.matter_id = m.id
            WHERE m.user_id = :user_id
            AND DATE(q.created_at) = CURRENT_DATE
        """)
        
        result = (await db.execute(sql, {"user_id": user_id})).scalar()
        return result or 0
    
    async def _get_credit_balance(self, db: AsyncSession, user_id: str) -> int:
        """Get current credit balance"""
        
        sql = text("SELECT credits_balance FROM billing_accounts WHERE user_id = :user_id")
        result = (await db.execute(sql, {"user_id": user_id})).scalar()
        return result or 0
    
    async def _record_billing_transaction(self, db: AsyncSession, user_id: str, 
                                        run_id: Optional[str], credits_delta: int,
                                        cost_usd: float, description: str) -> None:
        """Record a billing transaction"""
        
        sql = text("""
            INSERT INTO billing_ledger (user_id, run_id, credits_delta, cost_usd, description, created_at)
            VALUES (:user_id, :run_id, :credits_delta, :cost_usd, :description, NOW())
        """)
        
        await db.execute(sql, {
            "user_id": user_id,
            "run_id": run_id,
            "credits_delta": credits_delta,
            "cost_usd": cost_usd,
            "description": description
        })
    
    def _get_subscription_status(self, renews_at: date) -> str:
        """Determine subscription status"""
        
        today = date.today()
        
        if renews_at < today:
            return "expired"
        elif (renews_at - today).days <= 7:
            return "expiring_soon"
        else:
            return "active"
    
    async def get_billing_history(self, db: AsyncSession, user_id: str, 
                                limit: int = 50) -> List[Dict[str, Any]]:
        """Get billing history for user"""
        
        sql = text("""
            SELECT run_id, credits_delta, cost_usd, description, created_at
            FROM billing_ledger 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT :limit
        """)
        
        result = (await db.execute(sql, {"user_id": user_id, "limit": limit})).mappings().all()
        return [dict(row) for row in result]
