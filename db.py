from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def init_db():
    from . import models  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
