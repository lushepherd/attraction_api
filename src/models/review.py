from datetime import datetime

from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length

from init import db

class Review(db.Model):
    """
    A model representing a review of an attraction by a user.

    Attributes:
        id: Primary key, unique ID of the review.
        user_id: Foreign key to the user who wrote the review.
        attraction_id: Foreign key to the attraction being reviewed.
        rating: Rating given by the user (from 0 to 10).
        comment: Optional text comment provided by the user.
        created_at: Timestamp when the review was created.
    """
    __tablename__ = "reviews"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='reviews')  
    attraction = db.relationship('Attraction', back_populates='reviews')
    
class ReviewSchema(Schema):
    """
    Schema for serialising and deserialising review model objects.

    Includes validation for ratings (must be between 1-10), character limit for comments,
    date layout.
    """
    user = fields.Nested('UserSchema', only=('name',), dump_only=True)
    attraction = fields.Nested('AttractionSchema', only=('name',))
    rating = fields.Int(required=True, validate=lambda n: 0 <= n <= 10)
    comment = fields.String(validate=Length(max=100, error="Exceeds 100 character limit."))
    created_at = fields.DateTime('%d-%m-%Y')

    # Validates that provided rating is within the allowed range (0 to 10)
    @validates('rating')
    def validate_rating(self, value):
        if not (0 <= value <= 10):
            raise ValidationError('Rating must be between 0 and 10.')    
    
    # Fields that will be serialised and their order    
    class Meta:
        ordered = True
        fields = ('id', 'attraction', 'rating', 'comment', 'created_at', 'user')   

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)