import re
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, update
from database.db import async_session
from database.models import Room
from services.tmdb_api import discover, youtube_search_url
from services.rooms import record_vote, both_voted

router = Router()

def build_card_kb(room_id: int, item_id: int, title: str):
    trailer_url = youtube_search_url(f"{title} трейлер")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Смотреть", callback_data=f"vote_yes_{room_id}_{item_id}"),
            InlineKeyboardButton(text="🤷 Может",    callback_data=f"vote_maybe_{room_id}_{item_id}"),
            InlineKeyboardButton(text="👎 Пропустить", callback_data=f"vote_no_{room_id}_{item_id}"),
        ],
        [InlineKeyboardButton(text="▶️ Трейлер", url=trailer_url)],
    ])
    return kb

async def current_items(room: Room):
    gids = [int(x) for x in (room.genre_ids or "").split(",") if x.strip().isdigit()]
    return discover(
        content_type=room.content_type,
        genre_ids=gids if gids else None,
        min_rating=room.min_rating,
        min_year=room.min_year,
        page=1,
        page_size=50,
    )

async def send_card(ctx_msg: types.Message, room: Room):
    items = await current_items(room)
    if not items:
        await ctx_msg.answer("Ничего не найдено. Измените фильтры: /filters")
        return
    idx = max(0, min(room.idx, len(items) - 1))
    mv = items[idx]
    text = f"🎬 <b>{mv['title']}</b>\n⭐ {mv['rating']}  •  📅 {mv['year']}\n\n{mv['description']}"
    kb = build_card_kb(room.id, mv["id"], mv["title"])
    await ctx_msg.answer(text, reply_markup=kb)

@router.message(F.text.regexp(r"^/start_swipe\s+([A-Z0-9]{6,8})$"))
async def start_swipe(msg: types.Message):
    m = re.search(r"^/start_swipe\s+([A-Z0-9]{6,8})$", msg.text or "")
    if not m:
        return
    code = m.group(1)

    async with async_session() as s:
        rq = await s.execute(select(Room).where(Room.code == code, Room.active == True))
        room = rq.scalar_one_or_none()
        if not room:
            await msg.answer("Комната не найдена.")
            return
        if not (room.user1_id and room.user2_id):
            await msg.answer("Нужны два участника. Второй присоединился через /join CODE?")
            return
        await send_card(msg, room)

@router.callback_query(F.data.startswith("vote_"))
async def on_vote(c: types.CallbackQuery):
    try:
        _, decision, room_id, item_id = c.data.split("_")
    except Exception:
        await c.answer("Некорректные данные.", show_alert=True)
        return

    room_id = int(room_id); item_id = int(item_id)
    choice_map = {"yes": 1.0, "maybe": 0.5, "no": 0.0}
    await record_vote(room_id, c.from_user.id, item_id, decision, choice_map.get(decision, 0.0))

    if await both_voted(room_id, item_id):
        async with async_session() as s:
            rq = await s.execute(select(Room).where(Room.id == room_id))
            room = rq.scalar_one_or_none()
            if room:
                await c.message.answer("🔥 Матч! Оба выбрали 👍")
                await s.execute(update(Room).where(Room.id == room_id).values(idx=room.idx + 1))
                await s.commit()
                await send_card(c.message, room)
    else:
        await c.answer("Ок. Ждём второго участника…", show_alert=False)
