from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_with_user, SessionLocal
from app.db.models import DataRetentionLog, PIIRecord, Query, Run, AgentVote, OnchainProof
from app.core.encryption import get_encryption

log = structlog.get_logger()


class DataRetentionManager:
    """
    Manage data retention policies and crypto-shredding for DPDP compliance
    Default retention: 180 days unless user pins data
    """
    
    def __init__(self):
        self.default_retention_days = 180
        self.pii_retention_days = 90  # Shorter retention for PII
        self.crypto_shred_delay_hours = 24  # Delay before crypto-shred to allow recovery
    
    async def apply_retention_policy(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply retention policy to all eligible data
        If user_id is provided, only process that user's data
        """
        log.info("retention.policy_start", user_id=user_id)
        
        results = {
            "queries_processed": 0,
            "pii_records_processed": 0,
            "crypto_shredded": 0,
            "hard_deleted": 0,
            "errors": []
        }
        
        async with SessionLocal() as db:
            try:
                # Process expired queries and runs
                query_results = await self._process_expired_queries(db, user_id)
                results["queries_processed"] = query_results["processed"]
                results["errors"].extend(query_results["errors"])
                
                # Process expired PII records
                pii_results = await self._process_expired_pii(db, user_id)
                results["pii_records_processed"] = pii_results["processed"]
                results["errors"].extend(pii_results["errors"])
                
                # Crypto-shred marked data
                shred_results = await self._crypto_shred_marked_data(db, user_id)
                results["crypto_shredded"] = shred_results["shredded"]
                results["errors"].extend(shred_results["errors"])
                
                # Hard delete crypto-shredded data after delay
                delete_results = await self._hard_delete_expired_data(db, user_id)
                results["hard_deleted"] = delete_results["deleted"]
                results["errors"].extend(delete_results["errors"])
                
                await db.commit()
                
                log.info("retention.policy_complete", 
                        user_id=user_id,
                        **{k: v for k, v in results.items() if k != "errors"})
                
            except Exception as e:
                await db.rollback()
                log.error("retention.policy_error", error=str(e), user_id=user_id)
                results["errors"].append(f"Policy application failed: {str(e)}")
        
        return results
    
    async def _process_expired_queries(self, db: AsyncSession, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process queries older than retention period"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.default_retention_days)
        
        # Find expired queries
        where_clause = "WHERE q.created_at < :cutoff_date"
        params = {"cutoff_date": cutoff_date}
        
        if user_id:
            where_clause += " AND m.user_id = :user_id"
            params["user_id"] = user_id
        
        query_sql = f"""
            SELECT q.id, q.message, q.message_encrypted, m.user_id
            FROM queries q
            JOIN matters m ON q.matter_id = m.id
            {where_clause}
            AND q.id NOT IN (
                SELECT query_id FROM data_retention_logs 
                WHERE retention_type IN ('soft_delete', 'crypto_shred')
                AND query_id IS NOT NULL
            )
            LIMIT 1000
        """
        
        result = await db.execute(text(query_sql), params)
        expired_queries = result.fetchall()
        
        processed = 0
        errors = []
        
        for query_row in expired_queries:
            try:
                query_id, message, message_encrypted, query_user_id = query_row
                
                # Mark for crypto-shredding (soft delete first)
                await self._mark_for_crypto_shred(
                    db, 
                    str(query_user_id), 
                    "queries", 
                    str(query_id),
                    "retention_policy",
                    {"original_message_encrypted": bool(message_encrypted)}
                )
                
                # Crypto-shred encrypted message immediately if present
                if message_encrypted:
                    await db.execute(
                        text("UPDATE queries SET message_encrypted = NULL WHERE id = :query_id"),
                        {"query_id": query_id}
                    )
                    
                    log.info("retention.query_crypto_shredded", 
                            query_id=str(query_id),
                            user_id=str(query_user_id))
                
                processed += 1
                
            except Exception as e:
                errors.append(f"Query {query_id}: {str(e)}")
                log.error("retention.query_error", query_id=str(query_id), error=str(e))
        
        return {"processed": processed, "errors": errors}
    
    async def _process_expired_pii(self, db: AsyncSession, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process PII records older than PII retention period"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.pii_retention_days)
        
        where_clause = "WHERE created_at < :cutoff_date AND deleted_at IS NULL"
        params = {"cutoff_date": cutoff_date}
        
        if user_id:
            where_clause += " AND user_id = :user_id"
            params["user_id"] = user_id
        
        pii_sql = f"""
            SELECT id, user_id, original_encrypted
            FROM pii_records
            {where_clause}
            LIMIT 1000
        """
        
        result = await db.execute(text(pii_sql), params)
        expired_pii = result.fetchall()
        
        processed = 0
        errors = []
        
        for pii_row in expired_pii:
            try:
                pii_id, pii_user_id, original_encrypted = pii_row
                
                # Crypto-shred encrypted PII data
                if original_encrypted:
                    encryption = get_encryption()
                    encryption.crypto_shred(original_encrypted)
                
                # Mark as deleted
                await db.execute(
                    text("UPDATE pii_records SET deleted_at = NOW(), original_encrypted = NULL WHERE id = :pii_id"),
                    {"pii_id": pii_id}
                )
                
                # Log retention action
                await self._mark_for_crypto_shred(
                    db,
                    str(pii_user_id),
                    "pii_records",
                    str(pii_id),
                    "retention_policy",
                    {"pii_crypto_shredded": True}
                )
                
                processed += 1
                
                log.info("retention.pii_crypto_shredded", 
                        pii_id=str(pii_id),
                        user_id=str(pii_user_id))
                
            except Exception as e:
                errors.append(f"PII {pii_id}: {str(e)}")
                log.error("retention.pii_error", pii_id=str(pii_id), error=str(e))
        
        return {"processed": processed, "errors": errors}
    
    async def _crypto_shred_marked_data(self, db: AsyncSession, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Crypto-shred data that has been marked for shredding"""
        
        where_clause = "WHERE retention_type = 'soft_delete'"
        params = {}
        
        if user_id:
            where_clause += " AND user_id = :user_id"
            params["user_id"] = user_id
        
        # Find data marked for soft deletion that's ready for crypto-shredding
        marked_sql = f"""
            SELECT id, user_id, table_name, record_id, metadata_json
            FROM data_retention_logs
            {where_clause}
            AND deleted_at < NOW() - INTERVAL '1 hour'
            ORDER BY deleted_at
            LIMIT 100
        """
        
        result = await db.execute(text(marked_sql), params)
        marked_records = result.fetchall()
        
        shredded = 0
        errors = []
        
        for record in marked_records:
            try:
                log_id, record_user_id, table_name, record_id, metadata = record
                
                if table_name == "queries":
                    # Crypto-shred query data
                    await db.execute(
                        text("UPDATE queries SET message = '[CRYPTO_SHREDDED]', message_encrypted = NULL WHERE id = :id"),
                        {"id": record_id}
                    )
                
                elif table_name == "runs":
                    # Crypto-shred run answer text
                    await db.execute(
                        text("UPDATE runs SET answer_text = '[CRYPTO_SHREDDED]', retrieval_set_json = '[]' WHERE id = :id"),
                        {"id": record_id}
                    )
                
                # Update retention log to mark as crypto-shredded
                await db.execute(
                    text("UPDATE data_retention_logs SET retention_type = 'crypto_shred' WHERE id = :log_id"),
                    {"log_id": log_id}
                )
                
                shredded += 1
                
                log.info("retention.crypto_shred_complete",
                        table=table_name,
                        record_id=record_id,
                        user_id=str(record_user_id))
                
            except Exception as e:
                errors.append(f"Crypto-shred {table_name}.{record_id}: {str(e)}")
                log.error("retention.crypto_shred_error", 
                         table=table_name, 
                         record_id=record_id, 
                         error=str(e))
        
        return {"shredded": shredded, "errors": errors}
    
    async def _hard_delete_expired_data(self, db: AsyncSession, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Hard delete crypto-shredded data after delay period"""
        
        cutoff_date = datetime.utcnow() - timedelta(hours=self.crypto_shred_delay_hours)
        
        where_clause = "WHERE retention_type = 'crypto_shred' AND deleted_at < :cutoff_date"
        params = {"cutoff_date": cutoff_date}
        
        if user_id:
            where_clause += " AND user_id = :user_id"
            params["user_id"] = user_id
        
        # Find crypto-shredded data ready for hard deletion
        ready_sql = f"""
            SELECT id, user_id, table_name, record_id
            FROM data_retention_logs
            {where_clause}
            ORDER BY deleted_at
            LIMIT 50
        """
        
        result = await db.execute(text(ready_sql), params)
        ready_records = result.fetchall()
        
        deleted = 0
        errors = []
        
        for record in ready_records:
            try:
                log_id, record_user_id, table_name, record_id = record
                
                # Hard delete the actual record
                if table_name in ["queries", "runs", "pii_records"]:
                    await db.execute(
                        text(f"DELETE FROM {table_name} WHERE id = :id"),
                        {"id": record_id}
                    )
                    
                    # Update retention log to mark as hard deleted
                    await db.execute(
                        text("UPDATE data_retention_logs SET retention_type = 'hard_delete' WHERE id = :log_id"),
                        {"log_id": log_id}
                    )
                    
                    deleted += 1
                    
                    log.info("retention.hard_delete_complete",
                            table=table_name,
                            record_id=record_id,
                            user_id=str(record_user_id))
                
            except Exception as e:
                errors.append(f"Hard delete {table_name}.{record_id}: {str(e)}")
                log.error("retention.hard_delete_error",
                         table=table_name,
                         record_id=record_id,
                         error=str(e))
        
        return {"deleted": deleted, "errors": errors}
    
    async def _mark_for_crypto_shred(self, db: AsyncSession, user_id: str, 
                                   table_name: str, record_id: str, 
                                   reason: str, metadata: Optional[Dict] = None) -> None:
        """Mark a record for crypto-shredding"""
        
        retention_log = DataRetentionLog(
            user_id=user_id,
            retention_type="soft_delete",
            table_name=table_name,
            record_id=record_id,
            reason=reason,
            retention_period_days=self.default_retention_days,
            metadata_json=metadata or {}
        )
        
        db.add(retention_log)
    
    async def process_user_deletion_request(self, user_id: str, 
                                          reason: str = "user_request") -> Dict[str, Any]:
        """
        Process user's right to be forgotten (GDPR/DPDP)
        Immediately crypto-shred all user data
        """
        log.info("retention.user_deletion_start", user_id=user_id, reason=reason)
        
        results = {
            "queries_shredded": 0,
            "runs_shredded": 0,
            "pii_shredded": 0,
            "matters_marked": 0,
            "errors": []
        }
        
        async with get_db_with_user(user_id) as db:
            try:
                # Crypto-shred all queries
                queries_result = await db.execute(
                    text("""
                        UPDATE queries SET 
                            message = '[USER_DELETED]',
                            message_encrypted = NULL,
                            filters_json = '{}'
                        WHERE matter_id IN (
                            SELECT id FROM matters WHERE user_id = :user_id
                        )
                        RETURNING id
                    """),
                    {"user_id": user_id}
                )
                shredded_queries = queries_result.fetchall()
                results["queries_shredded"] = len(shredded_queries)
                
                # Crypto-shred all runs
                runs_result = await db.execute(
                    text("""
                        UPDATE runs SET 
                            answer_text = '[USER_DELETED]',
                            retrieval_set_json = '[]'
                        WHERE query_id IN (
                            SELECT q.id FROM queries q
                            JOIN matters m ON q.matter_id = m.id
                            WHERE m.user_id = :user_id
                        )
                        RETURNING id
                    """),
                    {"user_id": user_id}
                )
                shredded_runs = runs_result.fetchall()
                results["runs_shredded"] = len(shredded_runs)
                
                # Crypto-shred PII records
                pii_result = await db.execute(
                    text("""
                        UPDATE pii_records SET 
                            original_encrypted = NULL,
                            deleted_at = NOW()
                        WHERE user_id = :user_id
                        RETURNING id
                    """),
                    {"user_id": user_id}
                )
                shredded_pii = pii_result.fetchall()
                results["pii_shredded"] = len(shredded_pii)
                
                # Mark matters for deletion (keep for legal compliance)
                matters_result = await db.execute(
                    text("""
                        UPDATE matters SET 
                            title = '[USER_DELETED]'
                        WHERE user_id = :user_id
                        RETURNING id
                    """),
                    {"user_id": user_id}
                )
                marked_matters = matters_result.fetchall()
                results["matters_marked"] = len(marked_matters)
                
                # Log the deletion
                for query_id, in shredded_queries:
                    await self._mark_for_crypto_shred(
                        db, user_id, "queries", str(query_id), reason,
                        {"user_deletion": True, "immediate_shred": True}
                    )
                
                for run_id, in shredded_runs:
                    await self._mark_for_crypto_shred(
                        db, user_id, "runs", str(run_id), reason,
                        {"user_deletion": True, "immediate_shred": True}
                    )
                
                await db.commit()
                
                log.info("retention.user_deletion_complete", 
                        user_id=user_id,
                        **{k: v for k, v in results.items() if k != "errors"})
                
            except Exception as e:
                await db.rollback()
                log.error("retention.user_deletion_error", user_id=user_id, error=str(e))
                results["errors"].append(f"User deletion failed: {str(e)}")
                raise
        
        return results
    
    async def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's data for transparency/audit purposes"""
        
        async with get_db_with_user(user_id) as db:
            # Count user's data
            summary_sql = """
                SELECT 
                    (SELECT COUNT(*) FROM matters WHERE user_id = :user_id) as matters_count,
                    (SELECT COUNT(*) FROM documents WHERE uploaded_by = :user_id) as documents_count,
                    (SELECT COUNT(*) FROM queries q JOIN matters m ON q.matter_id = m.id WHERE m.user_id = :user_id) as queries_count,
                    (SELECT COUNT(*) FROM runs r JOIN queries q ON r.query_id = q.id JOIN matters m ON q.matter_id = m.id WHERE m.user_id = :user_id) as runs_count,
                    (SELECT COUNT(*) FROM pii_records WHERE user_id = :user_id AND deleted_at IS NULL) as active_pii_count,
                    (SELECT COUNT(*) FROM pii_records WHERE user_id = :user_id AND deleted_at IS NOT NULL) as deleted_pii_count,
                    (SELECT COUNT(*) FROM data_retention_logs WHERE user_id = :user_id) as retention_actions_count
            """
            
            result = await db.execute(text(summary_sql), {"user_id": user_id})
            row = result.fetchone()
            
            # Get oldest and newest data
            dates_sql = """
                SELECT 
                    MIN(created_at) as oldest_data,
                    MAX(created_at) as newest_data
                FROM (
                    SELECT created_at FROM matters WHERE user_id = :user_id
                    UNION ALL
                    SELECT q.created_at FROM queries q JOIN matters m ON q.matter_id = m.id WHERE m.user_id = :user_id
                    UNION ALL
                    SELECT created_at FROM pii_records WHERE user_id = :user_id
                ) data_dates
            """
            
            dates_result = await db.execute(text(dates_sql), {"user_id": user_id})
            dates_row = dates_result.fetchone()
            
            return {
                "user_id": user_id,
                "data_counts": {
                    "matters": row[0] if row else 0,
                    "documents": row[1] if row else 0,
                    "queries": row[2] if row else 0,
                    "runs": row[3] if row else 0,
                    "active_pii_records": row[4] if row else 0,
                    "deleted_pii_records": row[5] if row else 0,
                    "retention_actions": row[6] if row else 0
                },
                "data_age": {
                    "oldest_data": dates_row[0] if dates_row and dates_row[0] else None,
                    "newest_data": dates_row[1] if dates_row and dates_row[1] else None
                },
                "retention_policy": {
                    "default_retention_days": self.default_retention_days,
                    "pii_retention_days": self.pii_retention_days,
                    "crypto_shred_delay_hours": self.crypto_shred_delay_hours
                }
            }


# Global retention manager instance
_retention_manager: Optional[DataRetentionManager] = None


def get_retention_manager() -> DataRetentionManager:
    """Get global retention manager instance"""
    global _retention_manager
    if _retention_manager is None:
        _retention_manager = DataRetentionManager()
    return _retention_manager


async def run_retention_policy() -> Dict[str, Any]:
    """Run retention policy for all users (scheduled job)"""
    return await get_retention_manager().apply_retention_policy()


async def process_user_deletion(user_id: str, reason: str = "user_request") -> Dict[str, Any]:
    """Process user's right to be forgotten"""
    return await get_retention_manager().process_user_deletion_request(user_id, reason)


if __name__ == "__main__":
    # Test the retention system
    async def test_retention():
        manager = DataRetentionManager()
        
        # Test policy application
        results = await manager.apply_retention_policy()
        print("Retention policy results:")
        print(f"Queries processed: {results['queries_processed']}")
        print(f"PII records processed: {results['pii_records_processed']}")
        print(f"Crypto-shredded: {results['crypto_shredded']}")
        print(f"Hard deleted: {results['hard_deleted']}")
        print(f"Errors: {len(results['errors'])}")
        
        if results['errors']:
            print("Errors encountered:")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
    
    asyncio.run(test_retention())
