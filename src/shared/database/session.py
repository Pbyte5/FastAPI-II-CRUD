from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, create_engine
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
from typing import Annotated


# Connection: la URL viene de la variable de entorno DATABASE_URL
# (en AWS la inyecta docker compose desde el .env del servidor)
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def life_span(app: FastAPI):
    init_db()
    yield

SessionDep = Annotated[Session, Depends(get_session)]