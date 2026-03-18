import os
from dotenv import load_dotenv

import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Column

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5431)

PG_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)

    def id_dict(self):
        return {"id": self.id}


class Advertisement(Base):

    __tablename__ = "advertisements"

    # Связь с таблицей User
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='advertisements')

    header: MappedColumn[str] = mapped_column(String, unique=True)
    description: MappedColumn[str] = mapped_column(String)
    owner: MappedColumn[str] = mapped_column(String)
    registration_date: MappedColumn[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


    @property
    def dict(self):
        return {
            "id":self.id,
            "header":self.header,
            "description": self.description,
            "owner": self.owner,
            "registration_date": self.registration_date.isoformat()
        }


class User(Base):

    __tablename__ = "users"

    # Связь с таблицей Advertisement
    advertisements = relationship('Advertisement', back_populates='user')

    name: MappedColumn[str] = mapped_column(String, unique=True)
    password: MappedColumn[str] = mapped_column(String)
    registration_time: MappedColumn[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "registration_time": self.registration_time.isoformat(),
        }

async def init_orm():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_orm():
    await engine.dispose()