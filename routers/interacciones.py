from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session
from db import get_session
from schemas import InteraccionCreate, InteraccionRead, InteraccionUpdate
import crud
from supa.supabase import upload_to_bucket
from os import getenv

router = APIRouter(prefix="/interacciones", tags=["Interacciones"])

# ---------------------------
# CREAR
# ---------------------------
@router.post("/", response_model=InteraccionRead)
async def create_interaccion(
    descripcion: str = Form(...),
    imagen: UploadFile | None = File(None),
    session: Session = Depends(get_session)
):
    imagen_url = None

    # ✔ Si viene imagen → subir al bucket
    if imagen:
        imagen_url = await upload_to_bucket(imagen, bucket=getenv("BUCKET_INTERACCIONES"))

    i = crud.create_interaccion(
        session=session,
        descripcion=descripcion,
        imagen_url=imagen_url
    )

    return InteraccionRead(
        id=i.id,
        descripcion=i.descripcion,
        imagen_url=i.imagen_url
    )


# ---------------------------
# LISTAR TODAS
# ---------------------------
@router.get("/", response_model=list[InteraccionRead])
def list_interacciones(session: Session = Depends(get_session)):
    interacciones = crud.list_interacciones(session)
    return [InteraccionRead(id=i.id, descripcion=i.descripcion, imagen_url=i.imagen_url) for i in interacciones]

# ---------------------------
# LISTAR ELIMINADAS (SOFT DELETE)
# ---------------------------
@router.get("/eliminadas", response_model=list[InteraccionRead])
def listar_interacciones_eliminadas(session: Session = Depends(get_session)):
    interacciones = crud.listar_interacciones_eliminadas(session)
    return [InteraccionRead(id=i.id, descripcion=i.descripcion, imagen_url=i.imagen_url) for i in interacciones]

# ---------------------------
# OBTENER POR ID
# ---------------------------
@router.get("/id/{interaccion_id}", response_model=InteraccionRead)
def get_interaccion(interaccion_id: int, session: Session = Depends(get_session)):
    i = crud.get_interaccion(session, interaccion_id)
    if not i:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    return InteraccionRead(id=i.id, descripcion=i.descripcion, imagen_url=i.imagen_url)

# ---------------------------
# ACTUALIZAR
# ---------------------------
@router.put("/{interaccion_id}", response_model=InteraccionRead)
async def update_interaccion(
    interaccion_id: int,
    descripcion: str = Form(None),
    imagen: UploadFile | None = File(None),
    session: Session = Depends(get_session)
):
    imagen_url = None

    if imagen is not None:
        if imagen.filename == "":
            # ✔ Borrar imagen
            imagen_url = ""
        else:
            # ✔ Subir nueva
            imagen_url = await upload_to_bucket(imagen, bucket=getenv("BUCKET_INTERACCIONES"))

    i = crud.update_interaccion(
        session=session,
        interaccion_id=interaccion_id,
        descripcion=descripcion,
        imagen_url=imagen_url
    )

    if not i:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")

    return InteraccionRead(
        id=i.id,
        descripcion=i.descripcion,
        imagen_url=i.imagen_url
    )

# ---------------------------
# ELIMINAR (SOFT DELETE)
# ---------------------------
@router.delete("/{interaccion_id}")
def delete_interaccion(interaccion_id: int, session: Session = Depends(get_session)):
    ok = crud.delete_interaccion(session, interaccion_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    return {"ok": True, "mensaje": "Interacción eliminada correctamente"}

# ---------------------------
# RESTAURAR
# ---------------------------
@router.put("/{interaccion_id}/restaurar")
def restaurar_interaccion(interaccion_id: int, session: Session = Depends(get_session)):
    ok = crud.restaurar_interaccion(session, interaccion_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Interacción no encontrada o no estaba eliminada")
    return {"ok": True, "mensaje": "Interacción restaurada correctamente"}
