from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.auth.service import (
    register_user,
    login_user,
    forgot_password,
    reset_password,
    update_user_profile,
    change_password
)


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():

    email = get_jwt_identity()

    return {
        "message": "Authentication successful",
        "email": email
    }, 200

@auth_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_me():

    current_email = get_jwt_identity()

    data = request.get_json()

    return update_user_profile(
        current_email,
        data
    )

@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_user_password():

    current_email = get_jwt_identity()

    data = request.get_json()

    return change_password(
        current_email,
        data
    )

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    return register_user(data)


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    return login_user(data)


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot():

    data = request.get_json()

    return forgot_password(data)


@auth_bp.route("/reset-password", methods=["POST"])
def reset():

    data = request.get_json()

    return reset_password(data)

    