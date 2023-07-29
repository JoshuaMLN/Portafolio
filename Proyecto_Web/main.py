from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from routers import me, access, admin

app=FastAPI()
# Prueba con VisualCode
# uvicorn main:app --reload
# http://127.0.0.1:8000

# Routers
app.include_router(access.router)
app.include_router(me.router)
app.include_router(admin.router)

# Ruta para servir los archivos estáticos desde la carpeta "front"
app.mount("/front", StaticFiles(directory="static/front"), name="front")

# Utilizamos Jinja2Templates para renderizar las páginas HTML
templates = Jinja2Templates(directory="front")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return RedirectResponse(url="/front/login.html")

@app.get("/front/login.html", response_class=HTMLResponse)
async def read_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/front/register.html", response_class=HTMLResponse)
async def read_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
