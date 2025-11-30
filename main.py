from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import create_tables
from routers import items, categorias, ubicaciones, interacciones, imagenes

app = FastAPI(lifespan=create_tables, title="Blasphemous Wiki API")

#  Static y Templates

# Servir archivos estáticos (CSS, imágenes, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Motor de plantillas Jinja2
templates = Jinja2Templates(directory="templates")

app.include_router(items.router)
app.include_router(categorias.router)
app.include_router(ubicaciones.router)
app.include_router(interacciones.router)
app.include_router(imagenes.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/hello/{name}", response_class=HTMLResponse)
async def say_hello(request: Request, name: str):
    return templates.TemplateResponse(
        "hello.html",
        {"request": request, "texto": name.upper()}
    )

# -------------------------
#  Manejo de errores HTML
# -------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
    )