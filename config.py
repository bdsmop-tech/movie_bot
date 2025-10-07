import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# SQLite by default, no config needed
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
