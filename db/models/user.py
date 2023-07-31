from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel): 
    email: str  
    username: str
    password: str
    birthdate: str

class UserAdmin(User):
    id: Optional[str] = "Null"
    disabled: Optional[bool] = False
    admin: Optional[bool] = False