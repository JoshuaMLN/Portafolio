from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from typing import List, Dict

from db.models.user import UserAdmin
from db.client import db_client
from db.schemas.user import admin_schema, admins_schema
from routers.access import crypt, search_user, auth_admin


router = APIRouter(prefix="/admin",
                   tags=["Admin"],
                   responses={
                        status.HTTP_404_NOT_FOUND: {
                            "message": "No se encontro la página"
                            }
                       },
                       dependencies = [Depends(auth_admin)]
                    )


# Obtener la lista de usuarios con contraseña
@router.get("/show", response_model = List[Dict], status_code= status.HTTP_200_OK)
async def show_users():
    return admins_schema(db_client.users.find())

# Obtener un usuario a partir de un id especifico
@router.get("/find/{id}", response_model = dict)
async def find_user(id: str):
    validate_id(id)
    user = search_user("_id", ObjectId(id))
    if  user == "Null":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=  "No existe un usuario con ese id")
    return admin_schema(user)

# Modificar un usuario
@router.put("/update", response_model = dict, status_code=status.HTTP_202_ACCEPTED)
async def update_user(user: UserAdmin):
    # Validamos que existe un usuario con el id
    validate_id(user.id)
    # Validamos los cambios del usuario
    validate_user_update(user)
    # creamos ese usuario sin id
    user_dict = dict(user)
    del user_dict["id"]
    # Encriptamos la contraseña
    user_dict["password"] = crypt.encrypt(user.password)
    # Actualizamos los campos del usuario (excepto el id) 
    db_client.users.find_one_and_replace({"_id": ObjectId(user.id)}, user_dict)
    return admin_schema(db_client.users.find_one({"_id": ObjectId(user.id)}))

# Eliminar un usuario a partir de un id especifico
@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str):
    validate_id(id)
    search_user("_id",ObjectId(id))
    # Buscamos y borramos en la base de daots un usuario con ese id
    db_client.users.find_one_and_delete({"_id": ObjectId(id)})


# --------------------------------
# Funciones Adicionales
# --------------------------------

# Validar id
def validate_id(id: str):
    if id == "Null":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Debe ingresar un id"
        )
    try:    
            return ObjectId(id)
    except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "El id debe tener 24 digitos"
                ) 

# Validar campos al actualizar un usuario
def validate_user_update(user: UserAdmin):
    user_old = search_user("_id",ObjectId(user.id))
    if user_old == "Null":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "No se encontro un usuario con ese id"
        )
    # Comprobamos que no cause conflicto con otros usuarios
    #  Con respecto a su usuario
    if user.username != user_old.username and type(search_user("username", user.username)) == UserAdmin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail = "Nombre de usuario ya registrado"
                )
    #  Con respecto a su email
    if user.email != user_old.email and type(search_user("email", user.email)) == UserAdmin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail = "Email ya registrado"
                )
