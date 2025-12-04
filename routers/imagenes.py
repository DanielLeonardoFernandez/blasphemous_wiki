from fastapi import APIRouter, UploadFile, File, HTTPException
from supa.supabase import upload_to_bucket
from fastapi.templating import Jinja2Templates

from sqlalchemy import func
from sqlmodel import select, Session
from db import get_session
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Item, Categoria, Ubicacion, Interaccion

templates = Jinja2Templates(directory="templates")


router = APIRouter(prefix="/imagenes", tags=["Imágenes"])


@router.post("/upload", status_code=201)
async def subir_imagen(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    try:
        url = await upload_to_bucket(file)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, session: Session = Depends(get_session)):
    total_items = session.exec(select(func.count(Item.id))).one()
    total_categorias = session.exec(select(func.count(Categoria.id))).one()
    total_ubicaciones = session.exec(select(func.count(Ubicacion.id))).one()
    total_interacciones = session.exec(select(func.count(Interaccion.id))).one()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_items": total_items,
            "total_categorias": total_categorias,
            "total_ubicaciones": total_ubicaciones,
            "total_interacciones": total_interacciones
        }
    )
