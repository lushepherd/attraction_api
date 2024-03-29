from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db

from models.review import Review, review_schema, reviews_schema
from models.booking import Booking

review_bp = Blueprint('review_bp', __name__, url_prefix='/review')

def user_has_confirmed_booking(user_id, attraction_id):
    current_date = datetime.utcnow().date()

    booking = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.attraction_id == attraction_id,
        Booking.status == 'Confirmed',
        Booking.booking_date < current_date
    ).first()
    
    return booking is not None

@review_bp.route('/create/<int:attraction_id>', methods=['POST']) # Create review
@jwt_required()
def leave_review(attraction_id):
    user_id = get_jwt_identity()
    if not user_has_confirmed_booking(user_id, attraction_id):
        return ({"error": "No confirmed booking for this attraction"}), 403

    body_data = request.get_json()
    rating = body_data.get('rating')
    comment = body_data.get('comment')

    review = Review(
        user_id=user_id,
        attraction_id=attraction_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()

    return ({"message": "Review successfully added"}), 201

@review_bp.route('/<int:attraction_id>', methods=['GET']) # See reviews for one attraction
def get_reviews(attraction_id):
    reviews = Review.query.filter_by(attraction_id=attraction_id).all()
    reviews_data = [{'rating': review.rating, 'comment': review.comment, 'created_at': review.created_at} for review in reviews]
    return reviews_schema.dump(reviews), 200

@review_bp.route('/my_reviews', methods=['GET']) # See reviews as user
@jwt_required()
def get_my_reviews():
    user_id = get_jwt_identity()
    reviews = Review.query.filter_by(user_id=user_id).all()
    return reviews_schema.dump(reviews), 200

@review_bp.route('/update/<int:review_id>', methods=['PUT']) # Update review
@jwt_required()
def update_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.filter_by(id=review_id, user_id=user_id).first()
    
    if review is None:
        return {"error": "Review not found or access denied"}, 404
    
    body_data = request.get_json()
    review.rating = body_data.get('rating', review.rating)
    review.comment = body_data.get('comment', review.comment)
    
    db.session.commit()
    
    return review_schema.dump(review), 200

@review_bp.route('/delete/<int:review_id>', methods=['DELETE']) # Delete review as user
@jwt_required()
def delete_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.filter_by(id=review_id, user_id=user_id).first()
    
    if review is None:
        return {"error": "Review not found or access denied"}, 404
    
    db.session.delete(review)
    db.session.commit()
    
    return {"message": "Review deleted successfully"}, 200