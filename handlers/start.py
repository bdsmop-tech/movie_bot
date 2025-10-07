from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.message(F.text=="/start")
async def start(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать комнату", callback_data="room_create")],
        [InlineKeyboardButton(text="🔑 Присоединиться по коду", callback_data="room_join")],
    ])
    await msg.answer("Movie Match RU. Выберите действие:", reply_markup=kb)
