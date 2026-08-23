from datetime import datetime

from app.extensions import db


class Subscription(db.Model):

    __tablename__ = "subscriptions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    stripe_customer_id = db.Column(
        db.String(255),
        nullable=True
    )

    stripe_subscription_id = db.Column(
        db.String(255),
        unique=True,
        nullable=True
    )

    stripe_price_id = db.Column(
        db.String(255),
        nullable=True
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="incomplete"
    )

    current_period_start = db.Column(
        db.DateTime,
        nullable=True
    )

    current_period_end = db.Column(
        db.DateTime,
        nullable=True
    )

    cancel_at_period_end = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )