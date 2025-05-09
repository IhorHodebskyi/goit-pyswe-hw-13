from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contact import ContactResponse, ContactShema
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10), offset: int = Query(0, ge=0), query: str | None = Query(None),
                       db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(limit=limit, offset=offset, query=query, db=db, user=current_user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_user(contact_id: int, db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact_by_id(contact_id=contact_id, db=db, user=current_user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse)
async def create_contact(contact: ContactShema, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    user = await repository_contacts.create_contact(contact=contact, db=db, user=current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contact with this email or phone already exists")
    return user


@router.put("/{contact_id}", response_model=ContactResponse, status_code=status.HTTP_202_ACCEPTED)
async def update_contact(contact_id: int, contact: ContactShema, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    user = await repository_contacts.update_contact(contact_id=contact_id, contact=contact, db=db, user=current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return user


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    user = await repository_contacts.delete_contact(contact_id=contact_id, db=db, user=current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Contact deleted")
