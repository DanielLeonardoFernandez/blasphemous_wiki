# db.py
import os
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select

# 1) Tomar la URL desde la variable de entorno (Render) o usar SQLite local si no existe
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./blasphemous.db"

# 2) Crear el engine (echo=True para ver queries en logs; puedes poner False en prod si quieres menos ruido)
engine = create_engine(DATABASE_URL, echo=True)

# 3) Dependencia para obtener sesión
def get_session():
    with Session(engine) as session:
        yield session

# 4) Lifespan: crear tablas al iniciar la app (no hace seed ni inserciones)
@asynccontextmanager
async def create_tables(app):
    """
    Lifespan manager para FastAPI.
    Crea las tablas definidas en SQLModel si no existen.
    No inserta datos de ejemplo (seed) — eso se hace manualmente si lo deseas.
    """
    SQLModel.metadata.create_all(engine)
    yield
