import random, string
from sqlalchemy import select, update
from database.db import async_session
from database.models import Room, Vote, SwipeHistory

CODE_ALPH = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def gen_code(n: int = 6) -> str:
    return "".join(random.choices(CODE_ALPH, k=n))

async def create_room(user_id: int) -> Room:
    async with async_session() as s:
        code = gen_code()
        room = Room(code=code, user1_id=user_id)
        s.add(room)
        await s.commit()
        await s.refresh(room)
        return room

async def get_room_by_code(code: str) -> Room|None:
    async with async_session() as s:
        res = await s.execute(select(Room).where(Room.code==code, Room.active==True))
        return res.scalar_one_or_none()

async def join_room(room: Room, user_id: int) -> Room:
    async with async_session() as s:
        res = await s.execute(select(Room).where(Room.id==room.id))
        r = res.scalar_one()
        if r.user2_id and r.user2_id != user_id:
            return r
        if r.user1_id == user_id:
            return r
        r.user2_id = user_id
        await s.commit()
        return r

async def set_filters(room_id: int, content_type: str, genre_ids_csv: str, min_rating: float, min_year: int):
    async with async_session() as s:
        await s.execute(
            update(Room).where(Room.id==room_id).values(
                content_type=content_type,
                genre_ids=genre_ids_csv,
                min_rating=min_rating,
                min_year=min_year,
                idx=0,
            )
        )
        await s.commit()

async def record_vote(room_id: int, user_id: int, item_id: int, decision: str, value: float):
    async with async_session() as s:
        s.add(SwipeHistory(room_id=room_id, user_id=user_id, item_id=item_id, decision=decision))
        s.add(Vote(room_id=room_id, user_id=user_id, item_id=item_id, choice=value))
        try:
            await s.commit()
        except Exception:
            await s.rollback()

async def both_voted(room_id: int, item_id: int) -> bool:
    async with async_session() as s:
        res = await s.execute(select(Vote).where(Vote.room_id==room_id, Vote.item_id==item_id))
        return len(res.scalars().all()) >= 2
