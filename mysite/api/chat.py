from fastapi import HTTPException, Depends, APIRouter
from mysite.database.models import ChatGroup, UserProfile, StatusChoices
from mysite.database.schema import ChatGroupCreateSchema, ChatGroupOutSchema
from mysite.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


group_chat_router = APIRouter(prefix='/group', tags=['Chat Group'])


def check_group_owner(group_id: int, user_id: int, db: Session):
    group = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail='Группа табылган жок')

    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')

    if group.owner_id != user_id and user.user_status != StatusChoices.admin:
        raise HTTPException(status_code=403, detail='Бул группаны башкарууга укук жок')

    return group


@group_chat_router.post('/', response_model=dict)
async def group_create(group: ChatGroupCreateSchema, db: Session = Depends(get_db)):
    owner = db.query(UserProfile).filter(UserProfile.id == group.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail='Ээси табылган жок')

    group_db = ChatGroup(**group.dict())
    db.add(group_db)
    db.commit()
    db.refresh(group_db)
    return {'message': 'Saved'}


@group_chat_router.get('/', response_model=List[ChatGroupOutSchema])
async def group_list(db: Session = Depends(get_db)):
    return db.query(ChatGroup).all()


@group_chat_router.get('/{group_id}', response_model=ChatGroupOutSchema)
async def group_detail(group_id: int, db: Session = Depends(get_db)):
    group_db = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(status_code=404, detail='Группа табылган жок')
    return group_db


@group_chat_router.put('/{group_id}', response_model=ChatGroupOutSchema)
async def group_update(group_id: int, group: ChatGroupCreateSchema,
                       current_user_id: int, db: Session = Depends(get_db)):
    group_db = check_group_owner(group_id, current_user_id, db)

    owner = db.query(UserProfile).filter(UserProfile.id == group.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail='Ээси табылган жок')

    for group_key, group_value in group.dict().items():
        setattr(group_db, group_key, group_value)

    db.add(group_db)
    db.commit()
    db.refresh(group_db)
    return group_db


@group_chat_router.delete('/{group_id}')
async def group_delete(group_id: int, current_user_id: int, db: Session = Depends(get_db)):
    group_db = check_group_owner(group_id, current_user_id, db)

    db.delete(group_db)
    db.commit()
    return {'message': 'Deleted'}


@group_chat_router.get('/owner/{owner_id}', response_model=List[ChatGroupOutSchema])
async def groups_by_owner(owner_id: int, db: Session = Depends(get_db)):
    owner = db.query(UserProfile).filter(UserProfile.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')

    return db.query(ChatGroup).filter(ChatGroup.owner_id == owner_id).all()
