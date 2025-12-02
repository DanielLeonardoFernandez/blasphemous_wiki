from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlmodel import Session
from db import get_session
from schemas import ItemCreate, ItemRead, ItemUpdate, ItemReadFull
import crud
from typing import Optional, List
from supa.supabase import upload_to_bucket
from os import getenv
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/items", tags=["Items"])

# ---------------------------
# CREATE
# ---------------------------
@router.post("/", response_model=ItemRead)
async def crear_item(
    nombre: str = Form(...),
    descripcion: str = Form(None),
    costo: float | None = Form(None),
    indispensable: bool = Form(False),
    categoria_ids: list[int] = Form([]),
    ubicacion_ids: list[int] = Form([]),
    interaccion_ids: list[int] = Form([]),
    imagen: UploadFile | None = File(None),
    session: Session = Depends(get_session)
):

    imagen_url = None

    # Subir imagen si viene
    if imagen:
        imagen_url = await upload_to_bucket(imagen, bucket=getenv("BUCKET_ITEMS"))

    # Crear DTO para crud
    data = ItemCreate(
        nombre=nombre,
        descripcion=descripcion,
        costo=costo,
        indispensable=indispensable,
        categoria_ids=categoria_ids,
        ubicacion_ids=ubicacion_ids,
        interaccion_ids=interaccion_ids
    )

    item = crud.crear_item(session, data, imagen_url)

    if not item:
        raise HTTPException(status_code=400, detail="Error al crear el ítem")

    return item

"""
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
"""
# ---------------------------
# LISTAR TODOS LOS ITEMS
# ---------------------------
@router.get("/", response_class=HTMLResponse)
def listar_items(request: Request, session: Session = Depends(get_session)):
    items = crud.listar_items(session)
    return templates.TemplateResponse("items/items.html", {
        "request": request,
        "items": items
    })

# ---------------------------
# LISTAR ITEMS ELIMINADOS (SOFT DELETE)
# 🔹 Debe ir antes de cualquier ruta con {item_id}
# ---------------------------
@router.get("/estado/eliminados", response_class=HTMLResponse)
def listar_items_eliminados(request: Request, session: Session = Depends(get_session)):
    items = crud.listar_items_eliminados(session)
    return templates.TemplateResponse("items/items_eliminados.html", {
        "request": request,
        "items": items
    })
"""
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
"""


@router.get("/search", response_class=HTMLResponse)
def buscar_items_html(
        request: Request,
        categoria_id: Optional[str] = Query(default=None),
        ubicacion_id: Optional[str] = Query(default=None),
        indispensable: Optional[str] = Query(default=None),
        nombre: Optional[str] = Query(default=None),
        session: Session = Depends(get_session)
):
    # Convertir strings vacíos a tipos correctos
    categoria_id_int = int(categoria_id) if categoria_id else None
    ubicacion_id_int = int(ubicacion_id) if ubicacion_id else None

    if indispensable == "true":
        indispensable_bool = True
    elif indispensable == "false":
        indispensable_bool = False
    else:
        indispensable_bool = None

    items = crud.buscar_items(
        session,
        ubicacion_id=ubicacion_id_int,
        indispensable=indispensable_bool,
        nombre=nombre,
    )

    # Filtrado por categoría si se indicó
    if categoria_id_int is not None:
        items = [
            it for it in items
            if any(c.id == categoria_id_int for c in getattr(it, "categorias", []))
        ]

    return templates.TemplateResponse(
        "items/items.html",
        {
            "request": request,
            "items": items,
            "categoria_id": categoria_id,
            "ubicacion_id": ubicacion_id,
            "indispensable": indispensable,
            "nombre": nombre
        }
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

"""
# ---------------------------
# READ ONE
# ---------------------------
@router.get("/{item_id}", response_model=ItemRead)
def obtener_item(item_id: int, session: Session = Depends(get_session)):
    item = crud.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return item
"""

# ---------------------------
# OBTENER ITEM POR ID
# ---------------------------
@router.get("/{item_id}", response_class=HTMLResponse)
def obtener_item(request: Request, item_id: int, session: Session = Depends(get_session)):
    item = crud.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return templates.TemplateResponse("items/items_detalles.html", {
        "request": request,
        "item": item
    })

# ---------------------------
# UPDATE
# ---------------------------
@router.put("/{item_id}", response_model=ItemRead)
async def actualizar_item(
    item_id: int,
    nombre: str = Form(None),
    descripcion: str = Form(None),
    costo: float | None = Form(None),
    indispensable: bool = Form(False),
    categoria_ids: list[int] | None = Form(None),
    ubicacion_ids: list[int] | None = Form(None),
    interaccion_ids: list[int] | None = Form(None),
    imagen: UploadFile | None = File(None),
    session: Session = Depends(get_session)
):

    imagen_url = None

    if imagen is not None:
        # Caso 1: limpiar imagen
        if imagen.filename == "":
            imagen_url = ""

        # Caso 2: se sube imagen nueva
        elif imagen.file:
            imagen_url = await upload_to_bucket(imagen, bucket=getenv("BUCKET_ITEMS"))

        # Caso 3: valor extraño
        else:
            imagen_url = None

    # Crear DTO de actualización
    data = ItemUpdate(
        nombre=nombre,
        descripcion=descripcion,
        costo=costo,
        indispensable=indispensable,
        categoria_ids=categoria_ids,  # <-- lista
        ubicacion_ids=ubicacion_ids,
        interaccion_ids=interaccion_ids
    )

    item = crud.update_item(session, item_id, data, imagen_url)

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
