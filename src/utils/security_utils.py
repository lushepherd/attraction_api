from datetime import datetime, timedelta

from models.user import User
from models.booking import Booking
from init import db

def is_rate_limited(user_id):
    """
    Determines whether a user has exceeded the rate limit for booking requests within the last 24 hours.

    A user is considered rate-limited if they have 5 or more bookings in the "Requested" status within
    the past 24 hours. When rate-limited, the user's account is locked to prevent further booking requests.

    This is to help with fraud prevention - if an account is locked, a user can contact admin who can then
    verify them  and unlock their account, then change the status of their bookings to either "Confirmed" 
    or "Cancelled". The user is then able to proceed with more bookings.
    """
    user = User.query.get(user_id)
    # Check if user is already locked
    if user.is_locked:
        return True

    # Check bookings made in the past 24 hours and are in "Requested" status
    threshold_time = datetime.utcnow() - timedelta(days=1)
    bookings_count = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.status == 'Requested',  # Only counts bookings that are in "Requested" status
        Booking.created_at >= threshold_time
    ).count()

    # Lock the user if they have made 5 or more bookings in "Requested" status
    if bookings_count >= 5:
        user.is_locked = True
        db.session.commit()
        return True

    return False

def exceeded_booking_cost_limit(user_id, cost_limit=2500):
    """Check if the total cost of bookings made by a user in the last 24 hours exceeds the cost limit of $2500."""
    threshold_time = datetime.utcnow() - timedelta(days=1)
    total_cost = db.session.query(db.func.sum(Booking.total_cost))\
                .filter(Booking.user_id == user_id, Booking.created_at >= threshold_time)\
                .scalar() or 0
    print(f"Total cost calculated for user {user_id} in the last 24 hours: {total_cost}")
    return total_cost >= cost_limit