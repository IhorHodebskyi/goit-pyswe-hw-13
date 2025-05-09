from fastapi import Depends
from sqlalchemy import select, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db

from src.entity.models import Contact, User
from src.schemas.contact import ContactShema


async def get_contacts(limit: int, offset: int, query: str | None,
                       db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    if query:
        search = f"%{query.lower()}%"
        stmt = stmt.where(or_(
            Contact.name.ilike(search),
            Contact.email.ilike(search),
            Contact.phone.ilike(search),
            cast(Contact.birthday, String).like(search),
            Contact.additional_data.ilike(search)
        ))
    result = await db.execute(stmt)
    return result.scalars().unique().all()


async def get_contact_by_id(contact_id: int, user: User, db: AsyncSession = Depends(get_db)):
    stmt = select(Contact).filter_by(Contact.id == contact_id, user=user)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_contact(contact: ContactShema, user: User, db: AsyncSession = Depends(get_db)):
    stmt = select(Contact).where(or_(Contact.email == contact.email, Contact.phone == contact.phone))
    result = await db.execute(stmt)
    contact_in_db = result.scalars().unique().first()
    if contact_in_db:
        return None
    new_contact = Contact(**contact.model_dump(), user=user)
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


async def update_contact(contact_id: int, contact: ContactShema, user: User, db: AsyncSession = Depends(get_db)):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact_in_db = result.scalars().unique().first()
    if not contact_in_db:
        return None
    contact_in_db.name = contact.name
    contact_in_db.surname = contact.surname
    contact_in_db.email = contact.email
    contact_in_db.phone = contact.phone
    if contact.birthday:
        contact_in_db.birthday = contact.birthday
    if contact_in_db.birthday:
        contact_in_db.additional_data = contact.additional_data
    await db.commit()
    await db.refresh(contact_in_db)
    return contact_in_db


async def delete_contact(contact_id: int, user: User, db: AsyncSession = Depends(get_db)):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact_in_db = result.scalars().unique().first()
    if not contact_in_db:
        return None
    await db.delete(contact_in_db)
    await db.commit()
    return contact_in_db
