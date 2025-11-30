from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session
from db import get_session
from schemas import UbicacionCreate, UbicacionRead
import crud
from supa.supabase import upload_to_bucket
from os import getenv

router = APIRouter(prefix="/ubicaciones", tags=["Ubicaciones"])

# ---------------------------
# CREAR
# ---------------------------
@router.post("/", response_model=UbicacionRead)
async def create_ubicacion(
    nombre: str = Form(...),
    tipo: str | None = Form(None),
    descripcion: str | None = Form(None),
    imagen: UploadFile | None = File(None),
    session: Session = Depends(get_session)
):
    imagen_url = None

    # Subir imagen si viene
    if imagen:
        imagen_url = await upload_to_bucket(imagen, bucket=getenv("BUCKET_UBICACIONES"))

    u = crud.create_ubicacion(session, nombre, tipo, descripcion)
    u.imagen_url = imagen_url  # guardarla en el modelo

    session.add(u)
    session.commit()
    session.refresh(u)

    return UbicacionRead(
        id=u.id,
        nombre=u.nombre,
        tipo=u.tipo,
        descripcion=u.descripcion,
        imagen_url=u.imagen_url
    )


# ---------------------------
# LISTAR TODAS
# ---------------------------
@router.get("/", response_model=list[UbicacionRead])
def list_ubicaciones(session: Session = Depends(get_session)):
    ubicaciones = crud.list_ubicaciones(session)
    return [
        UbicacionRead(id=u.id, nombre=u.nombre, tipo=u.tipo, descripcion=u.descripcion, imagen_url=u.imagen_url)
        for u in ubicaciones
    ]

# ---------------------------
# LISTAR ELIMINADAS (SOFT DELETE)
# ---------------------------
@router.get("/eliminadas", response_model=list[UbicacionRead])
def listar_ubicaciones_eliminadas(session: Session = Depends(get_session)):
    ubicaciones = crud.listar_ubicaciones_eliminadas(session)
    return [
        UbicacionRead(id=u.id, nombre=u.nombre, tipo=u.tipo, descripcion=u.descripcion, imagen_url=u.imagen_url)
        for u in ubicaciones
    ]

# ---------------------------
# OBTENER POR ID
# ---------------------------
@router.get("/id/{ubicacion_id}", response_model=UbicacionRead)
def get_ubicacion(ubicacion_id: int, session: Session = Depends(get_session)):
    u = crud.get_ubicacion(session, ubicacion_id)
    if not u:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return UbicacionRead(id=u.id, nombre=u.nombre, tipo=u.tipo, descripcion=u.descripcion, imagen_url=u.imagen_url)

# ---------------------------
# ACTUALIZAR
# ---------------------------
@router.put("/{ubicacion_id}", response_model=UbicacionRead)
async def update_ubicacion(
    ubicacion_id: int,
    nombre: str | None = Form(None),
    tipo: str | None = Form(None),
    descripcion: str | None = Form(None),
    imagen: UploadFile | None = File(None),
    session: Session = Depends(get_session)
):
    imagen_url = None

    if imagen is not None:
        # Caso 1: campo enviado vacío → borrar imagen
        if imagen.filename == "":
            imagen_url = ""

        # Caso 2: archivo subido → subir al bucket
        elif imagen.file:
            imagen_url = await upload_to_bucket(imagen, bucket=getenv("BUCKET_UBICACIONES"))

        # Caso 3: algo raro → no tocar
        else:
            imagen_url = None

    u = crud.update_ubicacion(
        session,
        ubicacion_id,
        nombre,
        tipo,
        descripcion,
        imagen_url  # ✔ enviar control total al crud
    )

    if not u:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")

    return UbicacionRead(
        id=u.id,
        nombre=u.nombre,
        tipo=u.tipo,
        descripcion=u.descripcion,
        imagen_url=u.imagen_url
    )

# ---------------------------
# ELIMINAR (SOFT DELETE)
# ---------------------------
@router.delete("/{ubicacion_id}")
def delete_ubicacion(ubicacion_id: int, session: Session = Depends(get_session)):
    ok = crud.delete_ubicacion(session, ubicacion_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return {"ok": True, "mensaje": "Ubicación eliminada correctamente"}

# ---------------------------
# RESTAURAR
# ---------------------------
@router.put("/{ubicacion_id}/restaurar")
def restaurar_ubicacion(ubicacion_id: int, session: Session = Depends(get_session)):
    ok = crud.restaurar_ubicacion(session, ubicacion_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada o no estaba eliminada")
    return {"ok": True, "mensaje": "Ubicación restaurada correctamente"}
