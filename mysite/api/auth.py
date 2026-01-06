from fastapi import HTTPException, Depends, APIRouter
from mysite.database.models import UserProfile, ChatGroup, GroupPeople, ChatMessage
from mysite.database.schema import (UserProfileCreateSchema, UserProfileLoginSchema,
                                UserProfileOutSchema)
from mysite.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from mysite.config import (ALGORITHM, SECRET_KEY,
                             ACCESS_TOKEN_LIFETIME,
                             REFRESH_TOKEN_LIFETIME)
from datetime import timedelta, datetime


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
auth_router = APIRouter(prefix='/auth', tags=['Auth'])


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_LIFETIME))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_LIFETIME))


@auth_router.post('/register/')
async def register(user: UserProfileCreateSchema, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    user_email = db.query(UserProfile).filter(UserProfile.email == user.email).first()

    if user_db:
        raise HTTPException(status_code=400, detail='username is already taken')
    elif user_email:
        raise HTTPException(status_code=400, detail='email is already taken')

    new_hash_pass = get_password_hash(user.password)
    new_user = UserProfile(
        username=user.username,
        email=user.email,
        password=new_hash_pass,
        user_status=user.user_status
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {'message': 'User registered successfully'}


@auth_router.post('/login')
async def login(form_data: UserProfileLoginSchema = Depends(),
                db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=404, detail='Invalid credentials')

    access_token = create_access_token({'sub': user.username})
    refresh_token = create_refresh_token({'sub': user.username})

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }


@auth_router.post('/logout')
async def logout(refresh_token: str, db: Session = Depends(get_db)):
    return {'message': 'Logged out successfully'}


@auth_router.post('/refresh')
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEYS, algorithms=[ALGORITHM])
        username = payload.get('sub')

        if username is None:
            raise HTTPException(status_code=401, detail='Invalid token')

        access_token = create_access_token({'sub': username})

        return {'access_token': access_token, 'token_type': 'bearer'}

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')


@auth_router.delete('/')
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()

    if user_db is None:
        raise HTTPException(status_code=404, detail='User not found')

    db.delete(user_db)
    db.commit()

    return {'message': 'User deleted successfully'}