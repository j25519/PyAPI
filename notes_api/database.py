from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from databases import Database
from notes_api.config import config
from notes_api.models import NoteDB, Base
import asyncio

class DatabaseManager:
    def __init__(self):
        if config.DATABASE_TYPE == "sqlite":
            self.database = Database(config.SQLITE_URL)
            self.engine = create_async_engine(config.SQLITE_URL, echo=True)
            self.SessionLocal = sessionmaker(
                bind=self.engine, class_=AsyncSession, expire_on_commit=False
            )
        elif config.DATABASE_TYPE == "cloud":
            if not config.CLOUD_DB_API_KEY:
                raise ValueError("CLOUD_DB_API_KEY is required for cloud mode")
            raise NotImplementedError("Cloud DB not implemented yet")
        else:
            raise ValueError("Invalid DATABASE_TYPE")

    async def connect(self):
        if config.DATABASE_TYPE == "sqlite":
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        await self.database.connect()

    async def disconnect(self):
        await self.database.disconnect()
        await self.engine.dispose()

    async def create_note(self, note: dict):
        query = NoteDB.__table__.insert().values(**note)
        note_id = await self.database.execute(query)
        return note_id

    async def get_notes(self):
        query = NoteDB.__table__.select()
        return await self.database.fetch_all(query)

    async def get_note(self, note_id: int):
        query = NoteDB.__table__.select().where(NoteDB.id == note_id)
        return await self.database.fetch_one(query)

    async def update_note(self, note_id: int, note: dict):
        query = (
            NoteDB.__table__.update()
            .where(NoteDB.id == note_id)
            .values(**note)
        )
        await self.database.execute(query)
        return await self.get_note(note_id)

    async def delete_note(self, note_id: int):
        query = NoteDB.__table__.delete().where(NoteDB.id == note_id)
        await self.database.execute(query)

db_manager = DatabaseManager()
