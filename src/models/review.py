from datetime import datetime

from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length

from init import db

class Review(db.Model):
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
    user = fields.Nested('UserSchema', only=('name',), dump_only=True)
    attraction = fields.Nested('AttractionSchema', only=('name',))
    rating = fields.Int(required=True, validate=lambda n: 0 <= n <= 10)
    comment = fields.String(validate=Length(max=100, error="Exceeds 100 character limit."))
    created_at = fields.DateTime('%d/%m/%Y')

    @validates('rating')
    def validate_rating(self, value):
        if not (0 <= value <= 10):
            raise ValidationError('Rating must be between 0 and 10.')    
        
    class Meta:
        ordered = True
        fields = ('id', 'attraction', 'rating', 'comment', 'created_at', 'user')   

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)