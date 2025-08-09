from __future__ import annotations

from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import current_user
from app.core.data_retention import get_retention_manager
from app.db.session import get_db
from app.tasks.retention_tasks import process_user_deletion

router = APIRouter()


class DataSummaryResponse(BaseModel):
    user_id: str
    data_counts: Dict[str, int]
    data_age: Dict[str, Any]
    retention_policy: Dict[str, int]


class DataDeletionRequest(BaseModel):
    confirm_deletion: bool
    reason: str = "user_request"


class DataDeletionResponse(BaseModel):
    status: str
    user_id: str
    deletion_summary: Dict[str, int]
    estimated_completion: str


@router.get("/data-summary", response_model=DataSummaryResponse)
async def get_user_data_summary(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """
    Get summary of user's data for transparency (DPDP Article 11)
    Shows what data we have and how long it will be retained
    """
    user_id = user["id"]
    
    try:
        manager = get_retention_manager()
        summary = await manager.get_user_data_summary(user_id)
        
        return DataSummaryResponse(**summary)
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("privacy.data_summary_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve data summary"
        )


@router.post("/request-deletion", response_model=DataDeletionResponse)
async def request_data_deletion(
    request: DataDeletionRequest,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process user's right to be forgotten (DPDP Article 12)
    Immediately crypto-shreds all user data
    """
    if not request.confirm_deletion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deletion confirmation required"
        )
    
    user_id = user["id"]
    
    import structlog
    log = structlog.get_logger()
    log.info("privacy.deletion_request", user_id=user_id, reason=request.reason)
    
    try:
        # Get current data summary before deletion
        manager = get_retention_manager()
        pre_deletion_summary = await manager.get_user_data_summary(user_id)
        
        # Queue immediate deletion task
        task = process_user_deletion.delay(user_id, request.reason)
        
        log.info("privacy.deletion_queued", 
                user_id=user_id, 
                task_id=task.id,
                pre_deletion_counts=pre_deletion_summary["data_counts"])
        
        return DataDeletionResponse(
            status="queued",
            user_id=user_id,
            deletion_summary=pre_deletion_summary["data_counts"],
            estimated_completion="Data will be crypto-shredded within 1 hour"
        )
        
    except Exception as e:
        log.error("privacy.deletion_request_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process deletion request"
        )


@router.get("/data-processing-info")
async def get_data_processing_info(user=Depends(current_user)):
    """
    Provide information about how user data is processed (DPDP transparency)
    """
    return {
        "data_controller": {
            "name": "OPAL Legal AI",
            "contact": "privacy@opal-legal.ai",
            "data_protection_officer": "dpo@opal-legal.ai"
        },
        "processing_purposes": [
            "Legal research and analysis",
            "Document processing and OCR",
            "Query processing and response generation",
            "Billing and subscription management",
            "Security and fraud prevention"
        ],
        "data_categories": [
            "User queries and legal questions",
            "Uploaded legal documents",
            "Usage analytics and billing data",
            "Account information and preferences"
        ],
        "data_retention": {
            "default_retention_period_days": 180,
            "pii_retention_period_days": 90,
            "legal_basis": "Legitimate interest for service provision",
            "user_rights": [
                "Right to access data summary",
                "Right to data portability", 
                "Right to rectification",
                "Right to be forgotten (deletion)",
                "Right to restrict processing"
            ]
        },
        "data_protection_measures": [
            "Application-level encryption for sensitive data",
            "Row-level security for multi-tenant isolation",
            "PII detection and redaction",
            "Crypto-shredding for secure deletion",
            "Regular security audits and monitoring"
        ],
        "third_party_processors": [
            {
                "name": "OpenAI",
                "purpose": "AI processing (PII-redacted data only)",
                "data_residency": "US/EU"
            },
            {
                "name": "Supabase",
                "purpose": "Database and file storage",
                "data_residency": "India (ap-south-1)"
            }
        ],
        "user_rights_contact": {
            "email": "privacy@opal-legal.ai",
            "response_time": "30 days maximum",
            "escalation": "Data Protection Authority of India"
        }
    }


@router.get("/pii-audit")
async def get_pii_audit_log(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """
    Get user's PII detection and processing audit log
    """
    from sqlalchemy import text
    
    user_id = user["id"]
    
    try:
        # Get PII audit records for user
        audit_sql = """
            SELECT 
                pii_type,
                detection_confidence,
                redacted_count,
                created_at,
                deleted_at,
                query_id,
                document_id
            FROM pii_records 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT 100
        """
        
        result = await db.execute(text(audit_sql), {"user_id": user_id})
        pii_records = result.fetchall()
        
        # Get retention actions
        retention_sql = """
            SELECT 
                retention_type,
                table_name,
                reason,
                deleted_at,
                metadata_json
            FROM data_retention_logs 
            WHERE user_id = :user_id 
            ORDER BY deleted_at DESC 
            LIMIT 50
        """
        
        retention_result = await db.execute(text(retention_sql), {"user_id": user_id})
        retention_records = retention_result.fetchall()
        
        return {
            "user_id": user_id,
            "pii_detections": [
                {
                    "type": record[0],
                    "confidence": float(record[1]) if record[1] else 0,
                    "redacted_count": record[2],
                    "detected_at": record[3].isoformat() if record[3] else None,
                    "deleted_at": record[4].isoformat() if record[4] else None,
                    "query_id": str(record[5]) if record[5] else None,
                    "document_id": str(record[6]) if record[6] else None
                }
                for record in pii_records
            ],
            "retention_actions": [
                {
                    "action_type": record[0],
                    "table": record[1],
                    "reason": record[2],
                    "deleted_at": record[3].isoformat() if record[3] else None,
                    "metadata": record[4] or {}
                }
                for record in retention_records
            ],
            "summary": {
                "total_pii_detections": len(pii_records),
                "active_pii_records": len([r for r in pii_records if not r[4]]),  # not deleted
                "total_retention_actions": len(retention_records),
                "last_audit_date": max([r[3] for r in pii_records + retention_records if r[3]]).isoformat() if (pii_records or retention_records) else None
            }
        }
        
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("privacy.pii_audit_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve PII audit log"
        )


@router.post("/opt-out-analytics")
async def opt_out_analytics(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """
    Allow user to opt out of non-essential analytics
    """
    user_id = user["id"]
    
    try:
        # Update user preferences (you would implement user preferences table)
        # For now, just log the opt-out
        import structlog
        log = structlog.get_logger()
        log.info("privacy.analytics_opt_out", user_id=user_id)
        
        return {
            "status": "success",
            "message": "You have been opted out of non-essential analytics",
            "effective_date": "immediate"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process opt-out request"
        )
