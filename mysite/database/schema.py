from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class StatusChoices(str, Enum):
    admin = 'admin'
    simple = 'simple'


class UserProfileCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    user_status: Optional[StatusChoices] = StatusChoices.simple

    class Config:
        from_attributes = True


class UserProfileOutSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    user_status: StatusChoices
    date_register: date

    class Config:
        from_attributes = True


class UserProfileLoginSchema(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class ChatGroupCreateSchema(BaseModel):
    owner_id: int
    name: str

    class Config:
        from_attributes = True


class ChatGroupOutSchema(BaseModel):
    id: int
    owner_id: int
    name: str
    create_date: datetime

    class Config:
        from_attributes = True


class GroupPeopleCreateSchema(BaseModel):
    group_id: int
    user_id: int

    class Config:
        from_attributes = True


class GroupPeopleOutSchema(BaseModel):
    id: int
    group_id: int
    user_id: int
    joined_date: datetime

    class Config:
        from_attributes = True


class ChatMessageCreateSchema(BaseModel):
    group_id: int
    user_id: int
    text: str

    class Config:
        from_attributes = True


class ChatMessageOutSchema(BaseModel):
    id: int
    group_id: int
    user_id: int
    text: str
    created_date: datetime

    class Config:
        from_attributes = True