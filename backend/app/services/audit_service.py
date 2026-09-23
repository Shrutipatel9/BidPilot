import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_action(
    db: AsyncSession,
    org_id: uuid.UUID | None,
    actor_id: uuid.UUID | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
) -> None:
    db.add(
        AuditLog(
            org_id=org_id,
            actor_user_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
        )
    )
    # Deliberately no commit() here — callers add this to the same transaction as the action
    # being logged, so the audit entry and the action it describes succeed or fail together.
