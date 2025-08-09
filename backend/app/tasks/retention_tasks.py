from __future__ import annotations

from datetime import datetime
import structlog

from app.core.tasks import get_celery
from app.core.data_retention import get_retention_manager

log = structlog.get_logger()


@get_celery().task(name="app.tasks.retention_tasks.run_retention_policy")
def run_retention_policy():
    """
    Scheduled task to apply data retention policy
    Should be run daily via cron job or scheduler
    """
    import asyncio
    
    async def _run_policy():
        log.info("retention_task.start")
        
        try:
            manager = get_retention_manager()
            results = await manager.apply_retention_policy()
            
            log.info("retention_task.complete",
                    queries_processed=results["queries_processed"],
                    pii_records_processed=results["pii_records_processed"],
                    crypto_shredded=results["crypto_shredded"],
                    hard_deleted=results["hard_deleted"],
                    errors_count=len(results["errors"]))
            
            # Log errors if any
            if results["errors"]:
                for error in results["errors"][:10]:  # Log first 10 errors
                    log.error("retention_task.error", error=error)
            
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                **{k: v for k, v in results.items() if k != "errors"},
                "errors_count": len(results["errors"])
            }
            
        except Exception as e:
            log.error("retention_task.failed", error=str(e))
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return asyncio.run(_run_policy())


@get_celery().task(name="app.tasks.retention_tasks.process_user_deletion")
def process_user_deletion(user_id: str, reason: str = "user_request"):
    """
    Process immediate user data deletion (GDPR/DPDP right to be forgotten)
    """
    import asyncio
    
    async def _process_deletion():
        log.info("user_deletion_task.start", user_id=user_id, reason=reason)
        
        try:
            manager = get_retention_manager()
            results = await manager.process_user_deletion_request(user_id, reason)
            
            log.info("user_deletion_task.complete",
                    user_id=user_id,
                    queries_shredded=results["queries_shredded"],
                    runs_shredded=results["runs_shredded"],
                    pii_shredded=results["pii_shredded"],
                    matters_marked=results["matters_marked"])
            
            return {
                "status": "success",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                **{k: v for k, v in results.items() if k != "errors"},
                "errors_count": len(results["errors"])
            }
            
        except Exception as e:
            log.error("user_deletion_task.failed", user_id=user_id, error=str(e))
            return {
                "status": "failed",
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return asyncio.run(_process_deletion())


@get_celery().task(name="app.tasks.retention_tasks.cleanup_old_retention_logs")
def cleanup_old_retention_logs():
    """
    Clean up old retention logs (keep for 2 years for audit)
    """
    import asyncio
    from sqlalchemy import text
    from app.db.session import SessionLocal
    from datetime import timedelta
    
    async def _cleanup():
        log.info("retention_logs_cleanup.start")
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=730)  # 2 years
            
            async with SessionLocal() as db:
                result = await db.execute(
                    text("DELETE FROM data_retention_logs WHERE deleted_at < :cutoff_date"),
                    {"cutoff_date": cutoff_date}
                )
                
                deleted_count = result.rowcount
                await db.commit()
                
                log.info("retention_logs_cleanup.complete", deleted_count=deleted_count)
                
                return {
                    "status": "success",
                    "deleted_count": deleted_count,
                    "cutoff_date": cutoff_date.isoformat(),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            log.error("retention_logs_cleanup.failed", error=str(e))
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return asyncio.run(_cleanup())


# Celery beat schedule configuration
# Add this to your celery configuration:
RETENTION_SCHEDULE = {
    'run-retention-policy': {
        'task': 'app.tasks.retention_tasks.run_retention_policy',
        'schedule': 24 * 60 * 60,  # Run daily at midnight
        'options': {'expires': 3600}  # Task expires after 1 hour
    },
    'cleanup-retention-logs': {
        'task': 'app.tasks.retention_tasks.cleanup_old_retention_logs',
        'schedule': 7 * 24 * 60 * 60,  # Run weekly
        'options': {'expires': 3600}
    }
}
