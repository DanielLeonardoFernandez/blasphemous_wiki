from fastapi import APIRouter, UploadFile, File, HTTPException
from storage.supabase import upload_to_bucket

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