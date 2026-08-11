import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # MailHog / Flask-Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "1025"))

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_USE_TLS = os.getenv(
        "MAIL_USE_TLS", "False"
    ).lower() == "true"

    MAIL_USE_SSL = os.getenv(
        "MAIL_USE_SSL", "False"
    ).lower() == "true"

    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        "noreply@automationproject.local"
    )

    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000"
    )