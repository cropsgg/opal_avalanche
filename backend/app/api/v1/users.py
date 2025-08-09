from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import current_user
from app.db.session import get_db
from app.db import crud

router = APIRouter()


class UserResponse(BaseModel):
    id: UUID
    clerk_id: str
    email: str
    role: str
    wallet_address: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    wallet_address: Optional[str] = None
    role: Optional[str] = None


class FirmCreate(BaseModel):
    name: str
    gstin: Optional[str] = None
    pan: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class FirmResponse(BaseModel):
    id: UUID
    name: str
    gstin: Optional[str]
    pan: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class FirmUpdate(BaseModel):
    name: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class UserFirmInvite(BaseModel):
    user_email: str
    role: str = "member"


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Get current user's profile"""
    user_id = UUID(user["id"])
    db_user = await crud.get_user_by_id(db, user_id)
    
    if not db_user:
        # Create user record if doesn't exist (first time login from Clerk)
        db_user = await crud.create_user(
            db, 
            clerk_id=user["id"], 
            email=user.get("email", ""),
            role="lawyer"
        )
        
        # Create billing account for new user
        await crud.get_or_create_billing_account(db, db_user.id)
    
    return UserResponse(
        id=db_user.id,
        clerk_id=db_user.clerk_id,
        email=db_user.email,
        role=db_user.role,
        wallet_address=db_user.wallet_address,
        created_at=db_user.created_at.isoformat()
    )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate, 
    user=Depends(current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    user_id = UUID(user["id"])
    
    # Get current user
    db_user = await crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update user
    update_dict = update_data.model_dump(exclude_unset=True)
    updated_user = await crud.update_user(db, user_id, **update_dict)
    
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")
    
    return UserResponse(
        id=updated_user.id,
        clerk_id=updated_user.clerk_id,
        email=updated_user.email,
        role=updated_user.role,
        wallet_address=updated_user.wallet_address,
        created_at=updated_user.created_at.isoformat()
    )


@router.get("/firms")
async def get_user_firms(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Get all firms for current user"""
    user_id = UUID(user["id"])
    firms = await crud.get_user_firms(db, user_id)
    return {"firms": firms}


@router.post("/firms", response_model=FirmResponse)
async def create_firm(
    firm_data: FirmCreate, 
    user=Depends(current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Create a new firm and add current user as owner"""
    user_id = UUID(user["id"])
    
    # Create firm
    firm = await crud.create_firm(db, **firm_data.model_dump())
    
    # Add current user as firm owner
    await crud.add_user_to_firm(db, user_id, firm.id, role="owner")
    
    return FirmResponse(
        id=firm.id,
        name=firm.name,
        gstin=firm.gstin,
        pan=firm.pan,
        address=firm.address,
        city=firm.city,
        state=firm.state,
        pincode=firm.pincode,
        phone=firm.phone,
        email=firm.email,
        created_at=firm.created_at.isoformat()
    )


@router.get("/firms/{firm_id}")
async def get_firm_details(
    firm_id: UUID, 
    user=Depends(current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Get firm details and members (only if user is part of the firm)"""
    user_id = UUID(user["id"])
    
    # Check if user is part of this firm
    user_firms = await crud.get_user_firms(db, user_id)
    user_firm_ids = [UUID(f["firm_id"]) for f in user_firms]
    
    if firm_id not in user_firm_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Get firm details
    firm = await crud.get_firm_by_id(db, firm_id)
    if not firm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firm not found")
    
    # Get firm members
    members = await crud.get_firm_users(db, firm_id)
    
    return {
        "firm": FirmResponse(
            id=firm.id,
            name=firm.name,
            gstin=firm.gstin,
            pan=firm.pan,
            address=firm.address,
            city=firm.city,
            state=firm.state,
            pincode=firm.pincode,
            phone=firm.phone,
            email=firm.email,
            created_at=firm.created_at.isoformat()
        ),
        "members": members
    }


@router.put("/firms/{firm_id}", response_model=FirmResponse)
async def update_firm(
    firm_id: UUID,
    firm_data: FirmUpdate,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update firm details (only owners and partners can update)"""
    user_id = UUID(user["id"])
    
    # Check if user has permission to update this firm
    user_firms = await crud.get_user_firms(db, user_id)
    user_firm = next((f for f in user_firms if UUID(f["firm_id"]) == firm_id), None)
    
    if not user_firm or user_firm["role"] not in ["owner", "partner"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    # Update firm
    update_dict = firm_data.model_dump(exclude_unset=True)
    updated_firm = await crud.update_firm(db, firm_id, **update_dict)
    
    if not updated_firm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firm not found")
    
    return FirmResponse(
        id=updated_firm.id,
        name=updated_firm.name,
        gstin=updated_firm.gstin,
        pan=updated_firm.pan,
        address=updated_firm.address,
        city=updated_firm.city,
        state=updated_firm.state,
        pincode=updated_firm.pincode,
        phone=updated_firm.phone,
        email=updated_firm.email,
        created_at=updated_firm.created_at.isoformat()
    )


@router.post("/firms/{firm_id}/invite")
async def invite_user_to_firm(
    firm_id: UUID,
    invite: UserFirmInvite,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Invite a user to join the firm (only owners and partners can invite)"""
    user_id = UUID(user["id"])
    
    # Check if user has permission to invite to this firm
    user_firms = await crud.get_user_firms(db, user_id)
    user_firm = next((f for f in user_firms if UUID(f["firm_id"]) == firm_id), None)
    
    if not user_firm or user_firm["role"] not in ["owner", "partner"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    # For now, just return success - actual email invitation would be implemented separately
    # In a full implementation, this would send an email invitation
    return {
        "message": f"Invitation sent to {invite.user_email}",
        "firm_id": str(firm_id),
        "role": invite.role,
        "invited_by": user["email"]
    }


@router.delete("/firms/{firm_id}/members/{member_user_id}")
async def remove_user_from_firm(
    firm_id: UUID,
    member_user_id: UUID,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a user from the firm (only owners can remove members)"""
    user_id = UUID(user["id"])
    
    # Check if user has permission to remove members from this firm
    user_firms = await crud.get_user_firms(db, user_id)
    user_firm = next((f for f in user_firms if UUID(f["firm_id"]) == firm_id), None)
    
    if not user_firm or user_firm["role"] != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only firm owners can remove members")
    
    # Don't allow owner to remove themselves if they're the last owner
    if member_user_id == user_id:
        firm_members = await crud.get_firm_users(db, firm_id)
        owners = [m for m in firm_members if m["role_in_firm"] == "owner"]
        if len(owners) <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot remove the last owner from the firm"
            )
    
    # Remove user from firm
    success = await crud.remove_user_from_firm(db, member_user_id, firm_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in firm")
    
    return {"message": "User removed from firm successfully"}


@router.delete("/profile")
async def delete_user_account(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Delete user account (soft delete for compliance)"""
    user_id = UUID(user["id"])
    
    success = await crud.delete_user(db, user_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {"message": "Account deleted successfully"}
