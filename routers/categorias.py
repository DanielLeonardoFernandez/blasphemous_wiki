from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session
from db import get_session
from schemas import CategoriaCreate, CategoriaRead, CategoriaUpdate
import crud
from supa.supabase import upload_to_bucket
from typing import Optional
from os import getenv


router = APIRouter(prefix="/categorias", tags=["Categorías"])

# ---------------------------
# CREAR
# ---------------------------
@router.post("/", response_model=CategoriaRead)
async def create_categoria(
    nombre: str = Form(...),
    descripcion: str = Form(None),
    imagen: UploadFile = File(None),
    session: Session = Depends(get_session)
):
    imagen_url = None

    # Subir imagen si viene
    if imagen:
        imagen_url = await upload_to_bucket(imagen, bucket=getenv("SUPABASE_BUCKET"))

    cat = crud.create_categoria(session, nombre, descripcion, imagen_url)

    return CategoriaRead(
        id=cat.id,
        nombre=cat.nombre,
        descripcion=cat.descripcion,
        imagen_url=cat.imagen_url
    )

# ---------------------------
# LISTAR TODAS
# ---------------------------
@router.get("/", response_model=list[CategoriaRead])
def list_categorias(session: Session = Depends(get_session)):
    categorias = crud.list_categorias(session)
    return [
        CategoriaRead(
            id=c.id,
            nombre=c.nombre,
            descripcion=c.descripcion,
            imagen_url=c.imagen_url
        )
        for c in categorias
    ]

# ---------------------------
# LISTAR ELIMINADAS
# ---------------------------
@router.get("/eliminadas", response_model=list[CategoriaRead])
def listar_categorias_eliminadas(session: Session = Depends(get_session)):
    categorias = crud.listar_categorias_eliminadas(session)
    return [
        CategoriaRead(
            id=c.id,
            nombre=c.nombre,
            descripcion=c.descripcion,
            imagen_url=c.imagen_url
        )
        for c in categorias
    ]

# ---------------------------
# OBTENER POR ID
# ---------------------------
@router.get("/id/{categoria_id}", response_model=CategoriaRead)
def get_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = crud.get_categoria(session, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return CategoriaRead(
        id=categoria.id,
        nombre=categoria.nombre,
        descripcion=categoria.descripcion,
        imagen_url=categoria.imagen_url
    )

# ---------------------------
# ACTUALIZAR
# ---------------------------
@router.put("/{categoria_id}", response_model=CategoriaRead)
async def update_categoria(
    categoria_id: int,
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    imagen: UploadFile | None = File(None),  # ← mantiene input FILE normal
    session: Session = Depends(get_session)
):

    imagen_url = None

    if imagen is not None:
        # Caso 1: campo enviado vacío (send empty value)
        if imagen.filename == "":
            imagen_url = ""

        # Caso 2: el usuario sí sube archivo normal
        elif imagen.file:
            imagen_url = await upload_to_bucket(
                imagen,
                bucket=getenv("SUPABASE_BUCKET")   # ← AQUÍ EL CAMBIO
            )

        # Caso 3: algo raro
        else:
            imagen_url = None

    # Si imagen == None → NO tocar imagen en BD

    categoria = crud.update_categoria(
        session,
        categoria_id,
        nombre,
        descripcion,
        imagen_url
    )

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return CategoriaRead(
        id=categoria.id,
        nombre=categoria.nombre,
        descripcion=categoria.descripcion,
        imagen_url=categoria.imagen_url
    )


# ---------------------------
# ELIMINAR (SOFT DELETE)
# ---------------------------
@router.delete("/{categoria_id}")
def delete_categoria(categoria_id: int, session: Session = Depends(get_session)):
    success = crud.delete_categoria(session, categoria_id)
    if not success:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"ok": True, "mensaje": "Categoría eliminada correctamente"}

# ---------------------------
# RESTAURAR
# ---------------------------
@router.put("/{categoria_id}/restaurar")
def restaurar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    ok = crud.restaurar_categoria(session, categoria_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Categoría no encontrada o no estaba eliminada")
    return {"ok": True, "mensaje": "Categoría restaurada correctamente"}
