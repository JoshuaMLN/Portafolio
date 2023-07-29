from pydantic import BaseModel
from typing import Optional

class User(BaseModel): 
    email: str  
    username: str
    password: str

class UserAdmin(User):
    id: Optional[str] = "Null"
    disabled: Optional[bool] = False
    admin: Optional[bool] = False