import functools

from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow.exceptions import ValidationError

from init import db
from models.user import User
from models.booking import Booking, booking_schema, bookings_schema
from models.attraction import Attraction, attraction_schema, attractions_schema 

booking_bp = Blueprint('booking_bp', __name__, url_prefix='/booking')

def authorise_as_admin(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        stmt = db.select(User).filter_by(id=user_id)
        user = db.session.scalar(stmt)
        if user.is_admin:
            return fn(*args, **kwargs)
        else:
            return {"error": "Not authorised. Admin access required."}, 403
        
    return wrapper

@booking_bp.route('/new', methods=['POST']) # Create booking 
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    body_data = request.get_json()
    attraction_id = body_data.get('attraction_id')

    booking = Booking(
        user_id=user_id,
        attraction_id=attraction_id,
        booking_date=body_data.get('booking_date'), 
        number_of_guests=body_data.get('number_of_guests'),
        status='Requested' 
    )

    db.session.add(booking)
    db.session.commit()

    return booking_schema.dump(booking), 201

@booking_bp.route('/my_bookings', methods=['GET']) # Logged in user view bookings
@jwt_required()
def view_my_bookings():
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return bookings_schema.dump(bookings)

@booking_bp.route('/all', methods=['GET']) # Admin can view all bookings
@jwt_required()
@authorise_as_admin
def get_all_bookings():
    stmt = db.select(Booking).order_by(Booking.created_at.desc())
    bookings = db.session.scalars(stmt)
    return bookings_schema.dump(bookings)

@booking_bp.route('/<int:booking_id>', methods=['PUT']) # Logged in user update booking
def update_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking is None:
        abort(404)
    try:
        data = booking_schema.load(request.json)
    except ValidationError as err:
        return (err.messages), 400
    
    for key, value in data.items():
        setattr(booking, key, value)
    db.session.commit()

    return booking_schema.dump(booking)

@booking_bp.route('/<int:booking_id>', methods=['DELETE']) # Logged in user can delete booking
def delete_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking is None:
        abort(404)
    db.session.delete(booking)
    db.session.commit()
    return ({'message': 'Booking deleted successfully'}), 200