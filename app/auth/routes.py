from flask import Blueprint, request

from app.auth.service import (
    register_user,
    login_user,
    forgot_password
)

auth_bp = Blueprint("auth", __name__)


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