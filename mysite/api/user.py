from fastapi import HTTPException, Depends, APIRouter
from mysite.database.models import UserProfile, StatusChoices
from mysite.database.schema import UserProfileCreateSchema, UserProfileOutSchema, UserProfileLoginSchema
from mysite.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


user_router = APIRouter(prefix='/user', tags=['User Profile'])


def check_admin(user_id: int, db: Session):
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')
    if user.user_status != StatusChoices.admin:
        raise HTTPException(status_code=403, detail='Администратор укуктары жок')
    return user


def check_owner(user_id: int, current_user_id: int, db: Session):
    if user_id != current_user_id:
        user = db.query(UserProfile).filter(UserProfile.id == current_user_id).first()
        if not user or user.user_status != StatusChoices.admin:
            raise HTTPException(status_code=403, detail='Бул аккаунтту өзгөртүүгө укук жок')


@user_router.post('/', response_model=dict)
async def user_create(user: UserProfileCreateSchema, db: Session = Depends(get_db)):
    existing_user = db.query(UserProfile).filter(
        (UserProfile.username == user.username) | (UserProfile.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail='Мындай колдонуучу бар')

    user_db = UserProfile(**user.dict())
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return {'message': 'Saved'}


@user_router.get('/', response_model=List[UserProfileOutSchema])
async def user_list(db: Session = Depends(get_db)):
    return db.query(UserProfile).all()


@user_router.get('/{user_id}', response_model=UserProfileOutSchema)
async def user_detail(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')
    return user_db


@user_router.put('/{user_id}', response_model=UserProfileOutSchema)
async def user_update(user_id: int, user: UserProfileCreateSchema,
                      current_user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')

    check_owner(user_id, current_user_id, db)

    for user_key, user_value in user.dict(exclude_unset=True).items():
        setattr(user_db, user_key, user_value)

    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@user_router.delete('/{user_id}')
async def user_delete(user_id: int, current_user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail='Андай маалымат жок')

    check_owner(user_id, current_user_id, db)

    db.delete(user_db)
    db.commit()
    return {'message': 'Deleted'}


@user_router.post('/login', response_model=dict)
async def user_login(login_data: UserProfileLoginSchema, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.username == login_data.username).first()

    if not user_db:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')

    if user_db.password != login_data.password:
        raise HTTPException(status_code=401, detail='Пароль туура эмес')

    return {'message': 'Login successful', 'user_id': user_db.id, 'status': user_db.user_status}


@user_router.patch('/{user_id}/status', response_model=UserProfileOutSchema)
async def change_user_status(user_id: int, new_status: StatusChoices,
                             admin_id: int, db: Session = Depends(get_db)):
    check_admin(admin_id, db)


    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')

    user_db.user_status = new_status
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db
