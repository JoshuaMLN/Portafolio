from db.models.user import User, UserAdmin

def user_schema(user):
    if type(user) == UserAdmin:
        return {
                "username": user.username,
                "email":    user.email,
                "birthdate": user.birthdate,
                "gender": user.gender
                }
    return {
            "username": str(user["username"]),
            "email":    str(user["email"]),
            "birthdate": str(user["birthdate"]),
             "gender":    str(user["gender"])
            }

def admin_schema(user):
    if type(user) == UserAdmin:
        return { "id": user.id,
                "username": user.username,
                "password": user.password,
                "email":    user.email,
                "gender": user.gender,
                "birthdate": user.birthdate,
                "disabled": user.disabled,
                "admin":    user.admin
                }
    return {
            "id":       str(user["_id"]),
            "username": str(user["username"]),
            "password": str(user["password"]),
            "email":    str(user["email"]),
            "gender":    str(user["gender"]),
            "birthdate": str(user["birthdate"]),
            "disabled": bool(user["disabled"]),
            "admin":    bool(user["admin"])
            }

def users_schema(users) -> list:
    return [user_schema(user) for user in users]

def admins_schema(users) -> list:
    return [admin_schema(user) for user in users]