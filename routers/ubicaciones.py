from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db import get_session
from schemas import UbicacionCreate, UbicacionRead
import crud

router = APIRouter(prefix="/ubicaciones", tags=["Ubicaciones"])

# ---------------------------
# CREAR
# ---------------------------
@router.post("/", response_model=UbicacionRead)
def create_ubicacion(data: UbicacionCreate, session: Session = Depends(get_session)):
    u = crud.create_ubicacion(session, data.nombre, data.tipo, data.descripcion)
    return UbicacionRead(id=u.id, nombre=u.nombre, tipo=u.tipo, descripcion=u.descripcion)

# ---------------------------
# LISTAR TODAS
# ---------------------------
@router.get("/", response_model=list[UbicacionRead])
def list_ubicaciones(session: Session = Depends(get_session)):
    ubicaciones = crud.list_ubicaciones(session)
    return [
        UbicacionRead(id=u.id, nombre=u.nombre, tipo=u.tipo, descripcion=u.descripcion)
        for u in ubicaciones
    ]

# ---------------------------
# LISTAR ELIMINADAS (SOFT DELETE)
# ---------------------------
@router.get("/eliminadas", response_model=list[UbicacionRead])
def listar_ubicaciones_eliminadas(session: Session = Depends(get_session)):
    ubicaciones = crud.listar_ubicaciones_eliminadas(session)
    return [
        UbicacionRead(id=u.id, nombre=u.nombre, tipo=u.tipo, descripcion=u.descripcion)
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
    return UbicacionRead(id=u.id, nombre=u.nombre, tipo=u.tipo, descripcion=u.descripcion)

# ---------------------------
# ACTUALIZAR
# ---------------------------
@router.put("/{ubicacion_id}", response_model=UbicacionRead)
def update_ubicacion(ubicacion_id: int, data: UbicacionCreate, session: Session = Depends(get_session)):
    u = crud.update_ubicacion(session, ubicacion_id, data.nombre, data.tipo, data.descripcion)
    if not u:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return UbicacionRead(id=u.id, nombre=u.nombre, tipo=u.tipo, descripcion=u.descripcion)

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
