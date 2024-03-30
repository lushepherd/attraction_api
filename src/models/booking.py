from datetime import datetime

from marshmallow import fields
from marshmallow.validate import OneOf

from init import db, ma

class booking_status:
    REQUESTED = 'Requested'
    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'
    
class Booking(db.Model):
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
    
    def calculate_total_cost(self):
       self.total_cost = self.number_of_guests * self.attraction.ticket_price

class BookingSchema(ma.Schema): 
    status = fields.String(validate=OneOf([booking_status.REQUESTED, booking_status.CONFIRMED, booking_status.CANCELLED]))
    user = fields.Nested('UserSchema', only=['name', 'email', 'phone'])
    attraction = fields.Nested('AttractionSchema', only=('name',))
    booking_date = fields.DateTime('%d/%m/%Y')
    created_at = fields.DateTime('%d/%m/%Y')

    class Meta:
        
        fields = ('id', 'attraction', 'booking_date', 'number_of_guests', 'total_cost', 'status', 'created_at', 'user')

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
    