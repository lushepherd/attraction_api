from datetime import datetime, timedelta

from flask import Blueprint, request, abort, g, jsonify
from flask_jwt_extended import jwt_required

from init import db
from models.user import User
from models.booking import Booking, booking_schema, bookings_schema, booking_status
from models.attraction import Attraction

from utils.auth_utils import authorise_as_admin, load_current_user
from utils.security_utils import is_rate_limited, exceeded_booking_cost_limit

booking_bp = Blueprint('booking_bp', __name__, url_prefix='/booking')

def insufficient_slots_error():
    """
    Helper function to abort the request with a custom error message
    when there are not enough available slots for a booking.
    """
    return {'error': f'"Not enough available slots for this booking.'}, 400

def check_attraction_slots(attraction_id, required_slots):
    """
    Checks if the attraction has enough available slots for the booking.
    Checks attraction ID and slots required for the booking.
    
    """
    attraction = Attraction.query.get(attraction_id)
    if not attraction or attraction.available_slots < required_slots:
        return False, attraction
    return True, attraction

def create_booking_logic(user_id, data, bypass_limits_for_admin=False):
    """
    Handles the common logic for creating a booking for a user. Includes validating the booking date,
    checking availability of slots for the attraction, calculating the total cost, and applying security checks.

    Checks current user and if they are admin in case security bypasses are required.

    Creating a booking requires a JSON payload with the keys 'id'(attraction id), 'booking_date', 
    'number_of_guests'.
    
    Returns:
        Booking: The created Booking object on successful creation.

    Example JSON:
    {
        "id": 2,
        "booking_date": "2024-04-10",
        "number_of_guests": 1
    }
    
    Error handling - Contains custom error handling for specific scenarios.
    Helps to identify errors related to security checks, attractions not having
    enough availability.
    """
    user = User.query.get(user_id)
    if not user:
        abort(404)

    # Checks if current user is admin - if admin, they can bypass security limit checks. 
    if not (user.is_admin and bypass_limits_for_admin):
        if is_rate_limited(user_id) or exceeded_booking_cost_limit(user_id):
            abort(jsonify(message="Account locked for security reasons. Please contact admin."), 429)
        
    body_data = request.get_json()
    attraction_id = body_data.get('id')  
    number_of_guests = body_data.get('number_of_guests')
    booking_date = body_data.get('booking_date') 

    if number_of_guests > 20:
        abort(jsonify(message="For bookings greater than 20, please contact the attraction directly.")), 400

    # Parse and validate the booking date format
    # Checks if booking is a valid date between today and 6 months from now.
    try:
        booking_date = datetime.strptime(booking_date, '%d-%m-%Y')
    except ValueError:
        abort(jsonify(message="Invalid booking date format. Enter as DD-MM-YYYY.")), 400
    today = datetime.utcnow().date()
    max_booking_date = today + timedelta(days=180)
    if booking_date.date() < today or booking_date.date() > max_booking_date:
        abort(jsonify(message="Booking date out of allowed range."), 400)

    # Validates the attraction, checks availability for booking request
    attraction = Attraction.query.get(attraction_id)
    if not attraction:
        abort(404)
    if not check_attraction_slots(attraction.id, number_of_guests):
        abort(jsonify(message="Not enough available slots for this booking.")), 400

    # Creates booking object and calculates booking cost
    booking = Booking(
        user_id=user_id,
        attraction_id=attraction.id,
        booking_date=booking_date,  
        number_of_guests=number_of_guests,
        status='Requested'
    )
    booking.attraction = attraction 
    booking.calculate_total_cost()

    # If a booking is $1000 or more, checks if user is admin
    if booking.total_cost >= 1000 and not bypass_limits_for_admin:
        abort(jsonify(message="Bookings over $1000 require admin permission."), 403)

    available, _ = check_attraction_slots(attraction_id, number_of_guests)
    if not available:
        abort(jsonify(message="Not enough available slots for this booking."), 400)
    else:
        db.session.add(booking)
        db.session.commit()

    return booking

@booking_bp.route('/new', methods=['POST']) # User create a new booking
@jwt_required()
@load_current_user
def create_booking():
    """
    Endpoint for creating a new booking. Checks the user ID from the current user,
    retrieves the booking details from the request JSON, and calls the `create_booking_logic` function.
    This endpoint applies for both regular users and admins, with admins
    having the ability to bypass security restrictions.

    Returns:
        JSON: booking object along with a 201 status code for a successful booking creation.
    """
    data = request.get_json()
    booking = create_booking_logic(g.current_user.id, data)
    if not booking:
        abort(400)
    
    return booking_schema.dump(booking), 201

@booking_bp.route("/admin/<int:user_id>", methods=["POST"]) # Admin create a booking for user by their user ID
@jwt_required()
@authorise_as_admin
def admin_create_booking(user_id):
    """
    Allows an admin to create a booking for a specific user.

    Follows the same logic as standard "create booking" endpoint, however admin can 
    create a booking for a user that exceeds the $1000 price limit, the 24hr $2500
    spend limit or if they have 5 bookings in requested from the last 24hrs.
    """
    data = request.get_json()
    required_fields = ["id", "booking_date", "number_of_guests"]
    if not all(field in data for field in required_fields):
        abort(400)

    # Call create_booking_logic with bypass_limits_for_admin set to True
    booking = create_booking_logic(user_id, data, bypass_limits_for_admin=True)
    if not booking:
        abort(400)

    return booking_schema.dump(booking), 201

@booking_bp.route('/my_bookings', methods=['GET']) # Logged in user view bookings
@jwt_required()
@load_current_user
def view_my_bookings():
    """
    Retrieves all bookings associated with the currently logged-in user.

    User to be authenticated via JWT and token provided in authorisation header of the request.
    It uses the @load_current_user decorator to load the current user's details.
    """
    bookings = Booking.query.filter_by(user_id=g.current_user.id).all()
    return bookings_schema.dump(bookings)

@booking_bp.route('/<int:booking_id>', methods=['PUT']) # Admin update any user booking
@jwt_required()
@authorise_as_admin
def update_booking(booking_id):
    """
    Updates the details of an existing booking. Only accessible by admin.

    Requires:
        - JWT authentication as an admin user.
        - A JSON payload in the request body with one or more of the following keys:
            - 'booking_date' (str): New date for the booking in DD-MM-YYYY format.
            - 'number_of_guests' (int): Updated number of guests for the booking.
            - 'status' (str): New status of the booking (Requested, Confirmed, Cancelled).

    """
    booking = Booking.query.get(booking_id)
    if not booking:
        abort(404)

    data = request.get_json()

    # If booking date is entered, checks for correct format. Returns an error if required
    if 'booking_date' in data:
        try:
            booking.booking_date = datetime.strptime(data['booking_date'], '%d-%m-%Y')
        except ValueError:
            abort(jsonify(message="Invalid booking date format. Enter as DD-MM-YYYY.")), 400

    # If number of guests is updated, checks for availability and returns an error if required
    if 'number_of_guests' in data:
        new_guest_count = data['number_of_guests']
        guest_difference = new_guest_count - booking.number_of_guests
        attraction = Attraction.query.get(booking.attraction_id)
        
        if attraction.available_slots - guest_difference < 0:
            abort(jsonify(message="Not enough availability for the updated number of guests.")), 400

        # Updates the number of guests in the booking and attraction based on changes made
        booking.number_of_guests = new_guest_count
        attraction.available_slots -= guest_difference  

    # If status is updated, checks it is a valid status and returns an error if required.
    if 'status' in data and data['status'] in [booking_status.REQUESTED, booking_status.CONFIRMED, booking_status.CANCELLED]:
        booking.status = data['status']
    else:
        return jsonify({
            "error": "Invalid status value",
            "message": "Status can only be 'Requested', 'Confirmed', or 'Cancelled'.",
        }), 422 

    db.session.commit()
    return booking_schema.dump(booking), 200

@booking_bp.route('/delete/<int:booking_id>', methods=['DELETE']) # Delete booking as admin
@jwt_required()
@authorise_as_admin
def delete_booking(booking_id):
    """
    Deletes a booking by its ID. This action is restricted to admin users only.

    Upon deletion, it returns a confirmation message. 
    Additionally, the available slots for the attraction related to the booking are added back.

    """
    booking = Booking.query.get(booking_id)
    
    if booking is None:
        abort(404)
    
    # Retrieve attraction associated with booking
    attraction = Attraction.query.get(booking.attraction_id)
    if attraction:
        attraction.available_slots += booking.number_of_guests

    db.session.delete(booking)
    db.session.commit()
    return ({'message': 'Booking deleted successfully'}), 200