from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint, func

from app.db.engine import Base


class SyncItem(Base):
    __tablename__ = "sync_items"

    id = Column(Integer, primary_key=True, autoincrement=True)

    profile = Column(String, nullable=False, index=True)
    source_key = Column(String, nullable=False)
    sync_id = Column(String, nullable=False, index=True)

    status = Column(String, nullable=False)
    title = Column(String, nullable=True)
    platform = Column(String, nullable=True)
    video_id = Column(String, nullable=True)
    created_at_ms = Column(Integer, nullable=True)

    local_task_id = Column(String, nullable=True)
    local_has_note = Column(Boolean, nullable=True)
    local_has_transcript = Column(Boolean, nullable=True)

    dify_note_document_id = Column(String, nullable=True)
    dify_note_name = Column(String, nullable=True)
    dify_transcript_document_id = Column(String, nullable=True)
    dify_transcript_name = Column(String, nullable=True)
    remote_has_note = Column(Boolean, nullable=True)
    remote_has_transcript = Column(Boolean, nullable=True)

    minio_bundle_exists = Column(Boolean, nullable=True)
    minio_tombstone_exists = Column(Boolean, nullable=True)
    bundle_sha256_local = Column(String, nullable=True)
    bundle_sha256_remote = Column(String, nullable=True)
    note_sha256_local = Column(String, nullable=True)
    note_sha256_remote = Column(String, nullable=True)
    transcript_sha256_local = Column(String, nullable=True)
    transcript_sha256_remote = Column(String, nullable=True)

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("profile", "source_key", name="uq_sync_items_profile_source"),)

