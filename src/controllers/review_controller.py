from datetime import datetime

from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from init import db
from models.review import Review, review_schema, reviews_schema
from models.booking import Booking

from utils.auth_utils import load_current_user

review_bp = Blueprint('review_bp', __name__, url_prefix='/review')

def user_has_confirmed_booking(user_id, attraction_id):
    """
    Checks if a user has a confirmed booking for an attraction that has already occurred.

    Returns (boolean) True if there is a confirmed booking for the attraction that has occurred, False otherwise.
    """
    current_date = datetime.utcnow().date()

    booking = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.attraction_id == attraction_id,
        Booking.status == 'Confirmed',  # Use == instead of calling status as a function
        Booking.booking_date < current_date
    ).first()

    return booking is not None

@review_bp.route('/create/<int:attraction_id>', methods=['POST']) # Create review
@jwt_required()
@load_current_user
def leave_review(attraction_id):
    """
    The endpoint checks if the currently logged-in user has a confirmed booking for the given attraction
    that has already occurred. If so, it accepts a rating and comment as part of the review.
    
    If users have already left a review for an attraction, they won't be able to leave another.

    JSON Payload example:
    
    {
    "rating": 7, (float)
    "comment": "Ok!" (100 character limit)
    }
    """
    user_id = g.current_user.id

    # Check if the user already left a review for this attraction.
    existing_review = Review.query.filter_by(user_id=user_id, attraction_id=attraction_id).first()
    if existing_review:
        return {"error": "You have already left a review for this attraction"}, 403

    # Check if the user has a past confirmed booking
    if not user_has_confirmed_booking(user_id, attraction_id):
        return {"error": "No confirmed booking for this attraction"}, 403

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

    return {"message": "Review successfully added"}, 201

@review_bp.route('/my_reviews', methods=['GET']) # See reviews as user
@jwt_required()
@load_current_user
def get_my_reviews():
    """
    Retrieves all reviews made by the currently logged-in user.

    Requires JWT authentication to identify the requesting user. Fetches all reviews
    associated with the user's ID and returns them.
    """
    user_id = g.current_user.id
    reviews = Review.query.filter_by(user_id=user_id).all()
    return reviews_schema.dump(reviews), 200

@review_bp.route('/update/<int:review_id>', methods=['PUT']) # Update review
@jwt_required()
@load_current_user
def update_review(review_id):
    """
    Updates a specific review made by the currently logged-in user.

    Allows users to update the rating and comment of their own reviews.
    It checks if the review exists and if the logged-in user is the author of the review.

    JSON Payload:
        - rating (optional): A new rating for the review.
        - comment (optional): A new comment for the review.

    """
    user_id = g.current_user.id
    review = Review.query.filter_by(id=review_id, user_id=user_id).first()
    
    if review is None:
        return {"error": "Review not found or access denied"}, 404
    
    body_data = request.get_json()
    
    try:
        validated_data = review_schema.load(body_data, partial=True)
    except ValidationError as err:
        return err.messages, 400
    
    review.rating = validated_data.get('rating', review.rating)
    review.comment = validated_data.get('comment', review.comment)
    
    db.session.commit()
    
    return review_schema.dump(review), 200

@review_bp.route('/delete/<int:review_id>', methods=['DELETE']) # Delete review as user or admin
@jwt_required()
@load_current_user
def delete_review(review_id):
    """
    Endpoint for a user to delete their review.
    
    Only the user who created the review can delete it. The endpoint checks if the review
    exists and if the currently logged-in user is the owner of the review. If these conditions
    are met, the review is deleted.

    """
    user = g.current_user

    # Admin users can delete any review
    if user.is_admin:
        review = Review.query.get(review_id)
        if review is None:
            return {"error": "Review not found"}, 404
    else:
        # Regular users can only delete their own reviews
        review = Review.query.filter_by(id=review_id, user_id=user.id).first()
        if review is None:
            return {"error": "Review not found or access denied"}, 404

    # Proceed with deletion
    db.session.delete(review)
    db.session.commit()

    return {"message": "Review deleted successfully"}, 200