import bcrypt

from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer

from app.extensions import db,mail
from flask import current_app
from flask_mail import Message
from bcrypt import hashpw, gensalt
from app.models.user import User
from app.auth.token import generate_reset_token


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(
        current_app.config["JWT_SECRET_KEY"]
    )

    return serializer.dumps(email, salt="password-reset")

def verify_reset_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(
        current_app.config["JWT_SECRET_KEY"]
    )

    try:
        email = serializer.loads(
            token,
            salt="password-reset",
            max_age=max_age
        )

        return email

    except Exception:
        return None

def reset_password(data):

    token = data.get("token")
    new_password = data.get("password")

    if not token:
        return {
            "message": "Reset token is required."
        }, 400

    if not new_password:
        return {
            "message": "New password is required."
        }, 400

    if len(new_password) < 8:
        return {
            "message": "Password must be at least 8 characters."
        }, 400

    email = verify_reset_token(token)

    if not email:
        return {
            "message": "Invalid or expired reset link."
        }, 400

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:
        return {
            "message": "User not found."
        }, 404

    hashed_password = hashpw(
        new_password.encode("utf-8"),
        gensalt()
    ).decode("utf-8")

    user.password = hashed_password

    db.session.commit()

    return {
        "message": "Password has been reset successfully."
    }, 200

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

    if not user:
        return {
            "message": "Email not found"
        }, 404

    token = generate_reset_token(user.email)

    reset_link = (
        f"http://localhost:3000/reset-password/{token}"
    )

    msg = Message(
        subject="Reset Your Password",
        recipients=[user.email],
        body=f"""
Hello {user.name},

We received a request to reset your password.

Click the link below to reset your password:

{reset_link}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email.

Regards,
AutomationProject
"""
    )

    mail.send(msg)

    return {
        "message": "Password reset link sent."
    }, 200


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