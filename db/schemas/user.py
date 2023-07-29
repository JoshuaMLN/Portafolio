from db.models.user import User, UserAdmin

def user_schema(user):
    if type(user) == UserAdmin:
        return {
                "username": user.username,
                "email":    user.email
                }
    return {
            
            "username": str(user["username"]),
            "email":    str(user["email"])
            }

def admin_schema(user):
    if type(user) == UserAdmin:
        return { "id": user.id,
                "username": user.username,
                "password": user.password,
                "email":    user.email,
                "disabled": user.disabled,
                "admin":    user.admin
                }
    return {
            "id":       str(user["_id"]),
            "username": str(user["username"]),
            "password": str(user["password"]),
            "email":    str(user["email"]),
            "disabled": bool(user["disabled"]),
            "admin":    bool(user["admin"])
            }

def users_schema(users) -> list:
    return [user_schema(user) for user in users]

def admins_schema(users) -> list:
    return [admin_schema(user) for user in users]