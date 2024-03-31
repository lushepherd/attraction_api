from datetime import datetime, timedelta

from init import db
from models.user import User
from models.booking import Booking

from models.user import User
from models.booking import Booking
from init import db

def is_rate_limited(user_id):
    user = User.query.get(user_id)
    # Check if user is already locked
    if user.is_locked:
        return True

    # Check bookings made in the past 24 hours and are in "Requested" status
    threshold_time = datetime.utcnow() - timedelta(days=1)
    bookings_count = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.status == 'Requested',  # Only count bookings that are in "Requested" status
        Booking.created_at >= threshold_time
    ).count()

    # Lock the user if they have made 5 or more bookings in "Requested" status
    if bookings_count >= 5:
        user.is_locked = True
        db.session.commit()
        return True

    return False

def exceeded_booking_cost_limit(user_id, cost_limit=2500):
    """Check if the total cost of bookings made by a user in the last 24 hours exceeds the cost limit."""
    threshold_time = datetime.utcnow() - timedelta(days=1)
    total_cost = db.session.query(db.func.sum(Booking.total_cost))\
                .filter(Booking.user_id == user_id, Booking.created_at >= threshold_time)\
                .scalar() or 0
    return total_cost >= cost_limit