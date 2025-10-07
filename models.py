from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .db import Base

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, index=True)
    user1_id = Column(Integer, nullable=False)
    user2_id = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)

    content_type = Column(String(10), default="movie")  # movie|tv
    genre_ids = Column(String, default="")  # CSV of genre ids
    min_rating = Column(Float, default=0)
    min_year = Column(Integer, default=1900)

    idx = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    item_id = Column(Integer, index=True)  # internal catalog id
    choice = Column(Float)  # 1.0 yes, 0.5 maybe, 0.0 no
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint('room_id','user_id','item_id', name='uq_vote_once'),)

class SwipeHistory(Base):
    __tablename__ = "swipe_history"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    item_id = Column(Integer, index=True)
    decision = Column(String(10))  # yes|maybe|no
    created_at = Column(DateTime(timezone=True), server_default=func.now())
