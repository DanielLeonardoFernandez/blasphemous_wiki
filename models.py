from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
import datetime

# --- Bucket URL ---

class Imagen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    fecha_subida: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

# --- Link tables ---
class ItemLocationLink(SQLModel, table=True):
    item_id: Optional[int] = Field(default=None, foreign_key="item.id", primary_key=True)
    ubicacion_id: Optional[int] = Field(default=None, foreign_key="ubicacion.id", primary_key=True)

class ItemInteraccionLink(SQLModel, table=True):
    item_id: Optional[int] = Field(default=None, foreign_key="item.id", primary_key=True)
    interaccion_id: Optional[int] = Field(default=None, foreign_key="interaccion.id", primary_key=True)


# --- Modelos principales ---
class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)  # ✅ agregado

    items: List["Item"] = Relationship(back_populates="categoria")



class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    costo: Optional[int] = None
    indispensable: bool = False
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    activo: bool = Field(default=True)  # ✅ nuevo campo lógico

    categoria: Optional[Categoria] = Relationship(back_populates="items")

    ubicaciones: List["Ubicacion"] = Relationship(back_populates="items", link_model=ItemLocationLink)
    interacciones: List["Interaccion"] = Relationship(back_populates="items", link_model=ItemInteraccionLink)


class Ubicacion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)  # ✅ nuevo campo lógico

    items: List[Item] = Relationship(back_populates="ubicaciones", link_model=ItemLocationLink)

class Interaccion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    descripcion: str
    activo: bool = Field(default=True)  # ✅ nuevo campo lógico

    items: List[Item] = Relationship(back_populates="interacciones", link_model=ItemInteraccionLink)
