from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db import get_session
from schemas import InteraccionCreate, InteraccionRead, InteraccionUpdate
import crud

router = APIRouter(prefix="/interacciones", tags=["Interacciones"])

# ---------------------------
# CREAR
# ---------------------------
@router.post("/", response_model=InteraccionRead)
def create_interaccion(data: InteraccionCreate, session: Session = Depends(get_session)):
    i = crud.create_interaccion(session, data.descripcion)
    return InteraccionRead(id=i.id, descripcion=i.descripcion)

# ---------------------------
# LISTAR TODAS
# ---------------------------
@router.get("/", response_model=list[InteraccionRead])
def list_interacciones(session: Session = Depends(get_session)):
    interacciones = crud.list_interacciones(session)
    return [InteraccionRead(id=i.id, descripcion=i.descripcion) for i in interacciones]

# ---------------------------
# LISTAR ELIMINADAS (SOFT DELETE)
# ---------------------------
@router.get("/eliminadas", response_model=list[InteraccionRead])
def listar_interacciones_eliminadas(session: Session = Depends(get_session)):
    interacciones = crud.listar_interacciones_eliminadas(session)
    return [InteraccionRead(id=i.id, descripcion=i.descripcion) for i in interacciones]

# ---------------------------
# OBTENER POR ID
# ---------------------------
@router.get("/id/{interaccion_id}", response_model=InteraccionRead)
def get_interaccion(interaccion_id: int, session: Session = Depends(get_session)):
    i = crud.get_interaccion(session, interaccion_id)
    if not i:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    return InteraccionRead(id=i.id, descripcion=i.descripcion)

# ---------------------------
# ACTUALIZAR
# ---------------------------
@router.put("/{interaccion_id}", response_model=InteraccionRead)
def update_interaccion(interaccion_id: int, data: InteraccionUpdate, session: Session = Depends(get_session)):
    i = crud.update_interaccion(session, interaccion_id, data.descripcion)
    if not i:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    return InteraccionRead(id=i.id, descripcion=i.descripcion)

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
