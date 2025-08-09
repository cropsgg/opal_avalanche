from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, CheckConstraint, Date, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="lawyer")
    wallet_address: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    matters: Mapped[list["Matter"]] = relationship("Matter", back_populates="user")
    user_firms: Mapped[list["UserFirm"]] = relationship("UserFirm", back_populates="user")
    billing_account: Mapped[Optional["BillingAccount"]] = relationship("BillingAccount", back_populates="user", uselist=False)
    
    __table_args__ = (
        CheckConstraint("role in ('lawyer', 'admin', 'paralegal', 'client')", name="users_role_chk"),
    )


class Firm(Base):
    __tablename__ = "firms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    gstin: Mapped[Optional[str]] = mapped_column(String)  # GST Identification Number for Indian firms
    pan: Mapped[Optional[str]] = mapped_column(String)  # PAN for Indian firms
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String)
    state: Mapped[Optional[str]] = mapped_column(String)
    pincode: Mapped[Optional[str]] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_firms: Mapped[list["UserFirm"]] = relationship("UserFirm", back_populates="firm")


class UserFirm(Base):
    __tablename__ = "user_firms"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    firm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("firms.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String, default="member")
    joined_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_firms")
    firm: Mapped["Firm"] = relationship("Firm", back_populates="user_firms")
    
    __table_args__ = (
        CheckConstraint("role in ('owner', 'partner', 'associate', 'member', 'intern')", name="user_firms_role_chk"),
    )


class Authority(Base):
    __tablename__ = "authorities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    court: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    neutral_cite: Mapped[Optional[str]] = mapped_column(String)
    reporter_cite: Mapped[Optional[str]] = mapped_column(String)
    date: Mapped[Optional[datetime]] = mapped_column(Date)
    bench: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    hash_keccak256: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    chunks: Mapped[list["Chunk"]] = relationship("Chunk", back_populates="authority")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    authority_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("authorities.id", ondelete="CASCADE"))
    para_from: Mapped[Optional[int]] = mapped_column(Integer)
    para_to: Mapped[Optional[int]] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    tokens: Mapped[Optional[int]] = mapped_column(Integer)
    vector_id: Mapped[Optional[str]] = mapped_column(String)
    statute_tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    has_citation: Mapped[bool] = mapped_column(Boolean, default=False)

    authority: Mapped[Optional[Authority]] = relationship("Authority", back_populates="chunks")

    __table_args__ = (
        Index("idx_chunks_authority", "authority_id"),
        Index("idx_chunks_statutes", "statute_tags", postgresql_using="gin"),
    )


class Matter(Base):
    __tablename__ = "matters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String, default="en")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="matters")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"))
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    filetype: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[Optional[int]] = mapped_column(BigInteger)
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    ocr_status: Mapped[str] = mapped_column(String, default="pending")
    checksum_sha256: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class Query(Base):
    __tablename__ = "queries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"))
    message_encrypted: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Encrypted user input
    message: Mapped[str] = mapped_column(Text, nullable=False)  # For backward compatibility, will be deprecated
    mode: Mapped[str] = mapped_column(String, nullable=False)
    filters_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("mode in ('general','precedent','limitation','draft')", name="queries_mode_chk"),
    )

    @hybrid_property
    def decrypted_message(self) -> str:
        """Get decrypted message content"""
        if self.message_encrypted:
            from app.core.encryption import decrypt_user_input
            try:
                return decrypt_user_input(self.message_encrypted)
            except Exception:
                # Fallback to unencrypted message for migration period
                return self.message
        return self.message

    def encrypt_message(self, plaintext: str, user_id: str) -> None:
        """Encrypt and store message"""
        from app.core.encryption import encrypt_user_input
        self.message_encrypted = encrypt_user_input(plaintext, user_id)
        # Keep unencrypted for migration period
        self.message = plaintext


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"))
    answer_text: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric)
    retrieval_set_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class AgentVote(Base):
    __tablename__ = "agent_votes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"))
    agent: Mapped[str] = mapped_column(String, nullable=False)
    decision_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric, nullable=False)
    aligned: Mapped[Optional[bool]] = mapped_column(Boolean)
    weights_before: Mapped[Optional[dict]] = mapped_column(JSON)
    weights_after: Mapped[Optional[dict]] = mapped_column(JSON)


class OnchainProof(Base):
    __tablename__ = "onchain_proofs"

    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), primary_key=True)
    merkle_root: Mapped[str] = mapped_column(String, nullable=False)
    tx_hash: Mapped[str] = mapped_column(String, nullable=False)
    network: Mapped[str] = mapped_column(String, nullable=False)
    block_number: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class BillingAccount(Base):
    __tablename__ = "billing_accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    plan: Mapped[str] = mapped_column(String, default="starter")
    credits_balance: Mapped[int] = mapped_column(Integer, default=0)
    renews_at: Mapped[Optional[datetime]] = mapped_column(Date)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="billing_account")


class BillingLedger(Base):
    __tablename__ = "billing_ledger"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    run_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    credits_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd: Mapped[Optional[float]] = mapped_column(Numeric)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class PIIRecord(Base):
    """Track PII detected and redacted in user inputs"""
    __tablename__ = "pii_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    query_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"))
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    pii_type: Mapped[str] = mapped_column(String, nullable=False)  # 'aadhaar', 'pan', 'email', etc.
    detection_confidence: Mapped[float] = mapped_column(Numeric, default=1.0)
    redacted_count: Mapped[int] = mapped_column(Integer, default=1)
    original_encrypted: Mapped[Optional[dict]] = mapped_column(JSON)  # Encrypted original PII for audit
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))  # For retention policy

    @hybrid_property
    def original_value(self) -> Optional[str]:
        """Get decrypted original PII value (audit use only)"""
        if self.original_encrypted:
            from app.core.encryption import decrypt_user_input
            try:
                return decrypt_user_input(self.original_encrypted)
            except Exception:
                return None
        return None

    def encrypt_original(self, original_value: str, user_id: str) -> None:
        """Encrypt and store original PII value for audit"""
        from app.core.encryption import encrypt_user_input
        self.original_encrypted = encrypt_user_input(original_value, f"pii:{user_id}")


class DataRetentionLog(Base):
    """Track data retention and deletion activities"""
    __tablename__ = "data_retention_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    retention_type: Mapped[str] = mapped_column(String, nullable=False)  # 'soft_delete', 'hard_delete', 'crypto_shred'
    table_name: Mapped[str] = mapped_column(String, nullable=False)
    record_id: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)  # 'retention_policy', 'user_request', 'compliance'
    retention_period_days: Mapped[Optional[int]] = mapped_column(Integer)
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


