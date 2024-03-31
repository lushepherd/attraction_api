from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required

from init import db
from models.attraction import Attraction, attraction_schema, attractions_schema 
from utils.auth_utils import authorise_as_admin

attraction_bp = Blueprint('attraction_bp', __name__, url_prefix='/attractions')

@attraction_bp.route('/all', methods=['GET'])  # Show all attractions
def get_all_attractions():
    stmt = db.select(Attraction).order_by(Attraction.name)
    attractions = db.session.scalars(stmt).all()
    return attractions_schema.dump(attractions), 200

@attraction_bp.route('/<int:attraction_id>', methods=['Get']) # View one attraction
def get_one_attraction(attraction_id): 
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
    body_data = attraction_schema.load(request.get_json())
    attraction = Attraction(
        name = body_data.get('name'),
        description = body_data.get('description'),
        location = body_data.get('location'),
        contact_phone = body_data.get('contact_phone'),
        contact_email = body_data.get('contact_email'),
        opening_hours = body_data.get('opening_hours'),
        available_slots = body_data.get('available_slots')
    )

    db.session.add(attraction)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return ({"error": "Could not create attraction."}), 500

    return attraction_schema.dump(attraction), 201

@attraction_bp.route('/delete/<int:attraction_id>', methods=['DELETE']) # Delete attraction - admin only
@jwt_required()
@authorise_as_admin
def delete_attraction(attraction_id):
    attraction = Attraction.query.get(attraction_id)
    if attraction is None:
        abort(404)
    db.session.delete(attraction)
    db.session.commit()
    return {'message': f"Attraction '{attraction.name}' deleted successfully"}, 200

@attraction_bp.route('/update/<int:attraction_id>', methods=['PUT']) # Update attraction - admin only
@jwt_required()
@authorise_as_admin
def update_attraction(attraction_id):
    body_data = attraction_schema.load(request.get_json(), partial=True)

    stmt = db.select(Attraction).filter_by(attraction_id=attraction_id)
    attraction = db.session.scalar(stmt)
    
    if attraction:

        attraction.name = body_data.get('name', attraction.name)
        attraction.description = body_data.get('description', attraction.description)
        attraction.location = body_data.get('location', attraction.location)
        attraction.contact_phone = body_data.get('contact_phone', attraction.contact_phone)
        attraction.contact_email = body_data.get('contact_email', attraction.contact_email)
        attraction.opening_hours = body_data.get('opening_hours', attraction.opening_hours)  
        attraction.available_slots = body_data.get('available_slots', attraction.available_slots)  
        
        db.session.commit()
        return attraction_schema.dump(attraction), 200
    else:
        return {'error': f'Attraction with id {attraction_id} not found'}, 404