from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infra.persistence.database import async_session
from infra.persistence.models import UserModel
from api.schemas.auth_schema import UserCreate, UserLogin, Token
from api.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/register", status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    new_user = UserModel(email=user.email, hashed_password=get_password_hash(user.password))
    db.add(new_user)
    await db.commit()
    return {"mensaje": "Usuario registrado exitosamente"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.email == user.email))
    db_user = result.scalar_one_or_none()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
