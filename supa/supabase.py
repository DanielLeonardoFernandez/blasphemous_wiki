import os
from typing import Optional
from fastapi import UploadFile
from supabase import create_client, Client
from dotenv import load_dotenv
import re
import unicodedata
import uuid

if os.getenv("RENDER") is None:
    load_dotenv()

# Cargar credenciales desde variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

# Cliente cacheado (como en tu ejemplo)
_supabase_client: Optional[Client] = None


def get_supabase_client():
    """
    Devuelve el cliente global de Supabase.
    Se inicializa solo una vez, igual que en tu ejemplo original.
    """
    global _supabase_client

    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("No están configuradas las credenciales de Supabase")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

    return _supabase_client

def sanitize_filename(filename: str) -> str:
    # Normalizar para quitar acentos
    filename = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode()

    # Reemplazar cualquier caracter no permitido por _
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    return filename

async def upload_to_bucket(file: UploadFile, bucket: str | None = None):
    """
    Sube un archivo al bucket y devuelve la URL pública.
    Genera un nombre único para evitar errores 409 (Duplicate).

    Parámetros:
    - file: UploadFile de FastAPI
    - bucket: nombre del bucket en Supabase. Si es None usa SUPABASE_BUCKET (valor por defecto en .env)
    """
    client = get_supabase_client()

    # usar bucket pasado o el por defecto desde .env
    target_bucket = bucket or SUPABASE_BUCKET

    try:
        file_content = await file.read()

        # Extraer extensión del archivo
        ext = file.filename.split(".")[-1].lower()

        # Nombre seguro + UUID
        safe_name = sanitize_filename(file.filename.rsplit(".", 1)[0])
        unique_name = f"{safe_name}_{uuid.uuid4()}.{ext}"

        # Ruta final en supabase
        file_path = f"public/{unique_name}"

        client.storage.from_(target_bucket).upload(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": file.content_type
            }
        )

        # URL pública
        public_url = client.storage.from_(target_bucket).get_public_url(file_path)
        return public_url

    except Exception as e:
        raise e
