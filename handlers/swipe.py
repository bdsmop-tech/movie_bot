from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, update
from database.db import async_session
from database.models import Room
from services.tmdb_api import discover, youtube_search_url
from services.rooms import record_vote, both_voted
import re  # <-- добавлено

router = Router()

def build_card_kb(room_id: int, item_id: int, title: str):
    trailer_url = youtube_search_url(f"{title} трейлер")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👍 Смотреть", callback_data=f"vote_yes_{room_id}_{item_id}"),
         InlineKeyboardButton(text="🤷 Может", callback_data=f"vote_maybe_{room_id}_{item_id}"),
         InlineKeyboardButton(text="👎 Пропустить", callback_data=f"vote_no_{room_id}_{item_id}")],
        [InlineKeyboardButton(text="▶️ Трейлер", url=trailer_url)]
    ])
    return kb

# ... остальной код без изменений ...

@router.message(F.text.regexp(r"^/start_swipe\s+([A-Z0-9]{6,8})$"))
async def start_swipe(msg: types.Message, regexp: re.Match[str]):  # <-- заменено
    code = regexp.group(1)  # <-- заменено
    async with async_session() as s:
        rq = await s.execute(select(Room).where(Room.code==code, Room.active==True))
        room = rq.scalar_one_or_none()
        if not room:
            await msg.answer("Комната не найдена.")
            return
        if not (room.user1_id and room.user2_id):
            await msg.answer("Нужны два участника. Второй присоединился через /join?")
            return
        # вызов твоей функции send_card(...) как было
        # await send_card(msg, room)
