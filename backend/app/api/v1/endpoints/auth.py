from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ....core.database import get_async_session
from ....core.security import hash_password, verify_password, create_access_token
from ....models import User, UserRole
from ....schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        select(User).where(
            (User.username == data.username) | (User.email == data.username) | (User.phone == data.username)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    if role := data.role:
        if user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role mismatch")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        role=user.role,
        full_name=f"{user.first_name} {user.surname}",
        whatsapp_number=user.whatsapp_number,
        whatsapp_optin=user.whatsapp_optin or False,
    )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_async_session)):
    existing = await db.execute(
        select(User).where((User.username == data.username) | (User.email == data.email))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=data.username,
        email=data.email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        surname=data.surname,
        first_name=data.first_name,
        role=data.role,
        designation=data.designation,
        license_number=data.license_number,
        department=data.department,
        facility=data.facility,
        district=data.district,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
