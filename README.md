# Movie Match Bot (RU) — Railway-ready

## Что внутри
- Выбор: фильм / сериал
- Выбор жанра (RU)
- Свайпы синхронно для двух пользователей в "комнате"
- Матч-уведомления обоим при двух "👍"
- История свайпов
- Кнопка "Трейлер" (поиск на YouTube без API)

## Быстрый старт локально
1) Python 3.11+
2) `pip install -r requirements.txt`
3) Создайте `.env` по образцу `.env.example` и поставьте BOT_TOKEN
4) `python bot.py`

## Деплой на Railway
1) Создайте новый проект → New Service → Deploy from Repo/Empty
2) Загрузите все файлы из архива
3) В Settings → Variables добавьте `BOT_TOKEN`
4) Procfile уже настроен: `worker: python bot.py`
5) Нажмите Deploy. Бот запустится и создаст `app.db` (SQLite) автоматически.

## Команды
- `/start` — создание/вход
- `/join CODE` — присоединиться ко второй роли
- `/filters` — выбрать тип, жанры, пресет
- `/start_swipe CODE` — начать синхронный просмотр
- `/history CODE` — последние 10 решений

