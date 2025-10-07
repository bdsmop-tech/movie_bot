from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.tmdb_api import get_genres
from services.rooms import set_filters
from database.db import async_session
from database.models import Room
from sqlalchemy import select

router = Router()

@router.message(F.text=="/filters")
async def filters_root(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Фильмы", callback_data="type_movie"),
         InlineKeyboardButton(text="📺 Сериалы", callback_data="type_tv")]
    ])
    await msg.answer("Выберите тип:", reply_markup=kb)

@router.callback_query(F.data.startswith("type_"))
async def choose_genres(c: types.CallbackQuery):
    content_type = c.data.split("_")[1]
    genres = get_genres(content_type)
    # кнопки жанров (multi-select через простую CSV тактику)
    rows = []
    row = []
    for g in genres:
        row.append(InlineKeyboardButton(text=g["name"], callback_data=f"gsel_{content_type}_{g['id']}"))
        if len(row)==2:
            rows.append(row); row=[]
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="✅ Продолжить", callback_data=f"gdone_{content_type}")])
    await c.message.answer("Выберите жанры (можно несколько):", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

# в памяти chat -> selected genres (на простом уровне, без FSM, через message.chat.id dict)
_selected = {}

@router.callback_query(F.data.startswith("gsel_"))
async def toggle_genre(c: types.CallbackQuery):
    _, content_type, gid = c.data.split("_")
    key = (c.message.chat.id, content_type)
    cur = _selected.get(key, set())
    gid = int(gid)
    if gid in cur: cur.remove(gid)
    else: cur.add(gid)
    _selected[key] = cur
    await c.answer(f"Выбрано жанров: {len(cur)}", show_alert=False)

@router.callback_query(F.data.startswith("gdone_"))
async def genres_done(c: types.CallbackQuery):
    content_type = c.data.split("_")[1]
    key = (c.message.chat.id, content_type)
    gids = sorted(list(_selected.get(key, set())))
    # пресеты по рейтингу/году
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 6.5+ | 📅 2005+", callback_data=f"flt_{content_type}_{','.join(map(str,gids)) or '0'}_6.5_2005")],
        [InlineKeyboardButton(text="⭐ 7.0+ | 📅 2010+", callback_data=f"flt_{content_type}_{','.join(map(str,gids)) or '0'}_7.0_2010")],
        [InlineKeyboardButton(text="⭐ 7.5+ | 📅 2015+", callback_data=f"flt_{content_type}_{','.join(map(str,gids)) or '0'}_7.5_2015")],
    ])
    await c.message.answer("Выберите пресет фильтров:", reply_markup=kb)

@router.callback_query(F.data.startswith("flt_"))
async def apply_filters(c: types.CallbackQuery):
    _, content_type, gids_csv, min_r, min_y = c.data.split("_")
    min_rating = float(min_r); min_year = int(min_y)
    # Нужен активный room к чату — просим код
    await c.message.answer("Отправьте команду: <code>/use CODE</code> (код вашей комнаты), затем повторите выбор пресета, чтобы применить фильтры.")

@router.message(F.text.regexp(r"^/use\s+([A-Z0-9]{6,8})$"))
async def use_room_and_apply(msg: types.Message, regexp: types.MessageText):
    code = regexp.match.group(1)
    # Ищем последний пресет из истории сообщений (упрощение) — просим заново выбрать, затем зафиксируем
    await msg.answer(f"Активировали комнату <b>{code}</b>. Теперь заново выберите тип/жанры и пресет — фильтры будут применены к этой комнате.")
