from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

engine = create_async_engine(
    "sqlite+aiosqlite:///applicants.db"
)

new_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class ApplicantsORM(Base):
    __tablename__ = "applicants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    phone: Mapped[str | None]
    email: Mapped[str | None]
    snils: Mapped[str | None]
    contest_uuid: Mapped[str | None]
    competition_group: Mapped[str | None]
    type_of_places: Mapped[str | None]
    priority: Mapped[int | None]
    status: Mapped[str | None]
    original_docs: Mapped[bool | None]
    epgu_docs: Mapped[str | None]
    vuz: Mapped[str | None]
    number: Mapped[int | None]
    exam_1: Mapped[int | None]
    exam_2: Mapped[int | None]
    exam_3: Mapped[int | None]
    personal_achivements: Mapped[int | None]
    total_score: Mapped[int | None]
    last_update_on_server: Mapped[datetime | None]
    places: Mapped[int | None]


class CompetitionGroupsORM(Base):
    __tablename__ = "competition_groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    contest_uuid: Mapped[str | None]
    places: Mapped[int | None]

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def drop_app_table():
    async with engine.begin() as conn:
        await conn.run_sync(ApplicantsORM.metadata.drop_all)

async def create_app_table():
    async with engine.begin() as conn:
        await conn.run_sync(ApplicantsORM.metadata.create_all)