from datetime import datetime

from marshmallow import fields
from marshmallow.validate import OneOf, Range

from init import db, ma

# Constant booking statuses
class booking_status:
    REQUESTED = 'Requested'
    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'
    
class Booking(db.Model):
    """
    Represents a booking made by a user for an attraction.
    
    Attributes:
        id: The primary key and unique identifier for the booking.
        user_id: The ID of the user who made the booking. Foreign key to the User model.
        attraction_id: The ID of the attraction booked. Foreign key to the Attraction model.
        booking_date: The date and time for when the booking will be.
        number_of_guests: The number of guests included in the booking (int)
        total_cost: The total cost of the booking (float)
        status: The current status of the booking (Requested, Confirmed, Cancelled).
        created_at: Timestamp when the booking was created.
    """
    __tablename__ = "bookings"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    total_cost = db.Column(db.Float)
    status = db.Column(db.String, nullable=False, default=booking_status.REQUESTED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='bookings')
    attraction = db.relationship('Attraction', back_populates='bookings')
    
    # Calculates the total cost of booking based on the number of guests and the ticket price
    def calculate_total_cost(self):
       self.total_cost = self.number_of_guests * self.attraction.ticket_price

class BookingSchema(ma.Schema): 
    """
    Marshmallow schema for serialising and deserialising Booking model objects.
    
    Includes validation for booking status to ensure it's one of the defined statuses
    and validates the range for number of guests allowed in a booking.
    """
    status = fields.String(validate=OneOf([booking_status.REQUESTED, booking_status.CONFIRMED, booking_status.CANCELLED]))
    user = fields.Nested('UserSchema', only=['name', 'email', 'phone'])
    attraction = fields.Nested('AttractionSchema', only=('name',))
    booking_date = fields.DateTime('%d/%m/%Y')
    number_of_guests = fields.Integer(validate=Range(min=1, max=20, error="For bookings greater than 20, please contact the attraction directly."))
    created_at = fields.DateTime('%d/%m/%Y')

    # Fields that will be serialised and their order
    class Meta:
        fields = ('id', 'attraction', 'booking_date', 'number_of_guests', 'total_cost', 'status', 'created_at', 'user')

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
    