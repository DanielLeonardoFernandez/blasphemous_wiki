from fastapi import FastAPI
from db import create_tables
from routers import items, categorias, ubicaciones, interacciones

app = FastAPI(lifespan=create_tables, title="Blasphemous Wiki API")

app.include_router(items.router)
app.include_router(categorias.router)
app.include_router(ubicaciones.router)
app.include_router(interacciones.router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la Wiki de Blasphemous"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hola {name}, bienvenido a la wiki!"}

