from __future__ import annotations

from typing import Any, Dict, Optional
import structlog

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.cost_calculator import CostCalculator
from app.billing.subscription import SubscriptionManager

log = structlog.get_logger()


async def ensure_balance(db: AsyncSession, user_id: str, cost_credits: int) -> bool:
    """Check if user has sufficient credit balance"""
    
    row = (await db.execute(text("select credits_balance from billing_accounts where user_id=:u"), {"u": user_id})).first()
    balance = row[0] if row else 0
    
    has_balance = balance >= cost_credits
    
    log.info("credits.balance_check", 
            user_id=user_id, 
            required=cost_credits, 
            available=balance, 
            sufficient=has_balance)
    
    return has_balance


async def debit_credits(db: AsyncSession, user_id: str, run_id: str | None, 
                       delta: int, description: str = "Query execution") -> bool:
    """Debit credits from user account and record transaction"""
    
    try:
        # Check balance first
        if not await ensure_balance(db, user_id, delta):
            log.warning("credits.insufficient_balance", user_id=user_id, required=delta)
            return False
        
        # Record the transaction
        await db.execute(text("""
            insert into billing_ledger (user_id, run_id, credits_delta, description, created_at) 
            values (:u, :r, :d, :desc, NOW())
        """), {
            "u": user_id, 
            "r": run_id, 
            "d": -abs(delta),
            "desc": description
        })
        
        # Update account balance
        await db.execute(text("""
            insert into billing_accounts (user_id, credits_balance) 
            values (:u, 0) 
            on conflict (user_id) do update 
            set credits_balance = billing_accounts.credits_balance - :d
        """), {
            "u": user_id, 
            "d": abs(delta)
        })
        
        await db.commit()
        
        log.info("credits.debited", 
                user_id=user_id, 
                run_id=run_id, 
                amount=delta,
                description=description)
        
        return True
        
    except Exception as e:
        await db.rollback()
        log.error("credits.debit_error", user_id=user_id, error=str(e))
        return False


async def calculate_and_debit_query_cost(db: AsyncSession, user_id: str, run_id: str,
                                       query: str, mode: str, filters: Dict[str, Any] = None,
                                       sources_count: int = 0) -> Dict[str, Any]:
    """Calculate cost for a query and debit if sufficient balance"""
    
    calculator = CostCalculator()
    
    # Calculate query cost
    cost_result = calculator.calculate_query_cost(query, mode, filters or {})
    total_cost = cost_result["total_credits"]
    
    # Add retrieval cost
    if sources_count > 0:
        retrieval_cost = calculator.calculate_retrieval_cost(sources_count)
        total_cost += retrieval_cost["total_credits"]
        cost_result["breakdown"]["retrieval"] = retrieval_cost["total_credits"]
    
    # Check and debit
    if await ensure_balance(db, user_id, total_cost):
        success = await debit_credits(
            db, user_id, run_id, total_cost, 
            f"Query ({mode}) - {total_cost} credits"
        )
        
        return {
            "success": success,
            "cost_breakdown": cost_result,
            "total_cost": total_cost,
            "debited": success
        }
    else:
        # Get current balance for error message
        current_balance = await get_credit_balance(db, user_id)
        
        return {
            "success": False,
            "cost_breakdown": cost_result,
            "total_cost": total_cost,
            "current_balance": current_balance,
            "shortfall": total_cost - current_balance,
            "debited": False
        }


async def calculate_and_debit_document_cost(db: AsyncSession, user_id: str, 
                                          file_size: int, filetype: str,
                                          pages: Optional[int] = None,
                                          ocr_required: bool = False) -> Dict[str, Any]:
    """Calculate and debit cost for document processing"""
    
    calculator = CostCalculator()
    
    cost_result = calculator.calculate_document_cost(file_size, filetype, pages, ocr_required)
    total_cost = cost_result["total_credits"]
    
    if await ensure_balance(db, user_id, total_cost):
        success = await debit_credits(
            db, user_id, None, total_cost,
            f"Document processing - {total_cost} credits"
        )
        
        return {
            "success": success,
            "cost_breakdown": cost_result,
            "total_cost": total_cost,
            "debited": success
        }
    else:
        current_balance = await get_credit_balance(db, user_id)
        
        return {
            "success": False,
            "cost_breakdown": cost_result,
            "total_cost": total_cost,
            "current_balance": current_balance,
            "shortfall": total_cost - current_balance,
            "debited": False
        }


async def calculate_and_debit_export_cost(db: AsyncSession, user_id: str, run_id: str,
                                        export_format: str, run_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Calculate and debit cost for export operation"""
    
    calculator = CostCalculator()
    
    cost_result = calculator.calculate_export_cost(export_format, run_data)
    total_cost = cost_result["total_credits"]
    
    if await ensure_balance(db, user_id, total_cost):
        success = await debit_credits(
            db, user_id, run_id, total_cost,
            f"Export ({export_format}) - {total_cost} credits"
        )
        
        return {
            "success": success,
            "cost_breakdown": cost_result,
            "total_cost": total_cost,
            "debited": success
        }
    else:
        current_balance = await get_credit_balance(db, user_id)
        
        return {
            "success": False,
            "cost_breakdown": cost_result,
            "total_cost": total_cost,
            "current_balance": current_balance,
            "shortfall": total_cost - current_balance,
            "debited": False
        }


async def get_credit_balance(db: AsyncSession, user_id: str) -> int:
    """Get current credit balance for user"""
    
    row = (await db.execute(text("select credits_balance from billing_accounts where user_id=:u"), {"u": user_id})).first()
    return row[0] if row else 0


async def add_credits(db: AsyncSession, user_id: str, amount: int, description: str = "Credit addition") -> bool:
    """Add credits to user account"""
    
    try:
        # Record the transaction
        await db.execute(text("""
            insert into billing_ledger (user_id, run_id, credits_delta, description, created_at) 
            values (:u, NULL, :d, :desc, NOW())
        """), {
            "u": user_id, 
            "d": amount,
            "desc": description
        })
        
        # Update account balance
        await db.execute(text("""
            insert into billing_accounts (user_id, credits_balance) 
            values (:u, :amount) 
            on conflict (user_id) do update 
            set credits_balance = billing_accounts.credits_balance + :amount
        """), {
            "u": user_id, 
            "amount": amount
        })
        
        await db.commit()
        
        log.info("credits.added", user_id=user_id, amount=amount, description=description)
        return True
        
    except Exception as e:
        await db.rollback()
        log.error("credits.add_error", user_id=user_id, error=str(e))
        return False


async def get_usage_summary(db: AsyncSession, user_id: str, days: int = 30) -> Dict[str, Any]:
    """Get usage summary for the specified number of days"""
    
    sql = text("""
        SELECT 
            COUNT(*) as total_transactions,
            SUM(CASE WHEN credits_delta < 0 THEN ABS(credits_delta) ELSE 0 END) as credits_spent,
            SUM(CASE WHEN credits_delta > 0 THEN credits_delta ELSE 0 END) as credits_added,
            SUM(CASE WHEN cost_usd IS NOT NULL THEN cost_usd ELSE 0 END) as total_cost_usd
        FROM billing_ledger 
        WHERE user_id = :user_id 
        AND created_at >= NOW() - INTERVAL ':days days'
    """)
    
    result = (await db.execute(sql, {"user_id": user_id, "days": days})).first()
    
    current_balance = await get_credit_balance(db, user_id)
    
    return {
        "current_balance": current_balance,
        "period_days": days,
        "total_transactions": result[0] or 0,
        "credits_spent": result[1] or 0,
        "credits_added": result[2] or 0,
        "total_cost_usd": float(result[3] or 0),
        "net_credits": (result[2] or 0) - (result[1] or 0)
    }