import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.membership import Membership, MembershipRole
from app.models.organization import Organization
from app.models.user import User


async def test_create_org_user_membership(db_session):
    org = Organization(name="Acme Inc")
    user = User(email="owner@acme.test", hashed_password="hashed", auth_provider="password")
    db_session.add_all([org, user])
    await db_session.flush()

    membership = Membership(user_id=user.id, org_id=org.id, role=MembershipRole.owner)
    db_session.add(membership)
    await db_session.commit()

    result = await db_session.execute(select(Membership).where(Membership.org_id == org.id))
    fetched = result.scalar_one()
    assert fetched.role == MembershipRole.owner
    assert fetched.user_id == user.id


async def test_membership_unique_user_org(db_session):
    org = Organization(name="Acme Inc")
    user = User(email="dup@acme.test", hashed_password="hashed", auth_provider="password")
    db_session.add_all([org, user])
    await db_session.flush()

    db_session.add(Membership(user_id=user.id, org_id=org.id, role=MembershipRole.owner))
    await db_session.commit()

    db_session.add(Membership(user_id=user.id, org_id=org.id, role=MembershipRole.admin))
    with pytest.raises(IntegrityError):
        await db_session.commit()
