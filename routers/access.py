from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from email_validator import validate_email as validar_correo, EmailNotValidError
import re
from datetime import date

from db.models.user import User, UserAdmin
from db.schemas.user import admin_schema
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
                            "message": "No se encontro la página."
                            }
                       }
                    )


# Iniciar sesión
@router.post("/login", response_model = dict, status_code= status.HTTP_202_ACCEPTED)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # Buscamos si existe el usuario
    user = search_user("username", form.username)
    if type(user) is not UserAdmin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="El usuario no existe.")
    # Verificamos si la contraseña es correcta
    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="La contraseña es incorrecta.")
    if user.disabled == True:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="Usuario desactivado temporalmente. Pongase en contacto con el administrador.")
    token = generate_token(user.username, user.admin)
    # Retornamos el token
    return {"access_token": token, "token_type": "bearer"}

# Registrar un usuario
@router.post("/register", response_model = dict, status_code=status.HTTP_201_CREATED)
async def add_user(user: User):
    # Validamos los datos del usuario a crear
    validate_email(user.email)
    user.birthdate = validate_birthday(user.birthdate)
    validate_user_creation(user)
    # Creamos el usuario sin el id
    user_dict = dict(user)
    user_dict.setdefault("disabled", False)
    user_dict.setdefault("admin", False)
    # Encriptamos la contraseña
    user_dict["password"] = crypt.encrypt(user.password)
    user_dict["birthdate"] = str(user_dict["birthdate"])
    # Mongodb le asigna un id al usuario y lo añadimos a la bd
    db_client.users.insert_one(user_dict).inserted_id
    mensaje: str = "Usuario creado exitosamente."
    # Buscamos el usuario creado y retornamos
    return {"mensaje": mensaje}



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

def traducir_error(error_message: str):
    error_punto = "The part after the @-sign is not valid. It should have a period."
    error_dominio = "The domain name"
    error_email_largo = "The email address is too long before the @-sign"
    error_dominio_superior = "The part after the @-sign is not valid. It is not within a valid top-level domain."

    if error_punto in error_message:
        error_message = "La parte que sigue al signo @ no es válida. Debe tener un punto."

    if error_dominio in error_message:
        patron = r"(\b(?:\w+\.)+\w+\b)"
        coincidencias = re.search(patron, error_message)
        error_message = "El dominio " + coincidencias.group() + " no existe."

    if error_email_largo in error_message:
        patron = r"\((\d+)"
        coincidencias = re.search(patron, error_message)
        if coincidencias:
            error_message = "La dirección de correo electrónico es demasiado larga antes del signo @ " + coincidencias.group() +" carácteres de más)"

    if error_dominio_superior in error_message:
        error_message = "La parte que sigue al signo @ no es válida. No está dentro de un dominio de nivel superior válido."

    return error_message

def validate_email(email: str):
    try:
        validar_correo(email,check_deliverability=True)
    except EmailNotValidError as e:
        error_message = traducir_error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
def validate_birthday(birthdate: str):
    fecha_nacimiento = datetime.strptime(birthdate, "%Y-%m-%d").date()
    fecha_actual = date.today()
    edad = fecha_actual.year - fecha_nacimiento.year - ((fecha_actual.month, fecha_actual.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    if edad < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Debes de ser mayor de 10 años para poder registrarte.")
    return fecha_nacimiento.strftime("%d-%m-%Y")

def validate_user_creation(user: User):
    # Comprobamos que no cause conflicto con otros usuarios
    #  Con respecto a su usuario
    if type(search_user("username", user.username)) == UserAdmin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = "Nombre de usuario ya registrado."
            )
    #  Con respecto a su email
    if type(search_user("email", user.email)) == UserAdmin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = "Email ya registrado."
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
             detail="Su sesión expiró. Inicie sesión nuevamente.", 
             headers={"WWW_Authenticate": "Bearer"})
    try:
        username = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")
        if username is None:
            raise exception
    except JWTError:
        raise exception
    
    user = search_user("username", username)
    return user

async def auth_admin(user: UserAdmin = Depends(auth_user)):
    if user.admin == False:
        raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Credenciales de autenticación como administrador inválidas.", 
             headers={"WWW_Authenticate": "Bearer"})