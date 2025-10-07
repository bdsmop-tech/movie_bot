from aiogram import Router, types, F
from sqlalchemy import select, desc
from database.db import async_session
from database.models import SwipeHistory, Room
router = Router()

@router.message(F.text.startswith("/history"))
async def history_cmd(msg: types.Message):
    parts = msg.text.split()
    if len(parts) < 2:
        await msg.answer("Использование: /history CODE")
        return
    code = parts[1]
    async with async_session() as s:
        rq = await s.execute(select(Room).where(Room.code==code))
        room = rq.scalar_one_or_none()
        if not room:
            await msg.answer("Комната не найдена")
            return
        q = await s.execute(
            select(SwipeHistory.item_id, SwipeHistory.decision)
            .where(SwipeHistory.room_id==room.id, SwipeHistory.user_id==msg.from_user.id)
            .order_by(desc(SwipeHistory.created_at))
            .limit(10)
        )
        items = q.all()
        if not items:
            await msg.answer("История пуста.")
            return
        lines = [f"• {iid} — {dec}" for iid, dec in items]
        await msg.answer("Последние решения:\n" + "\n".join(lines))
