from flask import Flask

from app.config import Config
from app.extensions import db, migrate, jwt ,mail
from app.auth.routes import auth_bp
from app.payments.routes import payment_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    # Register Authentication Blueprint
    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
    payment_bp,
    url_prefix="/api/payment"
)
    from app.models import User
    from app.models.subscription import Subscription
    print("\n========== REGISTERED ROUTES ==========")
    print(app.url_map)
    print("=======================================\n")

    return app