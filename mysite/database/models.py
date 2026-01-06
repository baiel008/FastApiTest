from .db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Enum, Date, ForeignKey, DateTime, Text
from enum import Enum as PyEnum
from datetime import date, datetime
from typing import List

class StatusChoices(str, PyEnum):
    admin = 'admin'
    simple = 'simple'

class UserProfile(Base):
    __tablename__ = 'profile'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(500))
    email: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String)
    user_status: Mapped[StatusChoices] = mapped_column(Enum(StatusChoices), default=StatusChoices.simple)
    date_register: Mapped[date] = mapped_column(Date, default=date.today)

    owner_chat: Mapped[List['ChatGroup']] = relationship(back_populates='owner',
                                                        cascade='all, delete-orphan')
    user_groups: Mapped[List['GroupPeople']] = relationship(back_populates='user',
                                                            cascade='all, delete-orphan')

    user_sms: Mapped[List['ChatMessage']] = relationship(back_populates='user_message',
                                                         cascade='all, delete-orphan')

    user_token: Mapped[List['RefreshToken']] = relationship(back_populates='user',
                                                            cascade='all, delete-orphan')


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('profile.id'))
    user: Mapped[UserProfile] = relationship(back_populates='user_token')
    token: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)



class ChatGroup(Base):
    __tablename__ = 'group'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('profile.id'))
    owner: Mapped[UserProfile] = relationship(UserProfile, back_populates='owner_chat')
    name: Mapped[str] = mapped_column(String(100))
    create_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    group_chats: Mapped[List['GroupPeople']] = relationship(back_populates='group',
                                                            cascade='all, delete-orphan')

    group_messages: Mapped[List['ChatMessage']] = relationship(back_populates='group_mes',
                                                               cascade='all, delete-orphan')

class GroupPeople(Base):
    __tablename__ = 'people'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('group.id'))
    group: Mapped[ChatGroup] = relationship(ChatGroup, back_populates='group_chats')
    user_id: Mapped[int] = mapped_column(ForeignKey('profile.id'))
    user: Mapped[UserProfile] = relationship(back_populates='user_groups')
    joined_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = 'message'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('group.id'))
    group_mes: Mapped[ChatGroup] = relationship(ChatGroup, back_populates='group_messages')
    user_id: Mapped[int] = mapped_column(ForeignKey('profile.id'))
    user_message: Mapped[UserProfile] = relationship(back_populates='user_sms')
    text: Mapped[str] = mapped_column(Text)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
