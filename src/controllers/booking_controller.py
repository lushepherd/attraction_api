from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow.exceptions import ValidationError

from init import db
from models.user import User
from models.booking import Booking, booking_schema, bookings_schema
from models.attraction import Attraction
from controllers.auth_utils import authorise_as_admin

booking_bp = Blueprint('booking_bp', __name__, url_prefix='/booking')

@booking_bp.route('/new', methods=['POST'])  # Create booking
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    body_data = request.get_json()
    attraction_id = body_data.get('id')
    number_of_guests = body_data.get('number_of_guests')

    attraction = Attraction.query.get(attraction_id)
    if not attraction:
        return ({"error": "Attraction not found"}), 404

    if attraction.available_slots < number_of_guests:
        return ({"error": "Not enough available slots for this booking."}), 400

    booking = Booking(
        user_id=user_id,
        attraction_id=attraction_id,
        booking_date=body_data.get('booking_date'), 
        number_of_guests=number_of_guests,
        status='Requested' 
    )

    attraction.available_slots -= number_of_guests

    try:
        db.session.add(booking)
        db.session.commit()
        return (booking_schema.dump(booking)), 201
    except Exception as e:
        db.session.rollback()
        return ({"error": "Failed to create booking. Please try again."}), 500

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

@booking_bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
@authorise_as_admin
def update_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking is None:
        return ({"error": "Booking not found"}), 404

    data = request.json
    new_guest_count = data.get('number_of_guests', booking.number_of_guests)
    guest_difference = new_guest_count - booking.number_of_guests

    attraction = Attraction.query.get(booking.attraction_id)
    if attraction.available_slots - guest_difference < 0:
        return ({"error": "Not enough available slots for the updated number of guests."}), 400

    if 'booking_date' in data:
        booking.booking_date = data['booking_date']
    if 'number_of_guests' in data:
        booking.number_of_guests = new_guest_count
        attraction.available_slots -= guest_difference  # Adjust available slots

    if 'status' in data:
        booking.status = data['status']

    try:
        db.session.commit()
        return booking_schema.dump(booking), 200
    except Exception as e:
        db.session.rollback()
        return ({"error": "Failed to update booking. Please try again."}), 500

@booking_bp.route('/<int:booking_id>', methods=['DELETE']) # Delete booking as admin
@jwt_required()
@authorise_as_admin
def delete_booking(booking_id):
    booking = Booking.query.get(booking_id)
    
    if booking is None:
        return ({'error': 'Booking not found'}), 404
    
    attraction = Attraction.query.get(booking.attraction_id)
    if attraction:
        attraction.available_slots += booking.number_of_guests

    db.session.delete(booking)
    db.session.commit()
    return ({'message': 'Booking deleted successfully'}), 200