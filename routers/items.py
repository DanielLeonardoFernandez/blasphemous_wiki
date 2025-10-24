from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from db import get_session
from schemas import ItemCreate, ItemRead, ItemUpdate, ItemReadFull
import crud
from typing import Optional, List

router = APIRouter(prefix="/items", tags=["Items"])

# ---------------------------
# CREATE
# ---------------------------
@router.post("/", response_model=ItemRead)
def crear_item(item_in: ItemCreate, session: Session = Depends(get_session)):
    item = crud.crear_item(session, item_in)
    if not item:
        raise HTTPException(status_code=400, detail="Error al crear el ítem")
    return item


# ---------------------------
# READ ALL
# ---------------------------
@router.get("/", response_model=List[ItemRead])
def listar_items(session: Session = Depends(get_session)):
    return crud.listar_items(session)


# ---------------------------
# READ ALL (ELIMINADOS)
# 🔹 Debe ir antes de cualquier ruta con {item_id}
# ---------------------------
@router.get("/estado/eliminados", response_model=List[ItemRead])
def listar_items_eliminados(session: Session = Depends(get_session)):
    return crud.listar_items_eliminados(session)


# ---------------------------
# SEARCH / FILTER
# ---------------------------
@router.get("/search", response_model=List[ItemRead])
def buscar_items(
    categoria_id: Optional[int] = Query(default=None),
    ubicacion_id: Optional[int] = Query(default=None),
    indispensable: Optional[bool] = Query(default=None),
    nombre: Optional[str] = Query(default=None),
    session: Session = Depends(get_session)
):
    return crud.buscar_items(
        session,
        categoria_id=categoria_id,
        ubicacion_id=ubicacion_id,
        indispensable=indispensable,
        nombre=nombre,
    )


# ---------------------------
# READ ONE (DETALLADO)
# 🔹 Importante: antes de /{item_id}
# ---------------------------
@router.get("/{item_id}/detalles", response_model=ItemReadFull)
def obtener_item_detallado(item_id: int, session: Session = Depends(get_session)):
    item = crud.get_item_detallado(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return item


# ---------------------------
# RESTAURAR (activar ítem eliminado)
# ---------------------------
@router.put("/{item_id}/restaurar")
def restaurar_item(item_id: int, session: Session = Depends(get_session)):
    ok = crud.restaurar_item(session, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return {"ok": True, "mensaje": "Ítem restaurado correctamente"}


# ---------------------------
# READ ONE
# ---------------------------
@router.get("/{item_id}", response_model=ItemRead)
def obtener_item(item_id: int, session: Session = Depends(get_session)):
    item = crud.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return item


# ---------------------------
# UPDATE
# ---------------------------
@router.put("/{item_id}", response_model=ItemRead)
def actualizar_item(item_id: int, data: ItemUpdate, session: Session = Depends(get_session)):
    item = crud.update_item(session, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return item


# ---------------------------
# DELETE (soft delete)
# ---------------------------
@router.delete("/{item_id}")
def borrar_item(item_id: int, session: Session = Depends(get_session)):
    ok = crud.delete_item(session, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return {"ok": True, "mensaje": "Ítem marcado como inactivo"}
