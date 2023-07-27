from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from routers import me, access, admin

app=FastAPI()
# uvicorn main:app --reload
# http://127.0.0.1:8000

# Routers
app.include_router(access.router)
app.include_router(me.router)
app.include_router(admin.router)

app.mount("/images", StaticFiles(directory="static/images"), name="gura")

@app.get("/",tags=["Home"], status_code=status.HTTP_200_OK)
async def home():
    return {"message":"Bienvenido a mi proyecto de Backend"}

