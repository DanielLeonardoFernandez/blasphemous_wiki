import os
from typing import Optional
from fastapi import UploadFile
from supabase import create_client, Client

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


async def upload_to_bucket(file: UploadFile):
    """
    Sube un archivo al bucket y devuelve la URL pública.
    Mismo flujo que tu ejemplo, adaptado a tu proyecto.
    """
    client = get_supabase_client()

    try:
        file_content = await file.read()
        file_path = f"public/{file.filename}"

        client.storage.from_(SUPABASE_BUCKET).upload(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": file.content_type
            }
        )

        # Igual que tu ejemplo: obtener URL pública
        public_url = client.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
        return public_url

    except Exception as e:
        raise e