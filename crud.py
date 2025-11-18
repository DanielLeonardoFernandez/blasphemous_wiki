from sqlmodel import Session, select
from models import Item, Categoria, Ubicacion, Interaccion, ItemLocationLink, ItemInteraccionLink
from schemas import ItemCreate, ItemUpdate
from typing import List, Optional


def create_categoria(
    session: Session,
    nombre: str,
    descripcion: str | None = None,
    imagen_url: str | None = None
) -> Categoria:
    cat = Categoria(
        nombre=nombre,
        descripcion=descripcion,
        imagen_url=imagen_url
    )
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat



def list_categorias(session: Session):
    # ✅ Solo las categorías activas
    return session.exec(select(Categoria).where(Categoria.activo == True)).all()


def get_categoria(session: Session, categoria_id: int) -> Categoria | None:
    # ✅ Solo categorías activas
    return session.exec(
        select(Categoria)
        .where(Categoria.id == categoria_id, Categoria.activo == True)
    ).first()


def update_categoria(session: Session, categoria_id: int, nombre: str | None, descripcion: str | None) -> Categoria | None:
    categoria = session.get(Categoria, categoria_id)
    if not categoria or not categoria.activo:
        return None

    if nombre is not None:
        categoria.nombre = nombre
    if descripcion is not None:
        categoria.descripcion = descripcion

    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


def delete_categoria(session: Session, categoria_id: int) -> bool:
    # ✅ Soft delete
    categoria = session.get(Categoria, categoria_id)
    if not categoria or not categoria.activo:
        return False
    categoria.activo = False
    session.add(categoria)
    session.commit()
    return True


# ✅ Nuevo: restaurar una categoría
def restaurar_categoria(session: Session, categoria_id: int) -> bool:
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        return False
    categoria.activo = True
    session.add(categoria)
    session.commit()
    return True

def listar_categorias_eliminadas(session: Session):
    return session.exec(select(Categoria).where(Categoria.activo == False)).all()


# --- Ubicaciones

def create_ubicacion(session: Session, nombre: str, tipo: str | None, descripcion: str | None) -> Ubicacion:
    u = Ubicacion(nombre=nombre, tipo=tipo, descripcion=descripcion)
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def list_ubicaciones(session: Session):
    # ✅ Solo ubicaciones activas
    return session.exec(select(Ubicacion).where(Ubicacion.activo == True)).all()


def get_ubicacion(session: Session, ubicacion_id: int):
    # ✅ Ignora las inactivas
    return session.exec(
        select(Ubicacion)
        .where(Ubicacion.id == ubicacion_id, Ubicacion.activo == True)
    ).first()


def update_ubicacion(session: Session, ubicacion_id: int, nombre: str, tipo: str | None, descripcion: str | None):
    u = session.get(Ubicacion, ubicacion_id)
    if not u or not u.activo:
        return None
    u.nombre = nombre
    u.tipo = tipo
    u.descripcion = descripcion
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def delete_ubicacion(session: Session, ubicacion_id: int):
    # ✅ Soft delete
    u = session.get(Ubicacion, ubicacion_id)
    if not u or not u.activo:
        return False
    u.activo = False
    session.add(u)
    session.commit()
    return True


# ✅ Nuevo: restaurar una ubicación
def restaurar_ubicacion(session: Session, ubicacion_id: int) -> bool:
    u = session.get(Ubicacion, ubicacion_id)
    if not u:
        return False
    u.activo = True
    session.add(u)
    session.commit()
    return True

def listar_ubicaciones_eliminadas(session: Session):
    return session.exec(select(Ubicacion).where(Ubicacion.activo == False)).all()


# --- Interacciones

def create_interaccion(session: Session, descripcion: str) -> Interaccion:
    i = Interaccion(descripcion=descripcion)
    session.add(i)
    session.commit()
    session.refresh(i)
    return i


def list_interacciones(session: Session):
    # ✅ Solo interacciones activas
    return session.exec(select(Interaccion).where(Interaccion.activo == True)).all()


def get_interaccion(session: Session, interaccion_id: int):
    # ✅ Ignora las inactivas
    return session.exec(
        select(Interaccion)
        .where(Interaccion.id == interaccion_id, Interaccion.activo == True)
    ).first()


def update_interaccion(session: Session, interaccion_id: int, descripcion: str):
    i = session.get(Interaccion, interaccion_id)
    if not i or not i.activo:
        return None
    i.descripcion = descripcion
    session.add(i)
    session.commit()
    session.refresh(i)
    return i


def delete_interaccion(session: Session, interaccion_id: int):
    # ✅ Soft delete
    i = session.get(Interaccion, interaccion_id)
    if not i or not i.activo:
        return False
    i.activo = False
    session.add(i)
    session.commit()
    return True


# ✅ Nuevo: restaurar interacción
def restaurar_interaccion(session: Session, interaccion_id: int) -> bool:
    i = session.get(Interaccion, interaccion_id)
    if not i:
        return False
    i.activo = True
    session.add(i)
    session.commit()
    return True

def listar_interacciones_eliminadas(session: Session):
    return session.exec(select(Interaccion).where(Interaccion.activo == False)).all()


# --- Items
def crear_item(session: Session, data: ItemCreate) -> Item:
    item = Item(
        nombre=data.nombre,
        descripcion=data.descripcion,
        costo=data.costo,
        indispensable=data.indispensable,
        categoria_id=data.categoria_id
    )
    session.add(item)
    session.commit()
    session.refresh(item)

    # asociar ubicaciones
    for uid in data.ubicacion_ids:
        # valida existencia
        if session.get(Ubicacion, uid):
            session.add(ItemLocationLink(item_id=item.id, ubicacion_id=uid))
    # asociar interacciones
    for iid in data.interaccion_ids:
        if session.get(Interaccion, iid):
            session.add(ItemInteraccionLink(item_id=item.id, interaccion_id=iid))

    session.commit()
    session.refresh(item)
    return item

def listar_items(session: Session):
    items = session.exec(
        select(Item)
        .where(Item.activo == True)  # ✅ solo activos
        .options(
            selectinload(Item.ubicaciones),
            selectinload(Item.interacciones)
        )
    ).all()

    # ✅ Convertir relaciones a listas de IDs
    result = []
    for it in items:
        result.append({
            "id": it.id,
            "nombre": it.nombre,
            "descripcion": it.descripcion,
            "costo": it.costo,
            "indispensable": it.indispensable,
            "categoria_id": it.categoria_id,
            "ubicacion_ids": [u.id for u in it.ubicaciones],
            "interaccion_ids": [i.id for i in it.interacciones]
        })
    return result


def get_item(session: Session, item_id: int):
    item = session.exec(
        select(Item)
        .where(Item.id == item_id, Item.activo == True)
        .options(
            selectinload(Item.ubicaciones),
            selectinload(Item.interacciones)
        )
    ).first()
    if not item:
        return None
    return {
        "id": item.id,
        "nombre": item.nombre,
        "descripcion": item.descripcion,
        "costo": item.costo,
        "indispensable": item.indispensable,
        "categoria_id": item.categoria_id,
        "ubicacion_ids": [u.id for u in item.ubicaciones],
        "interaccion_ids": [i.id for i in item.interacciones]
    }




def update_item(session: Session, item_id: int, data: ItemUpdate) -> Item | None:
    item = session.get(Item, item_id)
    if not item:
        return None
    # aplicar cambios simples
    for field, val in data.dict(exclude_unset=True).items():
        if field in ("ubicacion_ids", "interaccion_ids"):
            continue
        setattr(item, field, val)
    session.add(item)
    session.commit()
    session.refresh(item)

    # si se otorgan listas explícitas, re-asocia
    if data.ubicacion_ids is not None:
        # borrar links existentes
        session.exec(select(ItemLocationLink).where(ItemLocationLink.item_id == item.id)).all()
        session.query(ItemLocationLink).filter(ItemLocationLink.item_id == item.id).delete()
        for uid in data.ubicacion_ids:
            if session.get(Ubicacion, uid):
                session.add(ItemLocationLink(item_id=item.id, ubicacion_id=uid))

    if data.interaccion_ids is not None:
        session.query(ItemInteraccionLink).filter(ItemInteraccionLink.item_id == item.id).delete()
        for iid in data.interaccion_ids:
            if session.get(Interaccion, iid):
                session.add(ItemInteraccionLink(item_id=item.id, interaccion_id=iid))

    session.commit()
    session.refresh(item)
    return item

def delete_item(session: Session, item_id: int) -> bool:
    it = session.get(Item, item_id)
    if not it:
        return False
    it.activo = False  # ✅ marcar como inactivo
    session.add(it)
    session.commit()
    return True

def restaurar_item(session: Session, item_id: int) -> bool:
    it = session.get(Item, item_id)
    if not it:
        return False
    it.activo = True
    session.add(it)
    session.commit()
    return True

def listar_items_eliminados(session: Session):
    return session.exec(select(Item).where(Item.activo == False)).all()


def buscar_items(
    session: Session,
    categoria_id: Optional[int] = None,
    ubicacion_id: Optional[int] = None,
    indispensable: Optional[bool] = None,
    nombre: Optional[str] = None
) -> List[dict]:
    # Cargar relaciones many-to-many eficientemente
    query = select(Item).options(
        selectinload(Item.ubicaciones),
        selectinload(Item.interacciones)
    )

    # Filtros básicos
    if categoria_id is not None:
        query = query.where(Item.categoria_id == categoria_id)

    if indispensable is not None:
        query = query.where(Item.indispensable == indispensable)

    if nombre is not None:
        query = query.where(Item.nombre.ilike(f"%{nombre}%"))

    items = session.exec(query).all()

    # Filtro por ubicación (más claro y directo)
    if ubicacion_id is not None:
        items = [
            it for it in items
            if any(u.id == ubicacion_id for u in it.ubicaciones)
        ]

    # Convertir los resultados en un formato amigable para FastAPI
    results = []
    for it in items:
        results.append({
            "id": it.id,
            "nombre": it.nombre,
            "descripcion": it.descripcion,
            "costo": it.costo,
            "indispensable": it.indispensable,
            "categoria_id": it.categoria_id,
            "ubicacion_ids": [u.id for u in it.ubicaciones],
            "interaccion_ids": [i.id for i in it.interacciones],
        })

    return results

from sqlalchemy.orm import selectinload
from sqlmodel import select
from models import Item

def get_item_detallado(session: Session, item_id: int):
    stmt = (
        select(Item)
        .where(Item.id == item_id)
        .options(
            selectinload(Item.categoria),
            selectinload(Item.ubicaciones),
            selectinload(Item.interacciones)
        )
    )

    item = session.exec(stmt).first()
    if not item:
        return None

    # ✅ Convertir a formato compatible con ItemReadFull
    return {
        "id": item.id,
        "nombre": item.nombre,
        "descripcion": item.descripcion,
        "costo": item.costo,
        "indispensable": item.indispensable,
        "categoria_id": item.categoria_id,
        "categoria": {
            "id": item.categoria.id if item.categoria else None,
            "nombre": item.categoria.nombre if item.categoria else None,
            "descripcion": item.categoria.descripcion if item.categoria else None
        } if item.categoria else None,
        "ubicaciones": [
            {"id": u.id, "nombre": u.nombre, "tipo": u.tipo, "descripcion": u.descripcion}
            for u in item.ubicaciones
        ],
        "interacciones": [
            {"id": i.id, "descripcion": i.descripcion}
            for i in item.interacciones
        ]
    }

