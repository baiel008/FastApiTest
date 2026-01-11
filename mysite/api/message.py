from fastapi import HTTPException, Depends, APIRouter
from mysite.database.models import ChatMessage, ChatGroup, UserProfile, GroupPeople
from mysite.database.schema import ChatMessageCreateSchema, ChatMessageOutSchema
from mysite.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


message_router = APIRouter(prefix='/message', tags=['Chat Message'])


@message_router.post('/', response_model=dict)
async def message_create(message: ChatMessageCreateSchema, db: Session = Depends(get_db)):
    group = db.query(ChatGroup).filter(ChatGroup.id == message.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail='Группа табылган жок')

    user = db.query(UserProfile).filter(UserProfile.id == message.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')

    is_member = db.query(GroupPeople).filter(
        GroupPeople.group_id == message.group_id,
        GroupPeople.user_id == message.user_id
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail='Колдонуучу группага мүчө эмес')

    if not message.text or message.text.strip() == '':
        raise HTTPException(status_code=400, detail='Билдирүү бош болбошу керек')

    message_db = ChatMessage(**message.dict())
    db.add(message_db)
    db.commit()
    db.refresh(message_db)
    return {'message': 'Saved'}


@message_router.get('/', response_model=List[ChatMessageOutSchema])
async def message_list(db: Session = Depends(get_db)):
    return db.query(ChatMessage).all()


@message_router.get('/{message_id}', response_model=ChatMessageOutSchema)
async def message_detail(message_id: int, db: Session = Depends(get_db)):
    message_db = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message_db:
        raise HTTPException(status_code=404, detail='Билдирүү табылган жок')
    return message_db



@message_router.delete('/{message_id}')
async def message_delete(message_id: int, db: Session = Depends(get_db)):
    message_db = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if message_db is None:
        raise HTTPException(status_code=404, detail='Андай маалымат жок')

    db.delete(message_db)
    db.commit()
    return {'message': 'Deleted'}


# @message_router.get('/group/{group_id}', response_model=List[ChatMessageOutSchema])
# async def message_by_group(group_id: int, db: Session = Depends(get_db)):
#     group = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
#     if not group:
#         raise HTTPException(status_code=404, detail='Группа табылган жок')
#
#     return db.query(ChatMessage).filter(ChatMessage.group_id == group_id).all()
