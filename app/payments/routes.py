from flask import Blueprint, request, current_app

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

import stripe

from app.models.user import User

from app.payments.service import (
    create_checkout_session,
    handle_checkout_completed
)


payment_bp = Blueprint(
    "payment",
    __name__
)


@payment_bp.route(
    "/create-checkout-session",
    methods=["POST"]
)
@jwt_required()
def checkout():

    current_email = get_jwt_identity()

    data = request.get_json()

    price_id = data.get("price_id")

    if not price_id:

        return {
            "message": "price_id is required"
        }, 400

    user = User.query.filter_by(
        email=current_email
    ).first()

    if not user:

        return {
            "message": "User not found"
        }, 404

    return create_checkout_session(
        user,
        price_id
    )


@payment_bp.route(
    "/webhook",
    methods=["POST"]
)
def webhook():

    payload = request.data

    sig_header = request.headers.get(
        "Stripe-Signature"
    )

    endpoint_secret = current_app.config[
        "STRIPE_WEBHOOK_SECRET"
    ]

    try:

        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )

    except ValueError:

        return {
            "message": "Invalid payload"
        }, 400

    except stripe.error.SignatureVerificationError:

        return {
            "message": "Invalid signature"
        }, 400

    event_type = event["type"]

    print(
        "Stripe event received:",
        event_type
    )

    try:

        if event_type == "checkout.session.completed":

            print(
                "Processing checkout.session.completed..."
            )

            session = event["data"]["object"]

            handle_checkout_completed(
                session
            )

        return {
            "message": "Webhook received"
        }, 200

    except Exception as e:

        print(
            "Webhook processing error:",
            str(e)
        )

        return {
            "message": "Webhook processing failed"
        }, 500