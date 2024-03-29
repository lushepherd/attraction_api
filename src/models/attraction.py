from sqlalchemy.orm import column_property
from sqlalchemy import select, func
from marshmallow import fields

from init import db, ma

from models.review import Review

class Attraction(db.Model):
    __tablename__ = "attractions"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    contact_phone = db.Column(db.String, nullable=False)
    contact_email = db.Column(db.String, nullable=False)
    opening_hours = db.Column(db.String, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)

    bookings = db.relationship('Booking', back_populates='attraction', cascade='all, delete')
    reviews = db.relationship('Review', back_populates='attraction', cascade='all, delete')

    average_rating = column_property(
        select(func.coalesce(func.avg(Review.rating), 0))
        .where(Review.attraction_id == id)
        .correlate_except(Review)
        .scalar_subquery()
    )
    
class AttractionSchema(ma.Schema):
    reviews = fields.List(fields.Nested('ReviewSchema', exclude=['attraction', 'id']))
    average_rating = fields.Method("get_average_rating")
    
    def get_average_rating(self, obj):
        return round(obj.average_rating, 1)
    class Meta:

        fields = ('id', 'name', 'average_rating', 'location', 'description', 'contact_phone', 'contact_email', 'opening_hours', 'available_slots', 'reviews')

attraction_schema = AttractionSchema()
attractions_schema = AttractionSchema(many=True)