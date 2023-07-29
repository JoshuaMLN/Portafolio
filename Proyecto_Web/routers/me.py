from fastapi import APIRouter, status, Depends

from db.models.user import UserAdmin
from db.schemas.user import user_schema
from routers.access import auth_user

router = APIRouter(prefix="/me",
                   tags=["Me"],
                   responses={
                        status.HTTP_404_NOT_FOUND: {
                            "message": "No se encontro la página"
                            }
                       },
                       dependencies = [Depends(auth_user)]
                    )

# Usuario logeado
my_user = router.dependencies[0]

# API's
@router.get("/profile", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def profile(user: UserAdmin = my_user):
    return user_schema(user)


    