from sqlalchemy.orm import column_property
from sqlalchemy import select, func
from marshmallow import fields
from marshmallow.validate import Regexp, Length

from init import db, ma

from models.review import Review

class Attraction(db.Model):
    """
    Represents an attraction available for booking.

    Attributes:
        id: Primary key and unique identifier for the attraction.
        name: Name of the attraction, must be unique.
        ticket_price: Price per ticket for the attraction.
        description: Description of the attraction.
        location: Location of the attraction.
        contact_phone: Contact phone number for the attraction (must be 10 characters representative of an Australian mobile or landline).
        contact_email: Contact email address for the attraction (must be in correct email format).
        opening_hours: Opening hours of the attraction, in 'HH:MM - HH:MM' 24hr format.
        available_slots: Number of available slots for booking the attraction.
    """
    __tablename__ = "attractions"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    ticket_price = db.Column(db.Float, nullable=False)
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
    """
    Schema for serialising and deserialising Attraction model objects.
    
    Includes validation for email, phone number, and opening hours format.
    """
    reviews = fields.List(fields.Nested('ReviewSchema', exclude=['attraction',]))
    average_rating = fields.Method("get_average_rating")
    description = fields.String(validate=Length(max=200, error="Maximum of 200 characters."))
    contact_email = fields.Email()
    contact_phone = fields.String(validate=Length(equal=10, error="Phone number must contain 10 characters."))
    opening_hours = fields.String(required=True, validate=Regexp(
        r'^((2[0-3]|[01]?[0-9]):([0-5]?[0-9]))\s*-\s*((2[0-3]|[01]?[0-9]):([0-5]?[0-9]))$',
        error="Opening hours must be in the format 'HH:MM - HH:MM' using 24-hour time."
    ))
    
    # Helper method to calculate the average rating of the attraction.
    def get_average_rating(self, obj):
        return round(obj.average_rating, 1)
    # Fields that will be serialised and their order 
    class Meta:
        fields = ('id', 'name', 'average_rating', 'ticket_price', 'location', 'description', 'contact_phone', 'contact_email', 'opening_hours', 'available_slots', 'reviews')

attraction_schema = AttractionSchema()
attractions_schema = AttractionSchema(many=True)