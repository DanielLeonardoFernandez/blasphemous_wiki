from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db import get_session
from schemas import CategoriaCreate, CategoriaRead, CategoriaUpdate
import crud

router = APIRouter(prefix="/categorias", tags=["categorias"])

# Crear categoría
@router.post("/", response_model=CategoriaRead)
def create_categoria(data: CategoriaCreate, session: Session = Depends(get_session)):
    cat = crud.create_categoria(session, data.nombre, data.descripcion)
    return CategoriaRead(id=cat.id, nombre=cat.nombre, descripcion=cat.descripcion)


# Listar todas las categorías
@router.get("/", response_model=list[CategoriaRead])
def list_categorias(session: Session = Depends(get_session)):
    categorias = crud.list_categorias(session)
    return [CategoriaRead(id=c.id, nombre=c.nombre, descripcion=c.descripcion) for c in categorias]

# Listar categorías eliminadas (soft delete)
@router.get("/eliminadas", response_model=list[CategoriaRead])
def listar_categorias_eliminadas(session: Session = Depends(get_session)):
    categorias = crud.listar_categorias_eliminadas(session)
    return [CategoriaRead(id=c.id, nombre=c.nombre, descripcion=c.descripcion) for c in categorias]


# Obtener una categoría por ID
@router.get("/{categoria_id}", response_model=CategoriaRead)
def get_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = crud.get_categoria(session, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return CategoriaRead(id=categoria.id, nombre=categoria.nombre, descripcion=categoria.descripcion)


# Actualizar una categoría
@router.put("/{categoria_id}", response_model=CategoriaRead)
def update_categoria(categoria_id: int, data: CategoriaUpdate, session: Session = Depends(get_session)):
    categoria = crud.update_categoria(session, categoria_id, data.nombre, data.descripcion)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return CategoriaRead(id=categoria.id, nombre=categoria.nombre, descripcion=categoria.descripcion)


# Eliminar una categoría
@router.delete("/{categoria_id}")
def delete_categoria(categoria_id: int, session: Session = Depends(get_session)):
    success = crud.delete_categoria(session, categoria_id)
    if not success:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"ok": True}

# Restaurar una categoría eliminada (soft delete)
@router.put("/{categoria_id}/restaurar")
def restaurar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    ok = crud.restaurar_categoria(session, categoria_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"ok": True, "mensaje": "Categoría restaurada correctamente"}

