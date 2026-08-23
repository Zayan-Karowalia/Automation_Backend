import stripe

from datetime import datetime

from flask import current_app

from app.extensions import db
from app.models.subscription import Subscription


def create_checkout_session(user, price_id):

    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    session = stripe.checkout.Session.create(

        mode="subscription",

        line_items=[
            {
                "price": price_id,
                "quantity": 1
            }
        ],

        customer_email=user.email,

        metadata={
            "user_id": str(user.id)
        },

        success_url=current_app.config["STRIPE_SUCCESS_URL"],
        cancel_url=current_app.config["STRIPE_CANCEL_URL"]
    )

    print(
        "Stripe Checkout Session created:",
        session.id
    )

    return {
        "checkout_url": session.url
    }, 200


def handle_checkout_completed(session):

    print(
        "Processing checkout.session.completed..."
    )

    # --------------------------------------------------
    # 1. Convert Checkout Session to normal dictionary
    # --------------------------------------------------

    if hasattr(session, "to_dict"):

        session = session.to_dict()

    # --------------------------------------------------
    # 2. Get metadata
    # --------------------------------------------------

    metadata = session.get("metadata") or {}

    user_id = metadata.get("user_id")

    if not user_id:

        print(
            "ERROR: Stripe Checkout Session has no user_id"
        )

        return

    print(
        "Application User ID:",
        user_id
    )

    # --------------------------------------------------
    # 3. Get Stripe subscription ID
    # --------------------------------------------------

    stripe_subscription_id = session.get(
        "subscription"
    )

    if not stripe_subscription_id:

        print(
            "ERROR: No Stripe subscription ID found"
        )

        return

    print(
        "Stripe Subscription ID:",
        stripe_subscription_id
    )

    # --------------------------------------------------
    # 4. Get Stripe customer ID
    # --------------------------------------------------

    stripe_customer_id = session.get(
        "customer"
    )

    print(
        "Stripe Customer ID:",
        stripe_customer_id
    )

    # --------------------------------------------------
    # 5. Configure Stripe
    # --------------------------------------------------

    stripe.api_key = current_app.config[
        "STRIPE_SECRET_KEY"
    ]

    # --------------------------------------------------
    # 6. Retrieve subscription from Stripe
    # --------------------------------------------------

    stripe_subscription = stripe.Subscription.retrieve(
        stripe_subscription_id
    )

    print(
        "Stripe subscription retrieved successfully"
    )

    # IMPORTANT:
    # Stripe returns a StripeObject.
    # Convert it into a normal dictionary.

    subscription_data = (
        stripe_subscription.to_dict()
    )

    # --------------------------------------------------
    # 7. Get subscription information
    # --------------------------------------------------

    status = subscription_data.get(
        "status"
    )

    cancel_at_period_end = subscription_data.get(
        "cancel_at_period_end",
        False
    )

    current_period_start = subscription_data.get(
        "current_period_start"
    )

    current_period_end = subscription_data.get(
        "current_period_end"
    )

    # --------------------------------------------------
    # 8. Get Price ID
    # --------------------------------------------------

    items = subscription_data.get(
        "items",
        {}
    )

    items_data = items.get(
        "data",
        []
    )

    if not items_data:

        print(
            "ERROR: Stripe subscription has no items"
        )

        return

    first_item = items_data[0]

    price = first_item.get(
        "price",
        {}
    )

    stripe_price_id = price.get(
        "id"
    )

    if not stripe_price_id:

        print(
            "ERROR: Could not find Stripe price ID"
        )

        return

    # --------------------------------------------------
    # 9. Convert timestamps
    # --------------------------------------------------

    period_start = None

    if current_period_start:

        period_start = datetime.fromtimestamp(
            current_period_start
        )

    period_end = None

    if current_period_end:

        period_end = datetime.fromtimestamp(
            current_period_end
        )

    # --------------------------------------------------
    # 10. Check if subscription already exists
    # --------------------------------------------------

    existing_subscription = (
        Subscription.query.filter_by(
            stripe_subscription_id=(
                stripe_subscription_id
            )
        ).first()
    )

    # --------------------------------------------------
    # 11. UPDATE existing subscription
    # --------------------------------------------------

    if existing_subscription:

        print(
            "Existing subscription found."
        )

        existing_subscription.user_id = int(
            user_id
        )

        existing_subscription.stripe_customer_id = (
            stripe_customer_id
        )

        existing_subscription.stripe_price_id = (
            stripe_price_id
        )

        existing_subscription.status = (
            status
        )

        existing_subscription.current_period_start = (
            period_start
        )

        existing_subscription.current_period_end = (
            period_end
        )

        existing_subscription.cancel_at_period_end = (
            cancel_at_period_end
        )

    # --------------------------------------------------
    # 12. CREATE new subscription
    # --------------------------------------------------

    else:

        print(
            "Creating new subscription..."
        )

        new_subscription = Subscription(

            user_id=int(
                user_id
            ),

            stripe_customer_id=(
                stripe_customer_id
            ),

            stripe_subscription_id=(
                stripe_subscription_id
            ),

            stripe_price_id=(
                stripe_price_id
            ),

            status=(
                status
            ),

            current_period_start=(
                period_start
            ),

            current_period_end=(
                period_end
            ),

            cancel_at_period_end=(
                cancel_at_period_end
            )
        )

        db.session.add(
            new_subscription
        )

    # --------------------------------------------------
    # 13. COMMIT TO DATABASE
    # --------------------------------------------------

    try:

        db.session.commit()

        print(
            "===================================="
        )

        print(
            "SUBSCRIPTION SAVED SUCCESSFULLY"
        )

        print(
            "User ID:",
            user_id
        )

        print(
            "Stripe Subscription:",
            stripe_subscription_id
        )

        print(
            "Stripe Customer:",
            stripe_customer_id
        )

        print(
            "Stripe Price:",
            stripe_price_id
        )

        print(
            "Status:",
            status
        )

        print(
            "===================================="
        )

    except Exception as e:

        db.session.rollback()

        print(
            "===================================="
        )

        print(
            "DATABASE ERROR"
        )

        print(
            str(e)
        )

        print(
            "===================================="
        )

        raise