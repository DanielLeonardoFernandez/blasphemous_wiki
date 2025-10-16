from sqlmodel import SQLModel, Field
from typing import Optional, List

# ==============================
# 📦 CATEGORÍAS
# ==============================
class CategoriaBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaRead(CategoriaBase):
    id: int

class CategoriaUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


# ==============================
# 🗺️ UBICACIONES
# ==============================
class UbicacionBase(SQLModel):
    nombre: str
    tipo: Optional[str] = None
    descripcion: Optional[str] = None

class UbicacionCreate(UbicacionBase):
    pass

class UbicacionRead(UbicacionBase):
    id: int


# ==============================
# 🔁 INTERACCIONES
# ==============================

class InteraccionCreate(SQLModel):
    descripcion: str


class InteraccionRead(SQLModel):
    id: int
    descripcion: str


class InteraccionUpdate(SQLModel):
    descripcion: Optional[str] = None


# ==============================
# ⚔️ ITEMS
# ==============================
class ItemBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    costo: Optional[int] = None
    indispensable: bool = False
    categoria_id: Optional[int] = None

class ItemCreate(ItemBase):
    ubicacion_ids: List[int] = Field(default_factory=list)
    interaccion_ids: List[int] = Field(default_factory=list)

class ItemRead(ItemBase):
    id: int
    ubicacion_ids: List[int] = Field(default_factory=list)
    interaccion_ids: List[int] = Field(default_factory=list)

class ItemUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    costo: Optional[int] = None
    indispensable: Optional[bool] = None
    categoria_id: Optional[int] = None
    ubicacion_ids: Optional[List[int]] = None
    interaccion_ids: Optional[List[int]] = None
