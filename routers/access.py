from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from db.models.user import User, UserAdmin
from db.schemas.user import user_schema, admin_schema
from db.client import db_client

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 5
SECRET = "pyXBdJgF3f7VpNxTwUMekB8x2JwhZSfKfDMwZq2BvXFZRhM9fvafC4g8YzMXHLT"

crypt = CryptContext(schemes=["bcrypt"])
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(prefix="/access",
                   tags=["Access"],
                   responses={
                        status.HTTP_404_NOT_FOUND: {
                            "message": "No se encontro la página"
                            }
                       }
                    )


# Iniciar sesión
@router.post("/login", response_model = dict, status_code= status.HTTP_202_ACCEPTED)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # Buscamos si existe el usuario
    user = search_user("username", form.username)
    if type(user) is not UserAdmin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="El usuario no es correcto")
    # Verificamos si la contraseña es correcta
    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="La contraseña no es correcta")
    token = generate_token(user.username, user.admin)
    # Retornamos el token
    return {"access_token": token, "token_type": "bearer"}

# Registrar un usuario
@router.post("/register", response_model = dict, status_code=status.HTTP_201_CREATED)
async def add_user(user: User):
    # Validamos los datos del usuario a crear
    validate_user_creation(user)
    # Creamos el usuario sin el id
    user_dict = dict(user)
    user_dict.setdefault("disabled", False)
    user_dict.setdefault("admin", False)
    # Encriptamos la contraseña
    user_dict["password"] = crypt.encrypt(user.password)
    # Mongodb le asigna un id al usuario y lo añadimos a la bd
    db_client.users.insert_one(user_dict).inserted_id
    # Buscamos el usuario creado y retornamos
    return {"message": "Usuario creado exitosamente"}



# --------------------------------
# Funciones Adicionales
# --------------------------------


# Generador de token
def generate_token(username: str, admin: bool):
    # Tiempo en el cual exporara el token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)
    # Creamos el token de autorización al usuario
    access_token = {"sub": username, "admin": str(admin), "exp": expire}
    # Retornamos el token codificado
    return jwt.encode(access_token, SECRET, algorithm=ALGORITHM)


def validate_user_creation(user: User):
    # Comprobamos que no cause conflicto con otros usuarios
    #  Con respecto a su usuario
    if type(search_user("username", user.username)) == UserAdmin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = "Nombre de usuario ya registrado"
            )
    #  Con respecto a su email
    if type(search_user("email", user.email)) == UserAdmin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = "Email ya registrado"
            )
    
def search_user(field: str, key):
    # Buscamos el usuario con el campo ingresado
    try:
        user = admin_schema(db_client.users.find_one({field: key}))
        return UserAdmin(**user)
    except:
        return "Null"



# FUNCIONES ASYNCRONICAS

async def auth_user(token : str = Depends(oauth2)):
    exception = HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Credenciales de autenticación inválidas", 
             headers={"WWW_Authenticate": "Bearer"})
    try:
        username = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")
        if username is None:
            raise exception
        
    except JWTError:
        raise exception
    
    user = search_user("username", username)

    if user.disabled:
        raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Usuario Inactivo")
    
    return user

async def auth_admin(user: UserAdmin = Depends(auth_user)):
    if user.admin == False:
        raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Credenciales de autenticación como administrador inválidas", 
             headers={"WWW_Authenticate": "Bearer"})