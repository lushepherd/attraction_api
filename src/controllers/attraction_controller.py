from flask import Blueprint, request, abort, jsonify
from flask_jwt_extended import jwt_required

from init import db
from models.attraction import Attraction, attraction_schema, attractions_schema 
from utils.auth_utils import authorise_as_admin

attraction_bp = Blueprint('attraction_bp', __name__, url_prefix='/attractions')

@attraction_bp.route('/all', methods=['GET'])  # Show all attractions
def get_all_attractions():
    """
    Retrieves all attractions from the database, sorts them alphabetically by their names, and
    returns them to the client. It does not require authentication and is accessible by any user or guest.
    """
    stmt = db.select(Attraction).order_by(Attraction.name)
    attractions = db.session.scalars(stmt).all()
    return attractions_schema.dump(attractions), 200

@attraction_bp.route('/<int:attraction_id>', methods=['Get']) # View one attraction
def get_one_attraction(attraction_id): 
    """
    Retrieves one attractions from the database identified by it's ID.
    It does not require authentication and is accessible by any user or guest.
    """
    stmt = db.select(Attraction).filter_by(attraction_id=attraction_id) 
    attraction = db.session.scalar(stmt)
    if attraction:
        return attraction_schema.dump(attraction)
    else:
        return {"error": f"Attraction with id {attraction_id} not found"}, 404

@attraction_bp.route('/create', methods=['POST']) # Create attraction - admin only
@jwt_required()
@authorise_as_admin
def create_attraction():
    """
    Creates a new attraction in the database. Restricted to admin only.
    
    The endpoint expects a JSON payload with the attraction details.

    Expected JSON payload fields:
    - name: The name of the attraction (must be unique)
    - ticket_price: The price of a ticket for the attraction (float)
    - description: A brief description of the attraction. (200 character limit)
    - location: The location where the attraction is situated.
    - contact_phone: A contact phone number for inquiries.
    - contact_email: A contact email for inquiries.
    - opening_hours: The opening hours of the attraction in 'HH:MM - HH:MM' format.
    - available_slots: The number of slots available for booking (int)

    """
    body_data = attraction_schema.load(request.get_json())
    
    # Create a new Attraction with the validated data
    attraction = Attraction(
        name = body_data.get('name'),
        ticket_price = body_data.get('ticket_price'),
        description = body_data.get('description'),
        location = body_data.get('location'),
        contact_phone = body_data.get('contact_phone'),
        contact_email = body_data.get('contact_email'),
        opening_hours = body_data.get('opening_hours'),
        available_slots = body_data.get('available_slots')
    )

    db.session.add(attraction)
    db.session.commit()

    return attraction_schema.dump(attraction), 201

@attraction_bp.route('/update/<int:attraction_id>', methods=['PUT']) # Update attraction - admin only
@jwt_required()
@authorise_as_admin
def update_attraction(attraction_id):
    """
    Updates the details of an existing attraction. Restricted to admin only.

    Allows partial updates; only the fields provided in the request will be updated.

    Parameters:
    - attraction_id (int): Path parameter specifying the ID of the attraction to update.

    Request body should include any of the following fields (all optional):
    - name: The new name of the attraction (must be unique)
    - ticket_price: The new price of a ticket for the attraction (float)
    - description: A new brief description of the attraction. (200 character limit)
    - location: The new location where the attraction is situated.
    - contact_phone: A new contact phone number for inquiries.
    - contact_email: A new contact email for inquiries.
    - opening_hours: The new opening hours of the attraction in 'HH:MM - HH:MM' format.
    - available_slots: The updated number of slots available for booking (int).

    """
    body_data = attraction_schema.load(request.get_json(), partial=True)

    stmt = db.select(Attraction).filter_by(id=attraction_id)
    attraction = db.session.scalar(stmt)
    
    if attraction:
        # Update attraction fields with provided values, defaulting to current values if not provided
        attraction.name = body_data.get('name', attraction.name)
        attraction.description = body_data.get('description', attraction.description)
        attraction.ticket_price = body_data.get('ticket_price', attraction.ticket_price)
        attraction.location = body_data.get('location', attraction.location)
        attraction.contact_phone = body_data.get('contact_phone', attraction.contact_phone)
        attraction.contact_email = body_data.get('contact_email', attraction.contact_email)
        attraction.opening_hours = body_data.get('opening_hours', attraction.opening_hours)  
        attraction.available_slots = body_data.get('available_slots', attraction.available_slots)  
        
        db.session.commit()
        return attraction_schema.dump(attraction), 200
    else:
        return {'error': f'Attraction with id {attraction_id} not found'}, 404

@attraction_bp.route('/delete/<int:attraction_id>', methods=['DELETE']) # Delete attraction - admin only
@jwt_required()
@authorise_as_admin
def delete_attraction(attraction_id):
    """
    Deletes an attraction identified by its ID. Restricted to admin only.

    Attempts to find an attraction with the provided ID. If found, the attraction is deleted from
    the database. If no attraction with the provided ID exists, a 404 Not Found error is returned.
    """
    attraction = Attraction.query.get(attraction_id)
    if attraction is None:
        return {'message': f"The requested attraction does not exist"}, 404
    db.session.delete(attraction)
    db.session.commit()
    return {'message': f"Attraction '{attraction.name}' deleted successfully"}, 200