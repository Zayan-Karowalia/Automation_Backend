import bcrypt

from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import User


def register_user(data):

    # Check whether email already exists
    existing_user = User.query.filter_by(
        email=data["email"]
    ).first()

    if existing_user:
        return {
            "message": "Email already exists"
        }, 400

    # Hash password
    password = bcrypt.hashpw(
        data["password"].encode(),
        bcrypt.gensalt()
    ).decode()

    # Create User object
    new_user = User(
        name=data["name"],
        email=data["email"],
        password=password
    )

    # Save to PostgreSQL
    db.session.add(new_user)
    db.session.commit()

    return {
        "message": "User Registered Successfully"
    }, 201


def login_user(data):

    user = User.query.filter_by(
        email=data["email"]
    ).first()

    if not user:
        return {
            "message": "User not found"
        }, 404

    if bcrypt.checkpw(
        data["password"].encode(),
        user.password.encode()
    ):

        token = create_access_token(
            identity=user.email
        )

        return {
            "access_token": token
        }, 200

    return {
        "message": "Invalid Password"
    }, 401


def forgot_password(data):

    user = User.query.filter_by(
        email=data["email"]
    ).first()

    if user:

        return {
            "message": "Password reset link sent."
        }, 200

    return {
        "message": "Email not found"
    }, 404


def update_user_profile(current_email, data):

    # Find currently logged-in user
    user = User.query.filter_by(
        email=current_email
    ).first()

    if not user:
        return {
            "message": "User not found"
        }, 404

    # Get new values
    new_name = data.get("name")
    new_email = data.get("email")

    # Update name if provided
    if new_name:
        user.name = new_name

    # Update email if provided
    if new_email:

        # Check whether another user already has this email
        existing_user = User.query.filter(
            User.email == new_email,
            User.id != user.id
        ).first()

        if existing_user:
            return {
                "message": "Email already exists"
            }, 400

        user.email = new_email

    # Save changes to PostgreSQL
    db.session.commit()

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }, 200


def change_password(current_email, data):

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    # Validate input
    if not current_password or not new_password:
        return {
            "message": "Current password and new password are required"
        }, 400

    # Find logged-in user
    user = User.query.filter_by(
        email=current_email
    ).first()

    if not user:
        return {
            "message": "User not found"
        }, 404

    # Verify current password
    if not bcrypt.checkpw(
        current_password.encode(),
        user.password.encode() if isinstance(user.password, str) else user.password
    ):
        return {
            "message": "Current password is incorrect"
        }, 401

    # Hash new password
    hashed_password = bcrypt.hashpw(
        new_password.encode(),
        bcrypt.gensalt()
    )

    # Save new password
    user.password = hashed_password.decode()

    db.session.commit()

    return {
        "message": "Password changed successfully"
    }, 200