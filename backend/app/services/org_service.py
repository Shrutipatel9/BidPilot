import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership, MembershipRole
from app.models.organization import Organization
from app.services.audit_service import log_action


async def create_organization(db: AsyncSession, owner_id: uuid.UUID, name: str) -> Organization:
    org = Organization(name=name)
    db.add(org)
    await db.flush()

    db.add(Membership(user_id=owner_id, org_id=org.id, role=MembershipRole.owner))
    await log_action(db, org.id, owner_id, "organization.created", "organization", str(org.id))
    await db.commit()
    await db.refresh(org)
    return org


async def list_my_organizations(db: AsyncSession, user_id: uuid.UUID) -> list[Organization]:
    result = await db.execute(
        select(Organization).join(Membership, Membership.org_id == Organization.id).where(Membership.user_id == user_id)
    )
    return list(result.scalars().all())


async def count_owners(db: AsyncSession, org_id: uuid.UUID) -> int:
    return await db.scalar(
        select(func.count()).select_from(Membership).where(
            Membership.org_id == org_id, Membership.role == MembershipRole.owner
        )
    )
