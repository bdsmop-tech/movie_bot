from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from services.rooms import create_room, get_room_by_code, join_room
from database.db import async_session
from database.models import Room
import re  # <-- добавлено

router = Router()

@router.callback_query(F.data=="room_create")
async def cb_room_create(c: types.CallbackQuery):
    r = await create_room(c.from_user.id)
    await c.message.answer(
        f"Комната создана. Код: <code>{r.code}</code>\n"
        "Передайте код напарнику. Он присоединится: /join CODE"
    )

@router.callback_query(F.data=="room_join")
async def cb_room_join(c: types.CallbackQuery):
    await c.message.answer("Введите: <code>/join ABC123</code>")

@router.message(F.text.regexp(r"^/join\s+([A-Z0-9]{6,8})$"))
async def join_cmd(msg: types.Message, regexp: re.Match[str]):  # <-- заменено
    code = regexp.group(1)  # <-- заменено (раньше было regexp.match.group(1))
    room = await get_room_by_code(code)
    if not room:
        await msg.answer("Комната не найдена или неактивна.")
        return
    room = await join_room(room, msg.from_user.id)
    if room.user1_id and room.user2_id:
        await msg.answer("Оба участника подключены. Настройте фильтры: /filters")
        await msg.answer(f"Для запуска: /start_swipe {room.code}")
    else:
        await msg.answer("Вы в комнате. Ожидаем второго участника.")
