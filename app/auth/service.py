import bcrypt
from flask_jwt_extended import create_access_token

from app.auth.data import users


def register_user(data):

    for user in users:
        if user["email"] == data["email"]:
            return {
                "message": "Email already exists"
            }, 400

    password = bcrypt.hashpw(
        data["password"].encode(),
        bcrypt.gensalt()
    )

    new_user = {
        "name": data["name"],
        "email": data["email"],
        "password": password
    }

    users.append(new_user)

    return {
        "message": "User Registered Successfully"
    }, 201


def login_user(data):

    for user in users:

        if user["email"] == data["email"]:

            if bcrypt.checkpw(
                data["password"].encode(),
                user["password"]
            ):

                token = create_access_token(identity=user["email"])

                return {
                    "access_token": token
                }, 200

            return {
                "message": "Invalid Password"
            }, 401

    return {
        "message": "User not found"
    }, 404


def forgot_password(data):

    for user in users:

        if user["email"] == data["email"]:

            return {
                "message": "Password reset link sent."
            }, 200

    return {
        "message": "Email not found"
    }, 404